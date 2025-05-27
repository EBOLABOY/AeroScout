"""
简化的航班搜索服务
基于Kiwi.com GraphQL API实现直飞和隐藏城市航班搜索
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import httpx

from app.core.config import settings
from app.core import dynamic_fetcher
from app.apis.v1.schemas import FlightSearchRequest, FlightItinerary, FlightSegment
from app.services.simplified_flight_helpers import SimplifiedFlightHelpers

logger = logging.getLogger(__name__)

class SimplifiedFlightService:
    """简化的航班搜索服务"""

    def __init__(self):
        self.base_url = "https://api.skypicker.com/umbrella/v2/graphql"
        self.timeout = 30.0
        self._hidden_city_flights_from_direct = []  # 存储从直飞搜索中发现的隐藏城市航班

    async def search_flights(
        self,
        request: FlightSearchRequest,
        include_direct: bool = True,
        include_hidden_city: bool = True
    ) -> Dict[str, Any]:
        """
        执行航班搜索

        Args:
            request: 搜索请求参数
            include_direct: 是否包含直飞航班
            include_hidden_city: 是否包含隐藏城市航班

        Returns:
            包含直飞和隐藏城市航班的搜索结果
        """
        start_time = time.time()
        search_id = f"simple_{int(time.time())}"

        # 重置实例变量
        self._hidden_city_flights_from_direct = []

        logger.info(f"[{search_id}] 开始简化航班搜索")
        logger.info(f"[{search_id}] 搜索参数: {request.origin_iata} -> {request.destination_iata}")
        logger.info(f"[{search_id}] 出发日期: {request.departure_date_from}")
        logger.info(f"[{search_id}] 包含直飞: {include_direct}, 包含隐藏城市: {include_hidden_city}")

        results = {
            "search_id": search_id,
            "direct_flights": [],
            "hidden_city_flights": [],
            "search_time_ms": 0,
            "disclaimers": []
        }

        try:
            # 获取Kiwi headers
            kiwi_headers = await self._get_kiwi_headers()

            # 构建GraphQL查询
            is_one_way = request.return_date_from is None

            # 搜索直飞航班
            if include_direct:
                logger.info(f"[{search_id}] 搜索直飞航班")
                direct_flights = await self._search_direct_flights(
                    request, kiwi_headers, is_one_way, search_id
                )
                results["direct_flights"] = direct_flights
                logger.info(f"[{search_id}] 找到 {len(direct_flights)} 个直飞航班")

            # 搜索隐藏城市航班
            if include_hidden_city:
                logger.info(f"[{search_id}] 搜索隐藏城市航班")
                hidden_flights = await self._search_hidden_city_flights(
                    request, kiwi_headers, is_one_way, search_id
                )
                results["hidden_city_flights"] = hidden_flights
                logger.info(f"[{search_id}] 找到 {len(hidden_flights)} 个隐藏城市航班")

                # 汇总显示隐藏航班信息
                if hidden_flights:
                    logger.info(f"🎯 【隐藏城市航班汇总】共找到 {len(hidden_flights)} 个隐藏航班:")
                    for i, flight in enumerate(hidden_flights[:5], 1):  # 显示前5个
                        price = flight.get("price", {}).get("amount", 0)
                        origin = flight.get("origin", {}).get("code", "")
                        destination = flight.get("destination", {}).get("code", "")
                        hidden_dests = flight.get("hidden_destinations", [])
                        hidden_info = ", ".join([f"{hd.get('code', '')}-{hd.get('name', '')}" for hd in hidden_dests]) if hidden_dests else "无"
                        logger.info(f"   {i}. ¥{price} | {origin}→{destination} | 隐藏目的地: {hidden_info}")
                else:
                    logger.info(f"❌ 未找到任何隐藏城市航班")

            # 设置免责声明
            results["disclaimers"] = SimplifiedFlightHelpers.get_disclaimer_flags(include_direct, include_hidden_city)

            execution_time = int((time.time() - start_time) * 1000)
            results["search_time_ms"] = execution_time

            # 简化日志输出 - 只记录关键信息
            logger.debug(f"[{search_id}] 搜索完成: 直飞 {len(results.get('direct_flights', []))}, 甩尾 {len(results.get('hidden_city_flights', []))}, 耗时: {execution_time}ms")
            return results

        except Exception as e:
            logger.error(f"[{search_id}] 搜索失败: {str(e)}", exc_info=True)
            execution_time = int((time.time() - start_time) * 1000)
            results["search_time_ms"] = execution_time
            results["error"] = str(e)
            return results

    async def _get_kiwi_headers(self) -> Dict[str, str]:
        """获取Kiwi API headers"""
        try:
            return await dynamic_fetcher.get_effective_kiwi_headers()
        except Exception as e:
            logger.error(f"获取Kiwi headers失败: {e}")
            # 返回基础headers
            return {
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

    async def _search_direct_flights(
        self,
        request: FlightSearchRequest,
        headers: Dict[str, str],
        is_one_way: bool,
        search_id: str
    ) -> List[Dict[str, Any]]:
        """搜索直飞航班"""
        try:
            # 构建GraphQL变量（限制为直飞）
            variables = SimplifiedFlightHelpers.build_graphql_variables(request, is_one_way)
            variables["filter"]["maxStopsCount"] = 0  # 直飞

            # 执行搜索
            raw_results = await SimplifiedFlightHelpers.execute_graphql_search(
                variables, headers, search_id, self.base_url, self.timeout
            )

            # 解析结果
            flights = []
            hidden_city_flights_from_direct = []  # 收集从直飞搜索中发现的隐藏城市航班
            logger.debug(f"[{search_id}] 开始解析 {len(raw_results)} 个直飞搜索结果")

            hidden_city_found_in_direct = 0
            valid_direct_flights = 0

            for raw_itinerary in raw_results:
                try:
                    flight_id = raw_itinerary.get("id", "UNKNOWN")
                    travel_hack = raw_itinerary.get("travelHack", {})
                    is_api_hidden_city = travel_hack.get("isTrueHiddenCity", False)

                    # 如果是隐藏城市航班，转移到隐藏城市列表
                    if is_api_hidden_city:
                        hidden_city_found_in_direct += 1
                        logger.warning(f"[{search_id}] 直飞搜索中发现隐藏城市航班，转移到隐藏城市列表: {flight_id}")

                        flight = await SimplifiedFlightHelpers.parse_flight_itinerary(raw_itinerary, request.preferred_currency)
                        if flight:
                            # 标记这个航班来自主要目的地搜索
                            flight["_internal_debug_markers"]["search_type"] = "main_destination"
                            flight["is_hidden_city"] = True
                            flight["flight_type"] = "hidden_city"
                            hidden_city_flights_from_direct.append(flight)
                            logger.debug(f"[{search_id}] 转移隐藏城市航班: {flight_id}")

                    # 解析航班并检查是否为直飞
                    else:
                        flight = await SimplifiedFlightHelpers.parse_flight_itinerary(raw_itinerary, request.preferred_currency)
                        if flight:
                            # 标记这个航班来自主要目的地搜索
                            flight["_internal_debug_markers"]["search_type"] = "main_destination"

                            # 检查是否为真正的直飞航班
                            num_segments = len(flight["all_segments_on_ticket"])
                            ticketed_dest = flight["ticketed_final_destination_airport"]["code"]
                            target_dest = request.destination_iata.upper()

                            if (num_segments == 1 and
                                not flight["api_travel_hack_info"]["is_true_hidden_city"] and
                                ticketed_dest == target_dest):
                                flight["is_hidden_city"] = False
                                flight["flight_type"] = "direct"
                                flight["display_flight_type"] = "直达"  # 设置显示类型
                                flights.append(flight)
                                valid_direct_flights += 1
                                logger.debug(f"[{search_id}] 添加直飞航班: {flight_id}")

                except Exception as e:
                    logger.warning(f"[{search_id}] 解析直飞航班失败: {e}")
                    continue

            # 将发现的隐藏城市航班存储到实例变量中，供隐藏城市搜索使用
            self._hidden_city_flights_from_direct = hidden_city_flights_from_direct

            # 简化汇总信息
            logger.debug(f"[{search_id}] 直飞搜索完成: {valid_direct_flights}/{len(raw_results)} 有效")
            if hidden_city_found_in_direct > 0:
                logger.warning(f"[{search_id}] 直飞搜索发现 {hidden_city_found_in_direct} 个隐藏城市航班，已转移到隐藏城市列表")

            return flights

        except Exception as e:
            logger.error(f"[{search_id}] 直飞搜索失败: {e}")
            return []

    async def _search_hidden_city_flights(
        self,
        request: FlightSearchRequest,
        headers: Dict[str, str],
        is_one_way: bool,
        search_id: str
    ) -> List[Dict[str, Any]]:
        """搜索隐藏城市航班（包含甩尾策略）"""
        try:
            logger.debug(f"[{search_id}] 开始甩尾票搜索: {request.origin_iata} -> {request.destination_iata}")

            # 判断目的地是否为国内
            is_destination_domestic = self._is_domestic_cn_airport(request.destination_iata)

            # 获取甩尾目的地列表
            throwaway_destinations = self._get_throwaway_destinations(
                request.origin_iata, request.destination_iata, is_destination_domestic
            )
            logger.debug(f"[{search_id}] 甩尾目的地: {len(throwaway_destinations)} 个")

            all_hidden_flights = []

            # 0. 首先添加从直飞搜索中发现的隐藏城市航班
            if hasattr(self, '_hidden_city_flights_from_direct') and self._hidden_city_flights_from_direct:
                all_hidden_flights.extend(self._hidden_city_flights_from_direct)
                logger.debug(f"[{search_id}] 添加从直飞搜索中发现的 {len(self._hidden_city_flights_from_direct)} 个隐藏城市航班")

            # 1. 搜索直接目的地的隐藏城市航班
            direct_hidden_flights = await self._search_direct_hidden_city(
                request, headers, is_one_way, search_id
            )
            all_hidden_flights.extend(direct_hidden_flights)

            # 2. 搜索甩尾目的地
            if throwaway_destinations:
                throwaway_flights = await self._search_throwaway_destinations(
                    request, headers, is_one_way, search_id, throwaway_destinations
                )
                all_hidden_flights.extend(throwaway_flights)

            # 去重并按价格排序
            unique_flights = SimplifiedFlightHelpers.deduplicate_flights(all_hidden_flights)

            # 使用新的分类逻辑重新分类隐藏城市航班
            classified_hidden_flights = self._classify_hidden_city_flights(unique_flights, request.destination_iata.upper(), search_id)

            logger.debug(f"[{search_id}] 甩尾搜索完成: {len(classified_hidden_flights)} 个有效航班")

            return classified_hidden_flights

        except Exception as e:
            logger.error(f"[{search_id}] 隐藏城市搜索失败: {e}")
            return []

    def _is_domestic_cn_airport(self, airport_code: str) -> bool:
        """判断机场代码是否为中国大陆国内机场"""
        # 处理可能的格式：Station:airport:PEK 或直接 PEK
        code_to_check = airport_code.upper()
        if code_to_check.startswith("STATION:AIRPORT:"):
            code_to_check = code_to_check.split(':')[-1]

        # 中国大陆主要机场代码集合
        domestic_cn_airports = {
            # 一线城市主要机场
            "PEK", "PKX",  # 北京
            "PVG", "SHA",  # 上海
            "CAN",         # 广州
            "SZX",         # 深圳

            # 主要枢纽城市
            "CTU",         # 成都
            "CKG",         # 重庆
            "XIY",         # 西安
            "KMG",         # 昆明
            "WUH",         # 武汉
            "CSX",         # 长沙
            "NKG",         # 南京
            "HGH",         # 杭州
            "XMN",         # 厦门
            "FOC",         # 福州

            # 其他重要城市
            "TSN",         # 天津
            "SHE",         # 沈阳
            "HRB",         # 哈尔滨
            "DLC",         # 大连
            "TAO",         # 青岛
            "CGO",         # 郑州
            "HFE",         # 合肥
            "TYN",         # 太原
            "KWE",         # 贵阳
            "NNG",         # 南宁
            "URC",         # 乌鲁木齐
            "SYX",         # 三亚
            "HAK",         # 海口
        }

        return code_to_check in domestic_cn_airports

    def _get_throwaway_destinations(self, origin: str, destination: str, is_destination_domestic: bool) -> List[str]:
        """获取甩尾目的地列表"""
        # 国内主要甩尾目的地（按重要性排序）
        domestic_throwaway_destinations = [
            'PEK', 'PKX',  # 北京
            'PVG', 'SHA',  # 上海
            'CAN',         # 广州
            'SZX',         # 深圳
            'CTU',         # 成都
            'CKG',         # 重庆
            'XIY',         # 西安
            'KMG',         # 昆明
            'WUH',         # 武汉
            'CSX',         # 长沙
            'NKG',         # 南京
            'HGH',         # 杭州
            'XMN',         # 厦门
            'TSN',         # 天津
            'TAO',         # 青岛
            'DLC',         # 大连
        ]

        # 国际主要甩尾目的地
        international_throwaway_destinations = [
            'HKG', 'TPE', 'NRT', 'ICN', 'SIN', 'BKK', 'KUL', 'MNL',  # 亚洲
            'FRA', 'AMS', 'CDG', 'LHR', 'FCO', 'VIE', 'ZUR',         # 欧洲
            'LAX', 'SFO', 'JFK', 'ORD', 'DFW', 'YVR', 'YYZ'          # 北美
        ]

        origin_upper = origin.upper()
        destination_upper = destination.upper()

        if is_destination_domestic:
            # 国内目的地：优先使用国内其他枢纽作为甩尾目的地
            throwaway_list = domestic_throwaway_destinations.copy()
            # 添加少量亚洲城市作为备选
            throwaway_list.extend(['HKG', 'TPE', 'NRT'])
        else:
            # 国际目的地：使用国际枢纽
            throwaway_list = international_throwaway_destinations.copy()

        # 过滤掉起始地和目的地
        filtered_list = [dest for dest in throwaway_list
                        if dest != origin_upper and dest != destination_upper]

        # 限制搜索数量以控制API调用（最多6个甩尾目的地）
        return filtered_list[:6]

    async def _search_direct_hidden_city(
        self,
        request: FlightSearchRequest,
        headers: Dict[str, str],
        is_one_way: bool,
        search_id: str
    ) -> List[Dict[str, Any]]:
        """搜索直接目的地的隐藏城市航班"""
        try:
            # 构建搜索变量（直接搜索到目标目的地，启用隐藏城市功能）
            variables = SimplifiedFlightHelpers.build_graphql_variables(request, is_one_way)
            variables["filter"]["maxStopsCount"] = 0  # 搜索直接目的地的隐藏城市航班
            variables["filter"]["enableTrueHiddenCity"] = True
            variables["filter"]["enableSelfTransfer"] = True
            variables["filter"]["enableThrowAwayTicketing"] = True

            # 执行搜索
            raw_results = await SimplifiedFlightHelpers.execute_graphql_search(
                variables, headers, f"{search_id}_direct_hidden", self.base_url, self.timeout
            )

            hidden_flights = []

            # 筛选出真正的隐藏城市航班
            for raw_itinerary in raw_results:
                try:
                    travel_hack = raw_itinerary.get("travelHack", {})
                    is_true_hidden_city = travel_hack.get("isTrueHiddenCity", False)

                    if is_true_hidden_city:
                        flight = await SimplifiedFlightHelpers.parse_flight_itinerary(raw_itinerary, request.preferred_currency)
                        if flight:
                            # 标记这个航班来自主要目的地搜索
                            flight["_internal_debug_markers"]["search_type"] = "main_destination"
                            flight["is_hidden_city"] = True
                            flight["flight_type"] = "hidden_city"
                            hidden_flights.append(flight)

                except Exception as e:
                    logger.warning(f"[{search_id}] 解析直接隐藏城市航班失败: {e}")
                    continue

            return hidden_flights

        except Exception as e:
            logger.error(f"[{search_id}] 直接隐藏城市搜索失败: {e}")
            return []

    async def _search_throwaway_destinations(
        self,
        request: FlightSearchRequest,
        headers: Dict[str, str],
        is_one_way: bool,
        search_id: str,
        throwaway_destinations: List[str]
    ) -> List[Dict[str, Any]]:
        """搜索甩尾目的地"""
        all_throwaway_flights = []
        target_destination = request.destination_iata.upper()

        for throwaway_dest in throwaway_destinations:
            try:
                logger.debug(f"[{search_id}] 搜索甩尾路线: {request.origin_iata} -> {throwaway_dest}")

                # 创建临时请求，目的地设为甩尾城市
                temp_request = FlightSearchRequest(
                    origin_iata=request.origin_iata,
                    destination_iata=throwaway_dest,  # 使用甩尾目的地
                    departure_date_from=request.departure_date_from,
                    departure_date_to=request.departure_date_to,
                    return_date_from=request.return_date_from,
                    return_date_to=request.return_date_to,
                    cabin_class=request.cabin_class,
                    adults=request.adults,
                    preferred_currency=request.preferred_currency,
                    market=request.market
                )

                # 构建搜索变量 - 使用统一的GraphQL变量构建方法
                variables = SimplifiedFlightHelpers.build_graphql_variables(temp_request, is_one_way)
                # 确保允许中转和隐藏城市搜索
                variables["filter"]["maxStopsCount"] = 3
                variables["filter"]["enableTrueHiddenCity"] = True
                variables["filter"]["enableSelfTransfer"] = True
                variables["filter"]["enableThrowAwayTicketing"] = True

                # 执行搜索 - 使用统一的GraphQL搜索方法
                raw_results = await SimplifiedFlightHelpers.execute_graphql_search(
                    variables, headers, f"{search_id}_throwaway_{throwaway_dest}",
                    self.base_url, self.timeout
                )

                # 解析结果并筛选出经过目标城市的航班
                valid_throwaway_count = 0
                for raw_itinerary in raw_results:
                    try:
                        # 使用统一的航班解析方法
                        flight = await SimplifiedFlightHelpers.parse_flight_itinerary(raw_itinerary, request.preferred_currency)
                        if flight:
                            # 标记这个航班来自甩尾搜索
                            flight["_internal_debug_markers"]["search_type"] = "throwaway_search"
                            flight["_internal_debug_markers"]["throwaway_ticketed_dest"] = throwaway_dest

                            # 验证是否为有效的甩尾航班
                            is_valid = self._is_valid_throwaway_flight(flight, target_destination, throwaway_dest)

                            if is_valid:
                                flight["is_hidden_city"] = True
                                flight["flight_type"] = "throwaway"
                                flight["throwaway_destination"] = throwaway_dest
                                all_throwaway_flights.append(flight)
                                valid_throwaway_count += 1

                                logger.debug(f"[{search_id}] 发现甩尾航班: {flight['id']}")

                    except Exception as e:
                        logger.warning(f"[{search_id}] 解析甩尾航班失败: {e}")
                        continue

                logger.debug(f"[{search_id}] 甩尾目的地 {throwaway_dest}: {valid_throwaway_count}/{len(raw_results)} 有效")

            except Exception as e:
                logger.warning(f"[{search_id}] 搜索甩尾目的地 {throwaway_dest} 失败: {e}")
                continue

        return all_throwaway_flights

    def _is_valid_throwaway_flight(self, flight: Dict[str, Any], target_city: str, final_dest: str) -> bool:
        """验证是否为有效的甩尾航班 - 必须经过目标城市作为中转站"""
        segments = flight.get("all_segments_on_ticket", [])
        if not segments:
            logger.debug(f"甩尾航班验证失败: {flight.get('id', 'UNKNOWN')} - 没有航段数据")
            return False

        target_city_upper = target_city.upper()
        final_dest_upper = final_dest.upper()

        # 构建航段路径用于调试
        route_codes = []
        for segment in segments:
            route_codes.append(segment.get("origin", {}).get("code", ""))
        if segments:
            route_codes.append(segments[-1].get("ticketed_destination", {}).get("code", ""))
        route_path = " -> ".join(route_codes)

        # 检查是否已经被API标记为隐藏城市航班
        travel_hack = flight.get("api_travel_hack_info", {})
        is_api_marked = travel_hack.get("is_true_hidden_city", False)

        # 核心验证逻辑：检查航段路径
        passes_through_target = False
        ends_at_throwaway = False

        # 遍历所有航段，寻找经过目标城市的中转
        for i, segment in enumerate(segments):
            arrival_airport = segment.get("ticketed_destination", {}).get("code", "").upper()

            # 检查是否经过目标城市（必须不是最后一个航段，因为我们要在目标城市下机）
            if arrival_airport == target_city_upper and i < len(segments) - 1:
                passes_through_target = True
                logger.debug(f"  找到目标城市中转: 第{i+1}段到达 {target_city_upper}")
                break

        # 检查最终目的地是否为甩尾目的地
        if segments:
            final_segment = segments[-1]
            final_arrival = final_segment.get("ticketed_destination", {}).get("code", "").upper()
            ends_at_throwaway = (final_arrival == final_dest_upper)

        # 甩尾航班必须满足两个条件：
        # 1. 经过目标城市作为中转站（不是最终目的地）
        # 2. 最终到达甩尾目的地
        is_valid_throwaway = passes_through_target and ends_at_throwaway

        # 简化调试日志
        logger.debug(f"甩尾航班验证: {flight.get('id', 'UNKNOWN')} - {route_path} - 经过目标: {passes_through_target}, 到达甩尾: {ends_at_throwaway}, API标记: {is_api_marked}, 结果: {is_valid_throwaway}")

        return is_valid_throwaway

    def _classify_hidden_city_flights(self, flights: List[Dict[str, Any]], target_destination: str, search_id: str) -> List[Dict[str, Any]]:
        """
        使用精确的分类逻辑重新分类隐藏城市航班
        区分API标记的隐藏城市和构造的隐藏城市
        """
        classified_flights = []
        target_destination_upper = target_destination.upper()

        for flight in flights:
            is_api_hc_flag = flight["api_travel_hack_info"]["is_true_hidden_city"]
            num_ticket_segments = len(flight["all_segments_on_ticket"])
            search_source_type = flight["_internal_debug_markers"].get("search_type")

            logger.debug(f"[{search_id}] 分类航班 {flight['id']}: API标记={is_api_hc_flag}, 航段数={num_ticket_segments}, 来源={search_source_type}")

            # 类别B: API标记的隐藏城市 (主要来自主要目的地搜索)
            if is_api_hc_flag and search_source_type == "main_destination":
                classified_flight = self._classify_api_marked_hidden_city(flight, target_destination_upper, search_id)
                if classified_flight:
                    classified_flights.append(classified_flight)
                    continue

            # 类别C: 构造的隐藏城市 (来自甩尾目的地搜索)
            if search_source_type == "throwaway_search":
                classified_flight = self._classify_constructed_hidden_city(flight, target_destination_upper, search_id)
                if classified_flight:
                    classified_flights.append(classified_flight)
                    continue

            # 如果都不匹配，保留原始分类
            logger.debug(f"[{search_id}] 航班 {flight['id']} 未匹配任何隐藏城市分类，保留原始分类")
            classified_flights.append(flight)

        return classified_flights

    def _classify_api_marked_hidden_city(self, flight: Dict[str, Any], target_destination: str, search_id: str) -> Optional[Dict[str, Any]]:
        """
        分类API标记的隐藏城市航班
        用户必须能够在原始目标城市实际下机
        """
        can_drop_off_at_target = False
        user_segments_for_hc = []
        user_layovers_for_hc = []
        arrival_at_target_local_for_hc = None

        for seg_idx, segment in enumerate(flight["all_segments_on_ticket"]):
            user_segments_for_hc.append(segment)
            if seg_idx > 0:
                if flight["all_layovers_on_ticket"] and (seg_idx - 1) < len(flight["all_layovers_on_ticket"]):
                    user_layovers_for_hc.append(flight["all_layovers_on_ticket"][seg_idx - 1])

            if segment["ticketed_destination"]["code"] == target_destination:
                # 检查是否可以在这个目标城市下机
                # 条件：不是票面行程的最后一个航段，或者是单段隐藏城市票
                num_segments = len(flight["all_segments_on_ticket"])
                is_final_destination = flight["ticketed_final_destination_airport"]["code"] == target_destination
                has_hidden_destinations = bool(flight["api_travel_hack_info"]["api_hidden_destinations_on_route"])

                if not is_final_destination or (num_segments == 1 and has_hidden_destinations):
                    can_drop_off_at_target = True
                    arrival_at_target_local_for_hc = segment["arrival"]["local_time"]

                    # 设置用户感知的行程信息
                    flight["display_flight_type"] = "隐藏城市 (API标记)"
                    flight["user_perceived_destination_airport"] = segment["ticketed_destination"]
                    flight["user_journey_segments_to_display"] = list(user_segments_for_hc)
                    flight["user_journey_layovers_to_display"] = list(user_layovers_for_hc)
                    flight["user_journey_arrival_datetime_local"] = arrival_at_target_local_for_hc

                    # 计算用户行程时长
                    dep_dt_utc_str = flight["all_segments_on_ticket"][0]["departure"].get("utc_time")
                    arr_dt_utc_str = segment["arrival"].get("utc_time")
                    if dep_dt_utc_str and arr_dt_utc_str:
                        dep_dt = SimplifiedFlightHelpers._parse_datetime_flexible(dep_dt_utc_str)
                        arr_dt = SimplifiedFlightHelpers._parse_datetime_flexible(arr_dt_utc_str)
                        if dep_dt and arr_dt:
                            flight["user_journey_duration_minutes"] = int((arr_dt - dep_dt).total_seconds() / 60)
                        else:
                            flight["user_journey_duration_minutes"] = -1

                    # 添加用户提醒
                    flight["user_alert_notes"].append(f"需在'{target_destination}'提前下机。")
                    if not is_final_destination:
                        flight["user_alert_notes"].append(f"票面终点'{flight['ticketed_final_destination_airport']['code']}'。")

                    logger.debug(f"[{search_id}] API标记隐藏城市航班分类成功: {flight['id']}")
                    break

        return flight if can_drop_off_at_target else None

    def _classify_constructed_hidden_city(self, flight: Dict[str, Any], target_destination: str, search_id: str) -> Optional[Dict[str, Any]]:
        """
        分类构造的隐藏城市航班
        检查中转点是否为目标城市
        """
        can_construct_hc_via_layover = False
        user_segments_for_constructed_hc = []
        user_layovers_for_constructed_hc = []
        arrival_at_target_local_for_constructed_hc = None

        # 遍历航段，寻找在中转点(即上一个航段的目的地)为 target_destination 的情况
        for seg_idx, segment in enumerate(flight["all_segments_on_ticket"]):
            # 我们关心的是在 segment[seg_idx-1] 的目的地（即中转点）下机
            if seg_idx > 0:  # 至少要有前一个航段
                prev_segment = flight["all_segments_on_ticket"][seg_idx - 1]
                if prev_segment["ticketed_destination"]["code"] == target_destination:
                    # 找到了一个中转点是我们的目标城市
                    can_construct_hc_via_layover = True
                    arrival_at_target_local_for_constructed_hc = prev_segment["arrival"]["local_time"]

                    # 用户行程只包含到这个中转点为止的航段
                    user_segments_for_constructed_hc = flight["all_segments_on_ticket"][:seg_idx]
                    # 用户行程的中转只包含这些航段之间的中转
                    user_layovers_for_constructed_hc = flight["all_layovers_on_ticket"][:seg_idx-1] if seg_idx > 1 else []

                    flight["display_flight_type"] = "隐藏城市 (中转即达)"
                    flight["user_perceived_destination_airport"] = prev_segment["ticketed_destination"]
                    flight["user_journey_segments_to_display"] = list(user_segments_for_constructed_hc)
                    flight["user_journey_layovers_to_display"] = list(user_layovers_for_constructed_hc)
                    flight["user_journey_arrival_datetime_local"] = arrival_at_target_local_for_constructed_hc

                    # 计算构造隐藏城市的用户行程时长
                    dep_dt_utc_str = flight["all_segments_on_ticket"][0]["departure"].get("utc_time")
                    arr_dt_utc_str = prev_segment["arrival"].get("utc_time")
                    if dep_dt_utc_str and arr_dt_utc_str:
                        dep_dt = SimplifiedFlightHelpers._parse_datetime_flexible(dep_dt_utc_str)
                        arr_dt = SimplifiedFlightHelpers._parse_datetime_flexible(arr_dt_utc_str)
                        if dep_dt and arr_dt:
                            flight["user_journey_duration_minutes"] = int((arr_dt - dep_dt).total_seconds() / 60)
                        else:
                            flight["user_journey_duration_minutes"] = -1

                    # 添加构造隐藏城市的用户提醒
                    flight["user_alert_notes"].append(f"需在中转站'{target_destination}'提前结束行程。")
                    flight["user_alert_notes"].append(f"票面终点'{flight['ticketed_final_destination_airport']['code']}'。")

                    logger.debug(f"[{search_id}] 构造隐藏城市航班分类成功: {flight['id']}")
                    break  # 找到构造点
            if can_construct_hc_via_layover:
                break  # 跳出外层循环

        return flight if can_construct_hc_via_layover else None