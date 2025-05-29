import asyncio
import json
import logging
import os # os 模块仍然可能用于其他目的，但 save_to_file 会被移除
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import httpx


# 为了独立运行，我们用一个简单的Mock类
class MockFlightSearchRequest:
    def __init__(self, **kwargs):
        self.origin_iata = kwargs.get("origin_iata")
        self.destination_iata = kwargs.get("destination_iata")
        self.departure_date_from = kwargs.get("departure_date_from")
        self.departure_date_to = kwargs.get("departure_date_to")
        self.adults = kwargs.get("adults", 1)
        self.children = kwargs.get("children", 0)
        self.infants = kwargs.get("infants", 0)
        self.cabin_class = kwargs.get("cabin_class", "ECONOMY")
        self.preferred_currency = kwargs.get("preferred_currency", "cny")
        self.is_one_way = kwargs.get("is_one_way", True)
        self.return_date_from = kwargs.get("return_date_from")
        self.return_date_to = kwargs.get("return_date_to")
        self.adults_hold_bags = kwargs.get("adults_hold_bags", [0])
        self.adults_hand_bags = kwargs.get("adults_hand_bags", [1])

    def model_dump(self): # 模拟Pydantic的model_dump
        return self.__dict__

    def copy(self, update: Dict[str, Any]): # 模拟Pydantic的copy
        new_data = self.model_dump()
        new_data.update(update)
        return MockFlightSearchRequest(**new_data)


logger = logging.getLogger(__name__)
# 配置日志（如果尚未在其他地方配置）
logging.basicConfig(
    level=logging.INFO, # 可以根据需要调整为 DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
)

# save_to_file 函数不再需要，可以移除
# def save_to_file(data, filename, directory="logs"):
#     # ...
#     pass

