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
            results["disclaimers"] = SimplifiedFlightHelpers.get_disclaimers(include_direct, include_hidden_city)

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
            logger.debug(f"[{search_id}] 开始解析 {len(raw_results)} 个直飞搜索结果")

            hidden_city_found_in_direct = 0
            valid_direct_flights = 0

            for raw_itinerary in raw_results:
                try:
                    flight_id = raw_itinerary.get("id", "UNKNOWN")
                    travel_hack = raw_itinerary.get("travelHack", {})
                    is_api_hidden_city = travel_hack.get("isTrueHiddenCity", False)

                    # 记录API返回的异常情况
                    if is_api_hidden_city:
                        hidden_city_found_in_direct += 1
                        logger.warning(f"[{search_id}] 直飞搜索中发现隐藏城市航班: {flight_id}")

                    # 检查是否为直飞（现在会正确排除隐藏城市航班）
                    if SimplifiedFlightHelpers.is_direct_flight(raw_itinerary):
                        flight = await SimplifiedFlightHelpers.parse_flight_itinerary(raw_itinerary, is_one_way)
                        if flight:
                            flight["is_hidden_city"] = False
                            flight["flight_type"] = "direct"
                            flights.append(flight)
                            valid_direct_flights += 1
                            logger.debug(f"[{search_id}] 添加直飞航班: {flight_id}")

                except Exception as e:
                    logger.warning(f"[{search_id}] 解析直飞航班失败: {e}")
                    continue

            # 简化汇总信息
            logger.debug(f"[{search_id}] 直飞搜索完成: {valid_direct_flights}/{len(raw_results)} 有效")
            if hidden_city_found_in_direct > 0:
                logger.warning(f"[{search_id}] 直飞搜索返回了 {hidden_city_found_in_direct} 个隐藏城市航班")

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

            # 1. 先搜索直接目的地的隐藏城市航班
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

            logger.debug(f"[{search_id}] 甩尾搜索完成: {len(unique_flights)} 个有效航班")

            return unique_flights

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
            variables["filter"]["maxStopsCount"] = 0  # 与验证查询一致
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
                        flight = await SimplifiedFlightHelpers.parse_flight_itinerary(raw_itinerary, is_one_way)
                        if flight:
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

                # 构建搜索变量 - 修复：搜索A→C普通中转航班，筛选经过B的航班
                variables = SimplifiedFlightHelpers.build_graphql_variables(temp_request, is_one_way)
                variables["filter"]["maxStopsCount"] = 3  # 允许中转以找到甩尾票
                # 🔧 关键修复：甩尾搜索时禁用隐藏城市功能，只搜索普通中转航班
                variables["filter"]["enableTrueHiddenCity"] = False  # 禁用隐藏城市
                variables["filter"]["enableSelfTransfer"] = True     # 允许自助中转
                variables["filter"]["enableThrowAwayTicketing"] = False  # 禁用甩尾票标记

                # 执行搜索
                raw_results = await SimplifiedFlightHelpers.execute_graphql_search(
                    variables, headers, f"{search_id}_throwaway_{throwaway_dest}",
                    self.base_url, self.timeout
                )

                # 解析结果并筛选出经过目标城市的航班
                valid_throwaway_count = 0
                for raw_itinerary in raw_results:
                    try:
                        flight = await SimplifiedFlightHelpers.parse_flight_itinerary(raw_itinerary, is_one_way)
                        if flight:
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
        segments = flight.get("segments", [])
        if not segments:
            return False

        target_city_upper = target_city.upper()
        final_dest_upper = final_dest.upper()

        # 构建航段路径用于调试
        route_codes = []
        for segment in segments:
            route_codes.append(segment.get("origin", {}).get("code", ""))
        if segments:
            route_codes.append(segments[-1].get("destination", {}).get("code", ""))
        route_path = " -> ".join(route_codes)

        # 检查是否已经被API标记为隐藏城市航班
        travel_hack = flight.get("travel_hack", {})
        is_api_marked = travel_hack.get("is_true_hidden_city", False)

        # 核心验证逻辑：检查航段路径
        passes_through_target = False
        ends_at_throwaway = False
        target_segment_index = -1

        # 遍历所有航段，寻找经过目标城市的中转
        for i, segment in enumerate(segments):
            arrival_airport = segment.get("destination", {}).get("code", "").upper()

            # 检查是否经过目标城市（必须不是最后一个航段，因为我们要在目标城市下机）
            if arrival_airport == target_city_upper and i < len(segments) - 1:
                passes_through_target = True
                target_segment_index = i
                logger.debug(f"  找到目标城市中转: 第{i+1}段到达 {target_city_upper}")
                break

        # 检查最终目的地是否为甩尾目的地
        if segments:
            final_segment = segments[-1]
            final_arrival = final_segment.get("destination", {}).get("code", "").upper()
            ends_at_throwaway = (final_arrival == final_dest_upper)

        # 甩尾航班必须满足两个条件：
        # 1. 经过目标城市作为中转站（不是最终目的地）
        # 2. 最终到达甩尾目的地
        is_valid_throwaway = passes_through_target and ends_at_throwaway

        # 如果API已标记为隐藏城市，需要进一步验证是否符合我们的甩尾逻辑
        if is_api_marked:
            # API标记的隐藏城市航班，但我们还需要验证是否经过目标城市
            is_valid = is_valid_throwaway
        else:
            # 非API标记的航班，严格按照甩尾逻辑验证
            is_valid = is_valid_throwaway

        # 简化调试日志
        logger.debug(f"甩尾航班验证: {flight.get('id', 'UNKNOWN')} - {route_path} - 结果: {is_valid}")

        return is_valid