"""
简化航班搜索服务的辅助方法
"""

import json
import logging
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)

def save_to_file(data, filename, directory="logs"):
    """将数据保存到文件"""
    try:
        # 确保目录存在
        os.makedirs(directory, exist_ok=True)

        # 构建完整的文件路径
        filepath = os.path.join(directory, filename)

        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            if isinstance(data, str):
                f.write(data)
            else:
                json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"数据已保存到文件: {filepath}")
    except Exception as e:
        logger.error(f"保存数据到文件失败: {e}")

class SimplifiedFlightHelpers:
    """简化航班搜索的辅助方法"""

    @staticmethod
    def _map_cabin_class(cabin_class: str) -> str:
        """
        映射舱位等级到Kiwi.com GraphQL API期望的格式

        Args:
            cabin_class: 前端传入的舱位等级

        Returns:
            映射后的舱位等级
        """
        cabin_mapping = {
            "ECONOMY": "ECONOMY",
            "PREMIUM_ECONOMY": "PREMIUM_ECONOMY",
            "BUSINESS": "BUSINESS",  # API期望的格式
            "BUSINESS_CLASS": "BUSINESS",  # 映射到API期望的格式
            "FIRST": "FIRST",  # API期望的格式
            "FIRST_CLASS": "FIRST"  # 映射到API期望的格式
        }

        mapped_class = cabin_mapping.get(cabin_class or "ECONOMY", "ECONOMY")
        logger.info(f"舱位等级映射: {cabin_class} -> {mapped_class}")
        return mapped_class

    @staticmethod
    def build_graphql_variables(request, is_one_way: bool) -> Dict[str, Any]:
        """构建GraphQL查询变量"""
        # 解析日期
        dep_date_start = datetime.strptime(request.departure_date_from, "%Y-%m-%d")
        dep_date_end = datetime.strptime(request.departure_date_to, "%Y-%m-%d") if request.departure_date_to else dep_date_start

        # 构建搜索参数
        search_params = {
            "itinerary": {
                "source": {"ids": [f"Station:airport:{request.origin_iata.upper()}"]},
                "destination": {"ids": [f"Station:airport:{request.destination_iata.upper()}"]},
                "outboundDepartureDate": {
                    "start": dep_date_start.strftime("%Y-%m-%dT00:00:00"),
                    "end": dep_date_end.strftime("%Y-%m-%dT23:59:59")
                }
            },
            "passengers": {
                "adults": request.adults,
                "children": 0,
                "infants": 0,
                "adultsHoldBags": [0],
                "adultsHandBags": [0],
                "childrenHoldBags": [],
                "childrenHandBags": []
            },
            "cabinClass": {
                "cabinClass": SimplifiedFlightHelpers._map_cabin_class(request.cabin_class),
                "applyMixedClasses": False
            }
        }

        # 如果是往返票，添加返程日期
        if not is_one_way and request.return_date_from:
            ret_date_start = datetime.strptime(request.return_date_from, "%Y-%m-%d")
            ret_date_end = datetime.strptime(request.return_date_to, "%Y-%m-%d") if request.return_date_to else ret_date_start
            search_params["itinerary"]["inboundDepartureDate"] = {
                "start": ret_date_start.strftime("%Y-%m-%dT00:00:00"),
                "end": ret_date_end.strftime("%Y-%m-%dT23:59:59")
            }

        # 构建过滤参数
        filter_params = {
            "allowChangeInboundDestination": True,
            "allowChangeInboundSource": True,
            "allowDifferentStationConnection": True,
            "enableSelfTransfer": True,
            "enableThrowAwayTicketing": True,
            "enableTrueHiddenCity": True,
            "maxStopsCount": 3,  # 放宽限制，允许最多3次中转
            "transportTypes": ["FLIGHT"],
            "contentProviders": ["KIWI"],
            "flightsApiLimit": 25,
            "limit": 10
        }

        # 构建选项参数
        options_params = {
            "sortBy": "QUALITY",
            "mergePriceDiffRule": "INCREASED",
            "currency": request.preferred_currency.lower() if request.preferred_currency else "cny",
            "apiUrl": None,
            "locale": "cn",
            "market": "us",
            "partner": "skypicker",
            "partnerMarket": "cn",
            "affilID": "cj_5250933",
            "storeSearch": False,
            "searchStrategy": "REDUCED",
            "abTestInput": {
                "priceElasticityGuarantee": "DISABLE",
                "baggageProtectionBundle": "ENABLE",
                "paretoProtectVanilla": "ENABLE",
                "kiwiBasicThirdIteration": "C",
                "offerStrategiesNonT1": "DISABLE",
                "kayakWithoutBags": "DISABLE",
                "carriersDeeplinkResultsEnable": True,
                "carriersDeeplinkOnSEMEnable": True
            },
            "serverToken": None,
            "searchSessionId": None
        }

        return {
            "search": search_params,
            "filter": filter_params,
            "options": options_params,
            "conditions": False
        }

    @staticmethod
    async def execute_graphql_search(
        variables: Dict[str, Any],
        headers: Dict[str, str],
        search_id: str,
        base_url: str = "https://api.skypicker.com/umbrella/v2/graphql",
        timeout: float = 30.0
    ) -> List[Dict[str, Any]]:
        """执行GraphQL搜索"""
        # 构建GraphQL查询（基于爬虫相关数据.txt中的查询）
        query = """
        query SearchOneWayItinerariesQuery(
          $search: SearchOnewayInput
          $filter: ItinerariesFilterInput
          $options: ItinerariesOptionsInput
          $conditions: Boolean!
        ) {
          onewayItineraries(search: $search, filter: $filter, options: $options) {
            __typename
            ... on AppError {
              error: message
            }
            ... on Itineraries {
              server {
                requestId
                environment
                packageVersion
                serverToken
              }
              metadata {
                eligibilityInformation {
                  baggageEligibilityInformation {
                    topFiveResultsBaggageEligibleForPrompt
                    numberOfBags
                  }
                  guaranteeAndRedirectsEligibilityInformation {
                    redirect {
                      anywhere
                      top10
                      isKiwiAvailable
                    }
                    guarantee {
                      anywhere
                      top10
                    }
                    combination {
                      anywhere
                      top10
                    }
                  }
                  kiwiBasicEligibility {
                    anywhere
                    top10
                  }
                  topThreeResortingOccurred
                  carriersDeeplinkEligibility
                  responseContainsKayakItinerary
                  paretoABTestEligible
                }
                carriers {
                  code
                  id
                  name
                }
                ...AirlinesFilter_data
                ...CountriesFilter_data
                ...WeekDaysFilter_data
                ...TravelTip_data
                ...Sorting_data
                ...useSortingModes_data
                ...PriceAlert_data
                itinerariesCount
                hasMorePending
                missingProviders {
                  code
                }
                searchFingerprint
                statusPerProvider {
                  provider {
                    id
                  }
                  errorHappened
                  errorMessage
                }
                hasTier1MarketItineraries
                sharedItinerary { # 如果需要分享功能，否则可以考虑移除以简化
                  __typename
                  ...TripInfo
                  ...ItineraryDebug @include(if: $conditions)
                  # ... (sharedItinerary 展开的类型和字段) ...
                  # 这部分如果不需要可以大大简化 query
                }
                kayakEligibilityTest {
                  containsKayakWithNewRules
                  containsKayakWithCurrentRules
                  containsKayakAirlinesWithNewRules
                }
              }
              itineraries {
                __typename
                ...TripInfo # 主要行程信息从此 Fragment 获取
                ...ItineraryDebug @include(if: $conditions) # 条件性调试信息
                ... on ItineraryOneWay {
                  # ItineraryOneWay 特有的一些字段，不在TripInfo里的
                  legacyId # 例如
                  # sector { id duration ... } # sector 的部分核心信息可能在 TripInfo, 更细节的直接请求
                  # 如果 TripInfo 包含了 sector 的全部所需信息，这里就不需要重复
                  # 但通常 ItineraryOneWay 会直接请求 sector 及其子结构

                  # 以下是示例，实际应基于 TripInfo 和你的需求决定哪些在此处直接请求
                  sector {
                      id
                      duration
                      sectorSegments {
                          guarantee
                          segment {
                              id
                              source {
                                  localTime
                                  utcTimeIso
                                  station {
                                      # ... (从 PrebookingStation 或直接请求) ...
                                      # 基于你的响应，这里请求了全部细节
                                      id legacyId name code type gps { lat lng }
                                      city { legacyId name id }
                                      country { code id }
                                  }
                              }
                              destination {
                                  localTime
                                  utcTimeIso
                                  station {
                                      # ... (同上) ...
                                      id legacyId name code type gps { lat lng }
                                      city { legacyId name id }
                                      country { code id }
                                  }
                              }
                              duration
                              type
                              code # flight number
                              carrier { id name code }
                              operatingCarrier { id name code }
                              cabinClass
                              hiddenDestination { # 重要，为隐藏城市信息
                                  code name city { name id } country { name id } id
                              }
                              throwawayDestination { id }
                          }
                          layover {
                              duration isBaggageRecheck isWalkingDistance transferDuration id
                          }
                      }
                  }
                  lastAvailable { seatsLeft }
                  isRyanair
                  benefitsData { # 内容省略，按需添加
                      automaticCheckinAvailable instantChatSupportAvailable disruptionProtectionAvailable
                      guaranteeAvailable guaranteeFee { roundedAmount } guaranteeFeeEur { amount }
                      searchReferencePrice { roundedAmount }
                  }
                  isAirBaggageBundleEligible
                  testEligibilityInformation { paretoABTestNewItinerary }
                }
                id # Itinerary 顶层的ID
              }
            }
          }
        }

        # --- 以下是所有必须的 Fragment 定义 ---
        fragment AirlinesFilter_data on ItinerariesMetadata {
          carriers { id code name }
        }
        fragment CountriesFilter_data on ItinerariesMetadata {
          stopoverCountries { code name id }
        }
        fragment ItineraryDebug on Itinerary {
          __isItinerary: __typename
          itineraryDebugData { debug }
        }
        fragment PrebookingStation on Station {
          code type city { name id }
        }
        fragment PriceAlert_data on ItinerariesMetadata {
          priceAlertExists existingPriceAlert { id } searchFingerprint hasMorePending
          priceAlertsTopResults {
            best { price { amount } } cheapest { price { amount } } fastest { price { amount } }
            sourceTakeoffAsc { price { amount } } destinationLandingAsc { price { amount } }
          }
        }
        fragment Sorting_data on ItinerariesMetadata {
          topResults {
            best { __typename duration price { amount } id }
            cheapest { __typename duration price { amount } id }
            fastest { __typename duration price { amount } id }
            sourceTakeoffAsc { __typename duration price { amount } id }
            destinationLandingAsc { __typename duration price { amount } id }
          }
        }
        fragment TravelTip_data on ItinerariesMetadata {
          travelTips { # 内容非常多，后端按需解析或直接透传
            __typename
            ... on TravelTipRadiusMoney { radius params { name value } savingMoney: saving { amount currency { id code name } formattedValue } location { __typename id legacyId name slug } }
            ... on TravelTipRadiusTime { radius params { name value } saving location { __typename id legacyId name slug } }
            ... on TravelTipRadiusSome { radius params { name value } location { __typename id legacyId name slug } }
            ... on TravelTipDateMoney { dates { start end } params { name value } savingMoney: saving { amount currency { id code name } formattedValue } }
            ... on TravelTipDateTime { dates { start end } params { name value } saving }
            ... on TravelTipDateSome { dates { start end } params { name value } }
            ... on TravelTipExtend { destination { __typename id name slug } locations { __typename id name slug } price { amount currency { id code name } formattedValue } }
          }
        }
        fragment TripInfo on Itinerary { # 核心行程信息
          __isItinerary: __typename
          id # 通常 id, shareId 在 Itinerary 级别获取，不一定在 TripInfo
          shareId
          price { amount priceBeforeDiscount }
          priceEur { amount }
          provider { name code hasHighProbabilityOfPriceChange contentProvider { code } id }
          bagsInfo {
            includedCheckedBags includedHandBags hasNoBaggageSupported hasNoCheckedBaggage
            checkedBagTiers { tierPrice { amount } bags { weight { value } } }
            handBagTiers { tierPrice { amount } bags { weight { value } } }
            includedPersonalItem
            personalItemTiers { tierPrice { amount } bags { weight { value } height { value } width { value } length { value } } }
          }
          bookingOptions {
            edges {
              node {
                token bookingUrl trackingPixel
                itineraryProvider { code name subprovider hasHighProbabilityOfPriceChange contentProvider { code } providerCategory id }
                price { amount } priceEur { amount }
                priceLocks {
                  priceLocksCurr { default price { amount roundedFormattedValue } }
                  priceLocksEur { default price { amount roundedFormattedValue } }
                }
                kiwiProduct disruptionTreatment usRulesApply
              }
            }
          }
          travelHack { isTrueHiddenCity isVirtualInterlining isThrowawayTicket }
          duration
          pnrCount
          # sector 信息可以在这里定义一部分，或者在具体类型如 ItineraryOneWay 中定义
          # 基于你的响应，TripInfo 里也包含了 sector 的基本结构
          ... on ItineraryOneWay { # TripInfo 也可以针对不同类型有不同字段
            sector {
              id # 确保 TripInfo 包含的 sector 结构与主 query 一致
              sectorSegments {
                segment {
                  source { station { ...PrebookingStation id } localTime }
                  destination { station { ...PrebookingStation id } }
                  id
                }
              }
            }
          }
          # ... (其他 ItineraryReturn, ItineraryMulticity 的 TripInfo 展开)
        }
        fragment WeekDaysFilter_data on ItinerariesMetadata {
          inboundDays outboundDays
        }
        fragment useSortingModes_data on ItinerariesMetadata { # 与 Sorting_data 类似
          topResults {
            best { __typename duration price { amount } id }
            cheapest { __typename duration price { amount } id }
            fastest { __typename duration price { amount } id }
            sourceTakeoffAsc { __typename duration price { amount } id }
            destinationLandingAsc { __typename duration price { amount } id }
          }
        }
        """

        payload = {
            "query": query,
            "variables": variables
        }

        try:
            # 初始化保存状态跟踪
            if not hasattr(SimplifiedFlightHelpers, "_saved_requests"):
                SimplifiedFlightHelpers._saved_requests = set()
            if not hasattr(SimplifiedFlightHelpers, "_has_saved_kiwi_response"):
                SimplifiedFlightHelpers._has_saved_kiwi_response = False

            # 添加调试日志验证修复
            logger.info(f"[{search_id}] 发送GraphQL请求，关键参数验证:")
            logger.info(f"[{search_id}] - maxStopsCount: {variables.get('filter', {}).get('maxStopsCount', 'MISSING')}")
            logger.info(f"[{search_id}] - enableTrueHiddenCity: {variables.get('filter', {}).get('enableTrueHiddenCity', 'MISSING')}")
            logger.info(f"[{search_id}] - enableSelfTransfer: {variables.get('filter', {}).get('enableSelfTransfer', 'MISSING')}")
            logger.info(f"[{search_id}] - enableThrowAwayTicketing: {variables.get('filter', {}).get('enableThrowAwayTicketing', 'MISSING')}")
            logger.info(f"[{search_id}] - cabinClass: {variables.get('search', {}).get('cabinClass', {}).get('cabinClass', 'MISSING')}")

            async with httpx.AsyncClient(timeout=timeout) as client:
                # 只保存第一次请求到文件
                base_search_id = search_id.split('_')[0] + '_' + search_id.split('_')[1]  # 提取基础search_id
                if base_search_id not in SimplifiedFlightHelpers._saved_requests:
                    save_to_file(payload, f"kiwi_request_{search_id}.json", "logs/kiwi_requests")
                    SimplifiedFlightHelpers._saved_requests.add(base_search_id)
                    logger.info(f"[{search_id}] 已保存请求文件")
                else:
                    logger.info(f"[{search_id}] 跳过保存请求文件（已保存过）")

                response = await client.post(
                    f"{base_url}?featureName=SearchOneWayItinerariesQuery",
                    json=payload,
                    headers=headers
                )

                # 添加响应状态日志
                logger.info(f"[{search_id}] HTTP响应状态: {response.status_code}")

                response.raise_for_status()

                data = response.json()
                # logger.info(f"[{search_id}] 原始GraphQL响应JSON: {json.dumps(data, indent=2, ensure_ascii=False)}")

                # 只保存一次原始响应到文件
                if not SimplifiedFlightHelpers._has_saved_kiwi_response:
                    save_to_file(data, f"kiwi_response_{search_id}.json", "logs/kiwi_responses")
                    SimplifiedFlightHelpers._has_saved_kiwi_response = True

                # 检查GraphQL错误
                if "errors" in data:
                    logger.error(f"[{search_id}] GraphQL错误: {data['errors']}")
                    return []

                # 提取航班数据
                oneway_itineraries = data.get("data", {}).get("onewayItineraries", {})
                if oneway_itineraries.get("__typename") == "AppError":
                    logger.error(f"[{search_id}] API错误: {oneway_itineraries.get('error')}")
                    return []

                itineraries = oneway_itineraries.get("itineraries", [])
                logger.info(f"[{search_id}] 获取到 {len(itineraries)} 个原始航班结果")

                return itineraries

        except httpx.HTTPStatusError as exc: # 更具体地捕获 HTTP 错误
            logger.error(f"[{search_id}] GraphQL请求发生HTTP错误: {exc.response.status_code}")
            try:
                # 尝试解析并记录JSON响应体，如果它是JSON的话
                response_body = exc.response.json()
                logger.error(f"[{search_id}] 错误响应体 (JSON): {json.dumps(response_body, indent=2, ensure_ascii=False)}")
            except json.JSONDecodeError:
                # 如果响应体不是JSON，则记录为文本
                logger.error(f"[{search_id}] 错误响应体 (Text): {exc.response.text}")

            # 记录详细的请求信息为DEBUG级别，因为它们可能很大或包含敏感数据
            logger.debug(f"[{search_id}] 失败请求的 Headers: {headers}")
            logger.debug(f"[{search_id}] 失败请求的 Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
            return []

        # 记录Kiwi API的完整响应
        SimplifiedFlightHelpers.log_kiwi_response(search_id, data)
        return []

    @staticmethod
    async def parse_flight_itinerary(raw_itinerary: Dict[str, Any], is_one_way: bool) -> Optional[Dict[str, Any]]:
        """解析航班行程数据"""
        try:
            # 提取基本信息
            flight_id = raw_itinerary.get("id", "")
            price_info = raw_itinerary.get("price", {})
            price_eur = raw_itinerary.get("priceEur", {})
            travel_hack = raw_itinerary.get("travelHack", {})
            duration = raw_itinerary.get("duration", 0)

            # 检查是否为隐藏城市航班
            is_hidden_city = travel_hack.get("isTrueHiddenCity", False)

            # 提取航段信息
            sector = raw_itinerary.get("sector", {})
            sector_segments = sector.get("sectorSegments", [])

            segments = []
            hidden_destinations = []

            for sector_segment in sector_segments:
                segment_data = sector_segment.get("segment", {})
                if segment_data:
                    segment = SimplifiedFlightHelpers.parse_segment(segment_data)
                    if segment:
                        segments.append(segment)
                        # 收集隐藏目的地信息
                        if segment.get("hidden_destination"):
                            hidden_destinations.append(segment["hidden_destination"])

            if not segments:
                return None

            # 提取预订选项
            booking_options = raw_itinerary.get("bookingOptions", {}).get("edges", [])
            booking_url = ""
            if booking_options:
                booking_url = booking_options[0].get("node", {}).get("bookingUrl", "")

            # 构建简化的航班信息
            flight_info = {
                "id": flight_id,
                "price": {
                    "amount": float(price_info.get("amount", 0)) if price_info.get("amount") else 0,
                    "currency": "CNY",  # 默认货币
                    "price_eur": float(price_eur.get("amount", 0)) if price_eur.get("amount") else 0
                },
                "duration_minutes": duration // 60 if duration else 0,  # 将秒转换为分钟
                "segments": segments,
                "travel_hack": {
                    "is_true_hidden_city": travel_hack.get("isTrueHiddenCity", False),
                    "is_virtual_interlining": travel_hack.get("isVirtualInterlining", False),
                    "is_throwaway_ticket": travel_hack.get("isThrowawayTicket", False)
                },
                "hidden_destinations": hidden_destinations,
                "booking_url": booking_url,
                "stops_count": len(segments) - 1,
                "departure_time": segments[0]["departure"]["local_time"] if segments else "",
                "arrival_time": segments[-1]["arrival"]["local_time"] if segments else "",
                "origin": segments[0]["origin"] if segments else {},
                "destination": segments[-1]["destination"] if segments else {}
            }

            # 简化隐藏城市航班日志
            if is_hidden_city and hidden_destinations:
                logger.debug(f"发现隐藏城市航班: {flight_id} - ¥{price_info.get('amount', 0)}")

            logger.debug(f"[{flight_id}] 航班解析完成")

            # 仅保存直飞航班解析结果
            if SimplifiedFlightHelpers.is_direct_flight(raw_itinerary):
                save_to_file(flight_info, f"parsed_flight_{flight_id}.json", "logs/parsed_flights")

            return flight_info

        except Exception as e:
            logger.warning(f"解析航班行程失败: {e}")
            return None

    @staticmethod
    def parse_segment(segment_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """解析航段数据"""
        try:
            source = segment_data.get("source", {})
            destination = segment_data.get("destination", {})
            carrier = segment_data.get("carrier", {})
            hidden_destination = segment_data.get("hiddenDestination", {})

            segment = {
                "id": segment_data.get("id", ""),
                "flight_number": segment_data.get("code", ""),
                "carrier": {
                    "code": carrier.get("code", ""),
                    "name": carrier.get("name", "")
                },
                "origin": {
                    "code": source.get("station", {}).get("code", ""),
                    "name": source.get("station", {}).get("name", ""),
                    "city": source.get("station", {}).get("city", {}).get("name", "")
                },
                "destination": {
                    "code": destination.get("station", {}).get("code", ""),
                    "name": destination.get("station", {}).get("name", ""),
                    "city": destination.get("station", {}).get("city", {}).get("name", "")
                },
                "departure": {
                    "local_time": source.get("localTime", ""),
                    "utc_time": source.get("utcTimeIso", "")
                },
                "arrival": {
                    "local_time": destination.get("localTime", ""),
                    "utc_time": destination.get("utcTimeIso", "")
                },
                "duration_minutes": segment_data.get("duration", 0) // 60 if segment_data.get("duration") else 0,  # 将秒转换为分钟
                "cabin_class": segment_data.get("cabinClass", "ECONOMY"),
                "hidden_destination": {
                    "code": hidden_destination.get("code", ""),
                    "name": hidden_destination.get("name", ""),
                    "city": hidden_destination.get("city", {}).get("name", ""),
                    "country": hidden_destination.get("country", {}).get("name", "")
                } if hidden_destination else None
            }

            # 简化隐藏目的地日志
            if hidden_destination:
                logger.debug(f"发现隐藏目的地航段: {segment['flight_number']} -> {hidden_destination.get('code', '')}")

            return segment

        except Exception as e:
            logger.warning(f"解析航段失败: {e}")
            return None

    @staticmethod
    def is_direct_flight(raw_itinerary: Dict[str, Any]) -> bool:
        """检查是否为直飞航班（排除隐藏城市航班）"""
        try:
            sector = raw_itinerary.get("sector", {})
            sector_segments = sector.get("sectorSegments", [])
            travel_hack = raw_itinerary.get("travelHack", {})

            # 基础检查：必须是单航段
            is_single_segment = len(sector_segments) == 1

            # 关键检查：不能是隐藏城市航班
            is_hidden_city = travel_hack.get("isTrueHiddenCity", False)

            # 添加诊断日志
            flight_id = raw_itinerary.get("id", "UNKNOWN")
            logger.info(f"🔍 【直飞验证】航班 {flight_id}:")
            logger.info(f"   - 单航段: {is_single_segment}")
            logger.info(f"   - 隐藏城市: {is_hidden_city}")
            logger.info(f"   - 最终判定: {is_single_segment and not is_hidden_city}")

            # 如果是隐藏城市航班但被误判为直飞，记录警告
            if is_single_segment and is_hidden_city:
                logger.warning(f"⚠️ 【分类错误】航班 {flight_id} 是隐藏城市航班但航段数为1，已正确排除")

            return is_single_segment and not is_hidden_city
        except Exception as e:
            logger.error(f"检查直飞航班失败: {e}")
            return False

    @staticmethod
    def is_hidden_city_flight(raw_itinerary: Dict[str, Any], target_destination: str) -> bool:
        """检查是否为隐藏城市航班（经过目标城市但不是最终目的地）"""
        try:
            # 检查travelHack字段
            travel_hack = raw_itinerary.get("travelHack", {})
            if not travel_hack.get("isTrueHiddenCity", False):
                return False

            # 检查航段是否经过目标城市
            sector = raw_itinerary.get("sector", {})
            sector_segments = sector.get("sectorSegments", [])

            for sector_segment in sector_segments:
                segment = sector_segment.get("segment", {})
                destination = segment.get("destination", {}).get("station", {})
                if destination.get("code", "").upper() == target_destination.upper():
                    return True

            return False

        except Exception as e:
            logger.warning(f"检查隐藏城市航班失败: {e}")
            return False

    @staticmethod
    def get_throwaway_destinations(origin: str, destination: str) -> List[str]:
        """获取潜在的甩尾目的地"""
        # 基于常见的航线模式定义甩尾目的地
        throwaway_map = {
            # 从中国出发的常见甩尾目的地
            "PEK": ["NRT", "ICN", "SIN", "BKK", "KUL", "MNL", "TPE"],
            "PVG": ["NRT", "ICN", "SIN", "BKK", "KUL", "MNL", "TPE"],
            "CAN": ["SIN", "BKK", "KUL", "MNL", "TPE", "ICN"],
            "SZX": ["SIN", "BKK", "KUL", "MNL", "TPE"],

            # 从其他亚洲城市出发
            "ICN": ["NRT", "SIN", "BKK", "TPE", "MNL"],
            "NRT": ["ICN", "SIN", "BKK", "TPE"],
            "SIN": ["BKK", "KUL", "MNL", "TPE", "ICN"],

            # 默认甩尾目的地
            "DEFAULT": ["NRT", "ICN", "SIN", "BKK", "KUL", "MNL", "TPE", "HKG"]
        }

        # 获取起始城市的甩尾目的地列表
        destinations = throwaway_map.get(origin.upper(), throwaway_map["DEFAULT"])

        # 过滤掉目标目的地本身
        filtered_destinations = [dest for dest in destinations if dest != destination.upper()]

        return filtered_destinations

    @staticmethod
    def deduplicate_flights(flights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重航班并按价格排序"""
        if not flights:
            return []

        # 使用航班ID去重
        seen_ids = set()
        unique_flights = []

        for flight in flights:
            flight_id = flight.get("id", "")
            if flight_id and flight_id not in seen_ids:
                seen_ids.add(flight_id)
                unique_flights.append(flight)

        # 按价格排序
        unique_flights.sort(key=lambda x: x.get("price", {}).get("amount", float('inf')))

        return unique_flights

    @staticmethod
    def get_disclaimers(include_direct: bool, include_hidden_city: bool) -> List[str]:
        """获取免责声明"""
        disclaimers = []

        if include_direct:
            disclaimers.append("直飞航班价格和时间可能会发生变化，请以实际预订为准。")

        if include_hidden_city:
            disclaimers.extend([
                "隐藏城市航班存在一定风险，包括但不限于：",
                "1. 航空公司可能取消后续航段",
                "2. 不能托运行李到最终目的地",
                "3. 违反航空公司条款可能导致账户被封",
                "4. 仅适用于单程票，不适用于往返票",
                "请谨慎使用隐藏城市航班，风险自负。"
            ])

        return disclaimers