class SimplifiedFlightHelpers:
    """简化航班搜索服务的辅助方法"""

    # _saved_requests_payloads也不再需要
    # _saved_requests_payloads = set()

    @staticmethod
    def _map_cabin_class(cabin_class: Optional[str]) -> str:
        cabin_mapping = {
            "ECONOMY": "ECONOMY",
            "PREMIUM_ECONOMY": "PREMIUM_ECONOMY",
            "BUSINESS": "BUSINESS",
            "BUSINESS_CLASS": "BUSINESS",
            "FIRST": "FIRST",
            "FIRST_CLASS": "FIRST"
        }
        safe_cabin_class = str(cabin_class).upper() if cabin_class else "ECONOMY"
        mapped_class = cabin_mapping.get(safe_cabin_class, "ECONOMY")
        return mapped_class

    @staticmethod
    def build_graphql_variables(request: Any, is_one_way: bool) -> Dict[str, Any]:
        dep_date_start_str = getattr(request, 'departure_date_from', None)
        dep_date_to_str = getattr(request, 'departure_date_to', None)
        origin_iata_str = getattr(request, 'origin_iata', None)
        destination_iata_str = getattr(request, 'destination_iata', None)
        adults_count = getattr(request, 'adults', 1)
        cabin_class_str = getattr(request, 'cabin_class', "ECONOMY")
        preferred_currency_str = getattr(request, 'preferred_currency', "cny")
        return_date_from_str = getattr(request, 'return_date_from', None)
        return_date_to_str = getattr(request, 'return_date_to', None)

        if not all([dep_date_start_str, origin_iata_str, destination_iata_str]):
            logger.error(f"构建GraphQL变量失败，缺少必要参数: dep_date_start={dep_date_start_str}, origin={origin_iata_str}, dest={destination_iata_str}")
            raise ValueError("Missing required request parameters for building GraphQL variables.")

        try:
            dep_date_start = datetime.strptime(dep_date_start_str, "%Y-%m-%d")
            dep_date_end = datetime.strptime(dep_date_to_str, "%Y-%m-%d") if dep_date_to_str else dep_date_start
        except ValueError as e:
            logger.error(f"日期格式错误: {e}. dep_from='{dep_date_start_str}', dep_to='{dep_date_to_str}'")
            raise

        search_params = {
            "itinerary": {
                "source": {"ids": [f"Station:airport:{origin_iata_str.upper()}"]},
                "destination": {"ids": [f"Station:airport:{destination_iata_str.upper()}"]},
                "outboundDepartureDate": {
                    "start": dep_date_start.strftime("%Y-%m-%dT00:00:00"),
                    "end": dep_date_end.strftime("%Y-%m-%dT23:59:59")
                }
            },
            "passengers": {
                "adults": adults_count,
                "children": getattr(request, 'children', 0),
                "infants": getattr(request, 'infants', 0),
                "adultsHoldBags": getattr(request, 'adults_hold_bags', [0]),
                "adultsHandBags": getattr(request, 'adults_hand_bags', [0]),
                "childrenHoldBags": [], "childrenHandBags": []
            },
            "cabinClass": {
                "cabinClass": SimplifiedFlightHelpers._map_cabin_class(cabin_class_str),
                "applyMixedClasses": True
            }
        }

        if not is_one_way and return_date_from_str:
            try:
                ret_date_start = datetime.strptime(return_date_from_str, "%Y-%m-%d")
                ret_date_end = datetime.strptime(return_date_to_str, "%Y-%m-%d") if return_date_to_str else ret_date_start
                search_params["itinerary"]["inboundDepartureDate"] = {
                    "start": ret_date_start.strftime("%Y-%m-%dT00:00:00"),
                    "end": ret_date_end.strftime("%Y-%m-%dT23:59:59")
                }
            except ValueError as e:
                logger.error(f"返程日期格式错误: {e}. ret_from='{return_date_from_str}', ret_to='{return_date_to_str}'")
                pass


        filter_params = {
            "allowChangeInboundDestination": True, "allowChangeInboundSource": True,
            "allowDifferentStationConnection": True, "enableSelfTransfer": True,
            "enableThrowAwayTicketing": True, "enableTrueHiddenCity": True,
            "maxStopsCount": 3, "transportTypes": ["FLIGHT"],
            "contentProviders": ["KIWI", "FRESH"],
            "flightsApiLimit": 30, "limit": 25
        }

        options_params = {
            "sortBy": "QUALITY", "mergePriceDiffRule": "INCREASED",
            "currency": preferred_currency_str.lower(),
            "locale": "cn", "market": "cn", "partner": "skypicker",
            "partnerMarket": "cn", "affilID": "skypicker", "storeSearch": False,
            "searchStrategy": "REDUCED",
            "abTestInput": {
                "priceElasticityGuarantee": "DISABLE", "baggageProtectionBundle": "ENABLE",
                "paretoProtectVanilla": "ENABLE", "kiwiBasicThirdIteration": "C",
                "offerStrategiesNonT1": "ENABLE", "kayakWithoutBags": "DISABLE",
                "carriersDeeplinkResultsEnable": True, "carriersDeeplinkOnSEMEnable": True
            }
        }
        return {"search": search_params, "filter": filter_params, "options": options_params}

    @staticmethod
    async def execute_graphql_search(
        variables: Dict[str, Any], headers: Dict[str, str], search_id: str,
        base_url: str = "https://api.skypicker.com/umbrella/v2/graphql", timeout: float = 45.0
    ) -> List[Dict[str, Any]]:
        query = """
        query SearchOneWayItinerariesQuery(
          $search: SearchOnewayInput, $filter: ItinerariesFilterInput, $options: ItinerariesOptionsInput
        ) {
          onewayItineraries(search: $search, filter: $filter, options: $options) {
            __typename
            ... on AppError { error: message }
            ... on Itineraries {
              server { requestId }
              metadata { itinerariesCount hasMorePending }
              itineraries {
                __typename
                ... on ItineraryOneWay {
                  ... on Itinerary {
                    id price { amount } duration pnrCount
                    bookingOptions { edges { node { token bookingUrl price { amount } } } }
                    travelHack { isTrueHiddenCity isVirtualInterlining isThrowawayTicket }
                  }
                  sector {
                    duration
                    sectorSegments {
                      segment {
                        source { localTime utcTime station { name code city { name } country { code name } } }
                        destination { localTime utcTime station { name code city { name } country { code name } } }
                        hiddenDestination { code name city { name } country { code name } }
                        code carrier { name code } operatingCarrier { name code } duration
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """
        payload = {"query": query, "variables": variables}

        try:
            # 移除保存请求文件的逻辑
            # save_to_file(payload, f"kiwi_request_{search_id}.json", "logs/kiwi_requests")
            # logger.debug(f"[{search_id}] GraphQL请求体: {json.dumps(payload)}") # 如果需要，可以记录请求体

            dest_info = variables.get('search',{}).get('itinerary',{}).get('destination',{}).get('ids',[''])[0]
            logger.info(f"[{search_id}] -> 发送GraphQL请求到 {dest_info}")

            async with httpx.AsyncClient(timeout=httpx.Timeout(timeout, connect=10.0)) as client:
                response = await client.post(
                    f"{base_url}?featureName=SearchOneWayItinerariesQuery", json=payload, headers=headers
                )
            logger.info(f"[{search_id}] <- HTTP响应状态: {response.status_code} for {dest_info}")

            try: data = response.json()
            except json.JSONDecodeError:
                logger.error(f"[{search_id}] API响应不是有效的JSON: {response.text[:500]}...") # 记录部分文本
                data = {"error": "Invalid JSON response", "status_code": response.status_code, "raw_text": response.text}
            
            # 移除保存响应文件的逻辑
            # save_to_file(data, f"kiwi_response_{search_id}.json", "logs/kiwi_responses")
            if response.status_code >= 400: # 如果是错误状态码，记录响应体用于调试
                 logger.warning(f"[{search_id}] API错误响应体 ({response.status_code}): {json.dumps(data, ensure_ascii=False)}")


            response.raise_for_status() # 确保在处理数据前检查HTTP错误

            if "errors" in data and data["errors"]:
                logger.error(f"[{search_id}] GraphQL API返回错误: {data['errors']}")
                return []
            oneway_data = data.get("data", {}).get("onewayItineraries", {})
            if oneway_data.get("__typename") == "AppError":
                logger.error(f"[{search_id}] GraphQL API应用错误: {oneway_data.get('error')}")
                return []
            itineraries = oneway_data.get("itineraries", [])
            logger.info(f"[{search_id}] 获取到 {len(itineraries)} 条原始行程 for {dest_info}")
            return itineraries
        except httpx.HTTPStatusError as exc:
            logger.error(f"[{search_id}] HTTP错误: {exc.response.status_code} for {exc.request.url}", exc_info=False) # exc_info=False 避免重复记录堆栈
            err_resp_text = exc.response.text
            logger.error(f"[{search_id}] HTTP错误响应内容: {err_resp_text[:1000]}") # 记录部分错误文本
            # 移除保存错误响应文件的逻辑
            # save_to_file(err_body, f"kiwi_error_response_{search_id}.json", "logs/kiwi_responses")
            return []
        except Exception as e:
            logger.error(f"[{search_id}] GraphQL搜索执行中发生未知异常: {e}", exc_info=True)
            # 移除保存异常文件的逻辑
            # save_to_file({"error": str(e), "type": type(e).__name__}, f"kiwi_exception_{search_id}.json", "logs/kiwi_responses")
            return []

    @staticmethod
    def _parse_datetime_flexible(time_str: Optional[str]) -> Optional[datetime]:
        if not time_str: return None
        try:
            dt_obj = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
            return dt_obj.astimezone(timezone.utc)
        except ValueError:
            try:
                dt_obj = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S")
                return dt_obj # 返回 naive，或根据业务决定是否赋予时区
            except ValueError:
                logger.warning(f"无法将 '{time_str}' 解析为datetime对象。")
                return None

    @staticmethod
    async def parse_flight_itinerary(
        raw_itinerary: Dict[str, Any],
        requested_currency: str
    ) -> Optional[Dict[str, Any]]:
        try:
            flight_id = raw_itinerary.get("id", f"unknown_id_{datetime.now(timezone.utc).timestamp()}") # 确保 flight_id 始终存在
            price_info_raw = raw_itinerary.get("price", {})
            travel_hack_raw = raw_itinerary.get("travelHack", {})
            total_duration_sec = raw_itinerary.get("duration", 0)
            pnr_count_val = raw_itinerary.get("pnrCount")

            sector_data = raw_itinerary.get("sector", {})
            sector_segments_list_raw = sector_data.get("sectorSegments", [])

            parsed_segments_list = []
            calculated_layovers_list = []
            api_hidden_destinations_on_route = []

            for i, seg_raw in enumerate(sector_segments_list_raw):
                segment_details_raw = seg_raw.get("segment", {})
                if segment_details_raw:
                    parsed_seg = SimplifiedFlightHelpers.parse_segment(segment_details_raw)
                    if parsed_seg:
                        parsed_segments_list.append(parsed_seg)
                        if parsed_seg.get("api_marked_hidden_destination"):
                            api_hidden_destinations_on_route.append(parsed_seg["api_marked_hidden_destination"])

                        if i > 0 and len(parsed_segments_list) > 1:
                            prev_seg = parsed_segments_list[i-1]
                            prev_arrival_utc_str = prev_seg["arrival"].get("utc_time")
                            curr_dep_utc_str = parsed_seg["departure"].get("utc_time")
                            
                            if prev_arrival_utc_str and curr_dep_utc_str: #确保两个时间都存在
                                prev_arrival_utc = SimplifiedFlightHelpers._parse_datetime_flexible(prev_arrival_utc_str)
                                curr_dep_utc = SimplifiedFlightHelpers._parse_datetime_flexible(curr_dep_utc_str)

                                if prev_arrival_utc and curr_dep_utc:
                                    if prev_arrival_utc.tzinfo is None or curr_dep_utc.tzinfo is None:
                                        logger.warning(f"[{flight_id}] 中转计算时遇到naive datetime，时长可能不准: {prev_arrival_utc_str} / {curr_dep_utc_str}")
                                    layover_delta_val = curr_dep_utc - prev_arrival_utc
                                    layover_mins = int(layover_delta_val.total_seconds() / 60)
                                    calculated_layovers_list.append({
                                        "duration_minutes": layover_mins,
                                        "airport_code": prev_seg["ticketed_destination"]["code"],
                                        "airport_name": prev_seg["ticketed_destination"]["name"],
                                        "city": prev_seg["ticketed_destination"]["city"],
                                        "arrival_at_layover_local": prev_seg["arrival"]["local_time"],
                                        "departure_from_layover_local": parsed_seg["departure"]["local_time"],
                                    })
                                else:
                                    calculated_layovers_list.append({"duration_minutes": -1, "airport_code": prev_seg["ticketed_destination"]["code"], "error": "UTC time parsing failed for layover"})
                            else:
                                logger.warning(f"[{flight_id}] 缺少UTC时间无法计算中转时长 for segment after {prev_seg['ticketed_destination']['code']}")
                                calculated_layovers_list.append({"duration_minutes": -2, "airport_code": prev_seg["ticketed_destination"]["code"], "error": "Missing UTC times for layover"})
            
            if not parsed_segments_list:
                logger.warning(f"[{flight_id}] 没有解析出任何航段。")
                return None

            booking_options_edges = raw_itinerary.get("bookingOptions", {}).get("edges", [])
            parsed_booking_opts = []
            for edge in booking_options_edges:
                node = edge.get("node", {})
                b_price = node.get("price", {})
                parsed_booking_opts.append({
                    "token": node.get("token"), "url": node.get("bookingUrl"),
                    "price_amount": float(b_price.get("amount", 0)) if b_price.get("amount") else 0,
                })
            if parsed_booking_opts: parsed_booking_opts.sort(key=lambda x: x["price_amount"])

            flight_info_obj = {
                "id": flight_id,
                "price": {"amount": float(price_info_raw.get("amount",0)) if price_info_raw.get("amount") else 0, "currency": requested_currency.upper()},
                "ticketed_total_duration_minutes": total_duration_sec // 60 if total_duration_sec else 0,
                "pnr_count": pnr_count_val,
                "ticketed_origin_airport": parsed_segments_list[0]["origin"],
                "ticketed_final_destination_airport": parsed_segments_list[-1]["ticketed_destination"],
                "ticketed_departure_datetime_local": parsed_segments_list[0]["departure"]["local_time"],
                "ticketed_arrival_datetime_local": parsed_segments_list[-1]["arrival"]["local_time"],
                "ticketed_stops_count": len(parsed_segments_list) - 1,
                "all_segments_on_ticket": parsed_segments_list,
                "all_layovers_on_ticket": calculated_layovers_list,
                "api_travel_hack_info": {
                    "is_true_hidden_city": travel_hack_raw.get("isTrueHiddenCity", False),
                    "is_virtual_interlining": travel_hack_raw.get("isVirtualInterlining", False),
                    "is_throwaway_ticket": travel_hack_raw.get("isThrowawayTicket", False),
                    "api_hidden_destinations_on_route": api_hidden_destinations_on_route,
                },
                "booking_options": parsed_booking_opts,
                "default_booking_url": parsed_booking_opts[0]["url"] if parsed_booking_opts else None,
                "display_flight_type": "Unknown",
                "user_perceived_destination_airport": parsed_segments_list[-1]["ticketed_destination"],
                "user_journey_segments_to_display": parsed_segments_list,
                "user_journey_layovers_to_display": calculated_layovers_list,
                "user_journey_duration_minutes": total_duration_sec // 60 if total_duration_sec else 0,
                "user_journey_arrival_datetime_local": parsed_segments_list[-1]["arrival"]["local_time"],
                "user_alert_notes": [],
                "_internal_debug_markers": {}
            }
            return flight_info_obj
        except Exception as e:
            fid = raw_itinerary.get("id", "PARSE_ITI_ERROR_UNKNOWN")
            logger.error(f"[{fid}] 解析航班行程时发生严重错误: {e}", exc_info=True)
            return None

    @staticmethod
    def parse_segment(segment_data_raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            source_raw = segment_data_raw.get("source", {})
            dest_raw = segment_data_raw.get("destination", {})
            carrier_raw = segment_data_raw.get("carrier", {})
            op_carrier_raw = segment_data_raw.get("operatingCarrier", {})
            api_hidden_dest_raw = segment_data_raw.get("hiddenDestination", {})

            source_station = source_raw.get("station", {})
            dest_station = dest_raw.get("station", {})

            # Ensure critical time fields have fallbacks to None if not present or empty
            dep_local_time = source_raw.get("localTime") or None
            dep_utc_time = source_raw.get("utcTime") or None
            arr_local_time = dest_raw.get("localTime") or None
            arr_utc_time = dest_raw.get("utcTime") or None


            parsed_seg_obj = {
                "flight_number": segment_data_raw.get("code", ""),
                "marketing_carrier": {"code": carrier_raw.get("code"), "name": carrier_raw.get("name")},
                "operating_carrier": {"code": op_carrier_raw.get("code"), "name": op_carrier_raw.get("name")} if op_carrier_raw and op_carrier_raw.get("code") else None,
                "origin": {
                    "code": source_station.get("code"), "name": source_station.get("name"),
                    "city": source_station.get("city", {}).get("name"),
                    "country_code": source_station.get("country", {}).get("code"),
                    "country_name": source_station.get("country", {}).get("name"),
                },
                "ticketed_destination": {
                    "code": dest_station.get("code"), "name": dest_station.get("name"),
                    "city": dest_station.get("city", {}).get("name"),
                    "country_code": dest_station.get("country", {}).get("code"),
                    "country_name": dest_station.get("country", {}).get("name"),
                },
                "departure": {"local_time": dep_local_time, "utc_time": dep_utc_time},
                "arrival": {"local_time": arr_local_time, "utc_time": arr_utc_time},
                "duration_minutes": segment_data_raw.get("duration", 0) // 60,
                "api_marked_hidden_destination": {
                    "code": api_hidden_dest_raw.get("code"), "name": api_hidden_dest_raw.get("name"),
                    "city": api_hidden_dest_raw.get("city", {}).get("name"),
                    "country_code": api_hidden_dest_raw.get("country", {}).get("code"),
                    "country_name": api_hidden_dest_raw.get("country", {}).get("name"),
                } if api_hidden_dest_raw and api_hidden_dest_raw.get("code") else None,
            }
            return parsed_seg_obj
        except Exception as e:
            flight_num = segment_data_raw.get('code', 'UNKNOWN_FLIGHT')
            logger.error(f"解析航段数据失败 {flight_num}: {e}", exc_info=True)
            return None

    @staticmethod
    def get_throwaway_destinations(origin_iata_code: str, target_dest_iata_code: str) -> List[str]:
        throwaway_map = { # 这个列表可以从配置文件或数据库加载
            "PEK": ["NRT", "ICN", "SIN", "BKK", "KUL", "MNL", "TPE", "CEB", "MFM", "HKG"],
            "PVG": ["NRT", "ICN", "SIN", "BKK", "KUL", "MNL", "TPE", "CEB", "MFM", "HKG"],
            "CAN": ["SIN", "BKK", "KUL", "MNL", "TPE", "ICN", "CEB", "MFM", "HKG"],
            "LHR": ["AMS", "CDG", "FRA", "DUB", "IST", "BCN", "MAD"], # 欧洲示例
            "JFK": ["LAX", "MIA", "YYZ", "MEX", "BOG"], # 美洲示例
            "DEFAULT": ["NRT", "ICN", "SIN", "BKK", "KUL", "MNL", "TPE", "HKG", "CEB", "MFM", "AMS", "IST"]
        }
        potential_dests = throwaway_map.get(origin_iata_code.upper(), throwaway_map["DEFAULT"])
        return list(set(d for d in potential_dests if d.upper() != target_dest_iata_code.upper()))

    @staticmethod
    def deduplicate_flights(flights_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not flights_list: return []
        seen_flight_ids = set()
        unique_flights_list = []
        for flight_item in flights_list:
            flight_id_val = flight_item.get("id")
            if flight_id_val and flight_id_val not in seen_flight_ids:
                seen_flight_ids.add(flight_id_val)
                unique_flights_list.append(flight_item)
            elif not flight_id_val:
                 unique_flights_list.append(flight_item)
                 logger.warning(f"Deduplicating flight with no ID: {flight_item.get('ticketed_origin_airport',{}).get('code')}")
        unique_flights_list.sort(key=lambda x: (
            x.get("price", {}).get("amount", float('inf')),
            x.get("user_journey_duration_minutes", x.get("ticketed_total_duration_minutes", float('inf')))
        ))
        return unique_flights_list

    @staticmethod
    def get_disclaimer_flags(direct_flights_found: bool, hidden_city_flights_found: bool) -> Dict[str, bool]:
        return {
            "show_direct_flight_disclaimer_key": direct_flights_found, # 前端用这个key找文本
            "show_hidden_city_disclaimer_key": hidden_city_flights_found, # 前端用这个key找文本
        }

# --- 上层协调逻辑 (示例) ---
async def find_and_classify_flights(
    search_request: MockFlightSearchRequest,
    api_headers: Dict[str, str]
) -> Dict[str, Any]:
    request_id_prefix = f"{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}_{search_request.origin_iata}_{search_request.destination_iata}"
    target_destination = search_request.destination_iata.upper()
    origin_airport = search_request.origin_iata.upper()
    requested_currency = search_request.preferred_currency or "cny"

    all_parsed_itineraries = []

    # --- 步骤 1: 搜索主要目的地 ---
    main_search_id = f"{request_id_prefix}_S1_main"
    logger.info(f"[{main_search_id}] 1. 主要目的地搜索: {origin_airport} -> {target_destination}")
    main_vars = SimplifiedFlightHelpers.build_graphql_variables(search_request, search_request.is_one_way)
    main_vars["filter"]["limit"] = 40
    main_vars["filter"]["flightsApiLimit"] = 50

    raw_main_itineraries = await SimplifiedFlightHelpers.execute_graphql_search(main_vars, api_headers, main_search_id)
    for raw_iti in raw_main_itineraries:
        parsed = await SimplifiedFlightHelpers.parse_flight_itinerary(raw_iti, requested_currency)
        if parsed:
            parsed["_internal_debug_markers"]["search_type"] = "main_destination"
            all_parsed_itineraries.append(parsed)
    logger.info(f"[{main_search_id}] 主要目的地搜索完成，解析到 {len([p for p in all_parsed_itineraries if p['_internal_debug_markers']['search_type'] == 'main_destination'])} 条有效行程。")

    # --- 步骤 2: 搜索周边/甩尾目的地 ---
    throwaway_search_id_prefix = f"{request_id_prefix}_S2_throwaway"
    potential_throwaway_dests = SimplifiedFlightHelpers.get_throwaway_destinations(origin_airport, target_destination)
    logger.info(f"[{throwaway_search_id_prefix}] 2. 周边/甩尾目的地搜索，潜在甩尾点: {potential_throwaway_dests}")

    throwaway_search_tasks = []
    for i, td_code in enumerate(potential_throwaway_dests):
        # 使用 Pydantic 的 .copy() 方法或 dataclasses.replace()
        # 对于 MockFlightSearchRequest，我们用 .copy()
        throwaway_req_obj = search_request.copy(update={"destination_iata": td_code})
        
        throwaway_vars = SimplifiedFlightHelpers.build_graphql_variables(throwaway_req_obj, throwaway_req_obj.is_one_way)
        throwaway_vars["filter"]["limit"] = 15 # 甩尾搜索的结果可以少一些
        throwaway_vars["filter"]["maxStopsCount"] = max(throwaway_vars["filter"].get("maxStopsCount", 2), 2) # 确保至少允许2次中转

        task_id = f"{throwaway_search_id_prefix}_{i}_{td_code}"
        throwaway_search_tasks.append(
            SimplifiedFlightHelpers.execute_graphql_search(throwaway_vars, api_headers, task_id)
        )

    if throwaway_search_tasks:
        logger.info(f"[{throwaway_search_id_prefix}] 并行执行 {len(throwaway_search_tasks)} 个甩尾搜索任务...")
        results_from_throwaway = await asyncio.gather(*throwaway_search_tasks, return_exceptions=True)
        
        for i, res_or_exc in enumerate(results_from_throwaway):
            td_code = potential_throwaway_dests[i]
            if isinstance(res_or_exc, Exception):
                logger.error(f"[{throwaway_search_id_prefix}] 甩尾搜索到 {td_code} 失败: {res_or_exc}")
                continue
            if res_or_exc:
                for raw_iti in res_or_exc:
                    parsed = await SimplifiedFlightHelpers.parse_flight_itinerary(raw_iti, requested_currency)
                    if parsed:
                        parsed["_internal_debug_markers"]["search_type"] = "throwaway_search"
                        parsed["_internal_debug_markers"]["throwaway_ticketed_dest"] = td_code
                        all_parsed_itineraries.append(parsed)
    logger.info(f"[{throwaway_search_id_prefix}] 周边/甩尾目的地搜索完成。")

    # --- 步骤 3: 结果整合与分类 ---
    classification_id = f"{request_id_prefix}_S3_classify"
    logger.info(f"[{classification_id}] 3. 开始整合与分类，总共解析到 {len(all_parsed_itineraries)} 条不重复前的行程...")
    unique_itineraries = SimplifiedFlightHelpers.deduplicate_flights(all_parsed_itineraries)
    logger.info(f"[{classification_id}] 去重后得到 {len(unique_itineraries)} 条独立行程。")

    direct_flights_final = []
    hidden_city_flights_final = []
    # other_flights_final = [] # 可选：用于存储普通中转等

    for flight in unique_itineraries:
        is_api_hc = flight["api_travel_hack_info"]["is_true_hidden_city"]
        num_ticket_segments = len(flight["all_segments_on_ticket"])

        # 类别A: 真实直达
        if num_ticket_segments == 1 and not is_api_hc and \
           flight["ticketed_final_destination_airport"]["code"] == target_destination:
            flight["display_flight_type"] = "直达"
            # user_journey... 字段已在解析时默认设置为票面全程，对于直达是正确的
            direct_flights_final.append(flight)
            continue

        # 类别B: API标记的隐藏城市 (用户在目标城市下机)
        if is_api_hc:
            can_drop_off_at_target = False
            user_segments = []
            user_layovers = [] # Layovers before reaching target_destination
            arrival_at_target_local = None
            
            for seg_idx, segment in enumerate(flight["all_segments_on_ticket"]):
                user_segments.append(segment)
                if seg_idx > 0: # Add layover before this segment
                     # Ensure index is valid for all_layovers_on_ticket
                    if flight["all_layovers_on_ticket"] and (seg_idx -1) < len(flight["all_layovers_on_ticket"]):
                        user_layovers.append(flight["all_layovers_on_ticket"][seg_idx-1])
                
                if segment["ticketed_destination"]["code"] == target_destination:
                    # This segment lands at the target destination
                    arrival_at_target_local = segment["arrival"]["local_time"]
                    
                    # Check if this is a valid drop-off point (i.e., not the ticketed final destination *unless* it's a single-segment HC)
                    if flight["ticketed_final_destination_airport"]["code"] != target_destination or num_ticket_segments == 1:
                        can_drop_off_at_target = True
                        flight["display_flight_type"] = "隐藏城市"
                        flight["user_perceived_destination_airport"] = segment["ticketed_destination"]
                        flight["user_journey_segments_to_display"] = list(user_segments) # Take a copy
                        flight["user_journey_layovers_to_display"] = list(user_layovers)
                        flight["user_journey_arrival_datetime_local"] = arrival_at_target_local
                        
                        dep_dt_utc_str = flight["all_segments_on_ticket"][0]["departure"].get("utc_time")
                        arr_dt_utc_str = segment["arrival"].get("utc_time")
                        dep_dt = SimplifiedFlightHelpers._parse_datetime_flexible(dep_dt_utc_str)
                        arr_dt = SimplifiedFlightHelpers._parse_datetime_flexible(arr_dt_utc_str)
                        if dep_dt and arr_dt:
                            flight["user_journey_duration_minutes"] = int((arr_dt - dep_dt).total_seconds() / 60)
                        else:
                            flight["user_journey_duration_minutes"] = -1 # Indicate error or unknown

                        flight["user_alert_notes"].append(f"需在“{target_destination}”提前下机。")
                        if flight["ticketed_final_destination_airport"]["code"] != target_destination:
                            flight["user_alert_notes"].append(f"票面终点“{flight['ticketed_final_destination_airport']['code']}”。")
                        hidden_city_flights_final.append(flight)
                        break # Found drop-off point
            if can_drop_off_at_target:
                continue
        
        # 类别C: 构造的隐藏城市 (通过甩尾搜索，在中转点是目标城市)
        if flight["_internal_debug_markers"].get("search_type") == "throwaway_search":
            can_construct_hc = False
            user_segments = []
            user_layovers = []
            arrival_at_target_local = None

            for seg_idx, segment in enumerate(flight["all_segments_on_ticket"]):
                user_segments.append(segment)
                if seg_idx > 0:
                    if flight["all_layovers_on_ticket"] and (seg_idx -1) < len(flight["all_layovers_on_ticket"]):
                        layover = flight["all_layovers_on_ticket"][seg_idx-1]
                        user_layovers.append(layover)
                        # Check if the layover (i.e., previous segment's destination) is the target
                        if layover["airport_code"] == target_destination:
                            arrival_at_target_local = flight["all_segments_on_ticket"][seg_idx-1]["arrival"]["local_time"]
                            can_construct_hc = True
                            flight["display_flight_type"] = "隐藏城市 (中转即达)"
                            flight["user_perceived_destination_airport"] = flight["all_segments_on_ticket"][seg_idx-1]["ticketed_destination"]
                            flight["user_journey_segments_to_display"] = list(user_segments[:-1]) # Segments up to target
                            flight["user_journey_layovers_to_display"] = list(user_layovers[:-1]) # Layovers before target
                            flight["user_journey_arrival_datetime_local"] = arrival_at_target_local
                           
                            dep_dt_utc_str = flight["all_segments_on_ticket"][0]["departure"].get("utc_time")
                            arr_dt_utc_str = flight["all_segments_on_ticket"][seg_idx-1]["arrival"].get("utc_time")
                            dep_dt = SimplifiedFlightHelpers._parse_datetime_flexible(dep_dt_utc_str)
                            arr_dt = SimplifiedFlightHelpers._parse_datetime_flexible(arr_dt_utc_str)
                            if dep_dt and arr_dt:
                                flight["user_journey_duration_minutes"] = int((arr_dt - dep_dt).total_seconds() / 60)
                            else:
                                flight["user_journey_duration_minutes"] = -1
                            
                            flight["user_alert_notes"].append(f"需在中转站“{target_destination}”提前结束行程。")
                            flight["user_alert_notes"].append(f"票面终点“{flight['ticketed_final_destination_airport']['code']}”。")
                            hidden_city_flights_final.append(flight)
                            break # Found HC opportunity
                if can_construct_hc: break # Break outer loop as well
            if can_construct_hc:
                continue
        
        # 可选：处理普通中转到目标城市的航班
        # if num_ticket_segments > 1 and not is_api_hc and \
        #    flight["_internal_debug_markers"].get("search_type") != "throwaway_search" and \
        #    flight["ticketed_final_destination_airport"]["code"] == target_destination:
        #     flight["display_flight_type"] = "普通中转"
        #     # user_journey... fields are already set to full ticketed journey
        #     other_flights_final.append(flight)

    direct_flights_final = SimplifiedFlightHelpers.deduplicate_flights(direct_flights_final)
    hidden_city_flights_final = SimplifiedFlightHelpers.deduplicate_flights(hidden_city_flights_final)
    # other_flights_final = SimplifiedFlightHelpers.deduplicate_flights(other_flights_final)

    logger.info(f"[{classification_id}] 分类完成。直达: {len(direct_flights_final)}, 隐藏城市: {len(hidden_city_flights_final)}")

    return {
        "direct_flights": direct_flights_final,
        "hidden_city_flights": hidden_city_flights_final,
        # "other_transfer_flights": other_flights_final,
        "disclaimer_flags": SimplifiedFlightHelpers.get_disclaimer_flags(
            direct_flights_found=bool(direct_flights_final),
            hidden_city_flights_found=bool(hidden_city_flights_final)
        )
    }

async def main_example_usage():
    # 确保在测试时替换为真实的API Key
    test_headers = {
        "Content-Type": "application/json",
        "apikey": os.environ.get("KIWI_API_KEY", "YOUR_KIWI_API_KEY_HERE") # 从环境变量或直接设置
    }
    if "YOUR_KIWI_API_KEY_HERE" in test_headers["apikey"]:
        logger.warning("请设置有效的KIWI_API_KEY环境变量或直接在代码中替换。")
        # return

    # 示例1: LHR -> PKX (北京大兴)
    request1 = MockFlightSearchRequest(
        origin_iata="LHR",
        destination_iata="PKX",
        departure_date_from="2024-09-15", # 使用未来的日期
        departure_date_to="2024-09-15",
        adults=1,
        cabin_class="ECONOMY",
        preferred_currency="cny"
    )
    logger.info(f"开始测试 LHR->PKX...")
    results1 = await find_and_classify_flights(request1, test_headers)
    # 为了避免控制台输出过长，我们只打印数量
    logger.info(f"LHR->PKX 结果: 直达 {len(results1['direct_flights'])}, 隐藏城市 {len(results1['hidden_city_flights'])}")
    with open("results_lhr_pkx.json", "w", encoding="utf-8") as f:
         json.dump(results1, f, indent=2, ensure_ascii=False)
    logger.info("LHR->PKX 结果已保存到 results_lhr_pkx.json")

    await asyncio.sleep(2) # API 可能有速率限制

    # 示例2: 中国国内，例如 PEK -> CAN (广州)
    # request2 = MockFlightSearchRequest(
    #     origin_iata="PEK",
    #     destination_iata="CAN",
    #     departure_date_from="2024-08-20",
    #     departure_date_to="2024-08-20",
    #     adults=1
    # )
    # logger.info(f"开始测试 PEK->CAN...")
    # results2 = await find_and_classify_flights(request2, test_headers)
    # logger.info(f"PEK->CAN 结果: 直达 {len(results2['direct_flights'])}, 隐藏城市 {len(results2['hidden_city_flights'])}")
    # with open("results_pek_can.json", "w", encoding="utf-8") as f:
    #      json.dump(results2, f, indent=2, ensure_ascii=False)
    # logger.info("PEK->CAN 结果已保存到 results_pek_can.json")


if __name__ == "__main__":
    # 运行示例
    asyncio.run(main_example_usage())