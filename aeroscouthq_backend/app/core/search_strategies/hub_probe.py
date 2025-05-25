"""
中转城市探测策略 - 第二阶段搜索
"""

import time
from typing import List, Dict, Any, Optional

from .base import SearchStrategy, SearchContext, SearchResult, SearchResultStatus
from app.apis.v1.schemas.flights_v2 import (
    EnhancedFlightItinerary,
    SearchPhase,
    HubSelectionStrategy,
    PhaseTwoSearchRequest
)
from app.apis.v1.schemas import FlightItinerary

# 导入现有的任务函数
from app.core.tasks import (
    _task_build_kiwi_variables,
    _task_run_search_with_retry,
    _task_parse_kiwi_itinerary
)

class HubProbeStrategy(SearchStrategy):
    """中转城市探测策略"""

    def __init__(self):
        super().__init__("hub_probe")
        # 主要国家/地区的枢纽机场映射
        self.hub_mappings = {
            # 中国主要枢纽
            'china': [
                {'iata': 'PEK', 'name': '北京首都国际机场', 'city': '北京'},
                {'iata': 'PVG', 'name': '上海浦东国际机场', 'city': '上海'},
                {'iata': 'CAN', 'name': '广州白云国际机场', 'city': '广州'},
                {'iata': 'SZX', 'name': '深圳宝安国际机场', 'city': '深圳'},
                {'iata': 'CTU', 'name': '成都天府国际机场', 'city': '成都'},
                {'iata': 'WUH', 'name': '武汉天河国际机场', 'city': '武汉'},
                {'iata': 'XMN', 'name': '厦门高崎国际机场', 'city': '厦门'},
            ],
            # 亚洲主要枢纽
            'asia': [
                {'iata': 'HKG', 'name': '香港国际机场', 'city': '香港'},
                {'iata': 'NRT', 'name': '东京成田国际机场', 'city': '东京'},
                {'iata': 'ICN', 'name': '首尔仁川国际机场', 'city': '首尔'},
                {'iata': 'SIN', 'name': '新加坡樟宜机场', 'city': '新加坡'},
                {'iata': 'BKK', 'name': '曼谷素万那普机场', 'city': '曼谷'},
                {'iata': 'DXB', 'name': '迪拜国际机场', 'city': '迪拜'},
            ],
            # 欧洲主要枢纽
            'europe': [
                {'iata': 'FRA', 'name': '法兰克福机场', 'city': '法兰克福'},
                {'iata': 'AMS', 'name': '阿姆斯特丹史基浦机场', 'city': '阿姆斯特丹'},
                {'iata': 'LHR', 'name': '伦敦希思罗机场', 'city': '伦敦'},
                {'iata': 'CDG', 'name': '巴黎戴高乐机场', 'city': '巴黎'},
                {'iata': 'VIE', 'name': '维也纳国际机场', 'city': '维也纳'},
            ],
            # 北美主要枢纽
            'north_america': [
                {'iata': 'LAX', 'name': '洛杉矶国际机场', 'city': '洛杉矶'},
                {'iata': 'SFO', 'name': '旧金山国际机场', 'city': '旧金山'},
                {'iata': 'JFK', 'name': '肯尼迪国际机场', 'city': '纽约'},
                {'iata': 'ORD', 'name': '芝加哥奥黑尔机场', 'city': '芝加哥'},
                {'iata': 'YVR', 'name': '温哥华国际机场', 'city': '温哥华'},
            ]
        }

    def can_execute(self, context: SearchContext) -> bool:
        """检查是否可以执行中转城市探测"""
        # 只在第二阶段执行
        return context.phase == SearchPhase.PHASE_TWO

    async def execute(self, context: SearchContext) -> SearchResult:
        """执行中转城市探测搜索"""
        start_time = time.time()
        await self._log_execution_start(context)

        # 验证请求参数
        if not await self._validate_request(context):
            return SearchResult(
                status=SearchResultStatus.FAILED,
                flights=[],
                execution_time_ms=int((time.time() - start_time) * 1000),
                error_message="请求参数验证失败"
            )

        try:
            # 获取第二阶段特定配置
            phase_two_config = self._extract_phase_two_config(context)

            # 获取要探测的中转城市列表
            hubs_to_probe = self._get_hubs_to_probe(context, phase_two_config)
            if not hubs_to_probe:
                return SearchResult(
                    status=SearchResultStatus.SUCCESS,
                    flights=[],
                    execution_time_ms=int((time.time() - start_time) * 1000),
                    metadata={"message": "未找到合适的中转城市"},
                    disclaimers=["当前路线暂无中转城市优惠"]
                )

            is_one_way = context.request.return_date_from is None
            all_hub_flights = []
            hub_analysis = {}

            # 对每个中转城市进行探测
            for hub_info in hubs_to_probe:
                hub_iata = hub_info['iata']
                hub_results = await self._probe_single_hub(
                    context, hub_info, is_one_way, phase_two_config
                )

                all_hub_flights.extend(hub_results['flights'])
                hub_analysis[hub_iata] = hub_results['analysis']

            # 去重和排序
            unique_flights = self._deduplicate_flights(all_hub_flights)

            # 增强航班信息
            enhanced_flights = []
            for flight in unique_flights:
                enhanced_flight = self._convert_to_enhanced_flight(flight, context)
                enhanced_flights.append(enhanced_flight)

            execution_time = int((time.time() - start_time) * 1000)

            result = SearchResult(
                status=SearchResultStatus.SUCCESS,
                flights=enhanced_flights,
                execution_time_ms=execution_time,
                metadata={
                    "hubs_probed": [h['iata'] for h in hubs_to_probe],
                    "hub_analysis": hub_analysis,
                    "enhanced_flights": len(enhanced_flights),
                    "is_one_way": is_one_way
                },
                disclaimers=self._get_disclaimers()
            )

            await self._log_execution_end(context, result)
            return result

        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self.logger.error(f"[{context.search_id}] 中转城市探测执行失败: {e}", exc_info=True)

            return SearchResult(
                status=SearchResultStatus.FAILED,
                flights=[],
                execution_time_ms=execution_time,
                error_message=f"中转城市探测执行失败: {str(e)}"
            )

    def _extract_phase_two_config(self, context: SearchContext) -> Dict[str, Any]:
        """从搜索上下文中提取第二阶段配置"""
        # 如果context中有phase_two相关配置，使用它
        metadata = context.metadata or {}
        return metadata.get('phase_two_config', {
            'hub_selection_strategy': HubSelectionStrategy.COUNTRY_MAJOR,
            'max_hubs_to_probe': 5,
            'enable_throwaway_ticketing': True,
            'price_threshold_factor': 0.9,
            'max_results_per_hub': 10
        })

    def _get_hubs_to_probe(self, context: SearchContext, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取要探测的中转城市列表"""
        strategy = config.get('hub_selection_strategy', HubSelectionStrategy.COUNTRY_MAJOR)
        max_hubs = config.get('max_hubs_to_probe', 5)
        custom_hubs = config.get('custom_hubs', [])

        destination = context.request.destination_iata.upper()
        origin = context.request.origin_iata.upper()

        if strategy == HubSelectionStrategy.CUSTOM_LIST and custom_hubs:
            # 使用自定义中转城市列表
            hubs = []
            for hub_code in custom_hubs[:max_hubs]:
                if hub_code != origin and hub_code != destination:
                    hubs.append({
                        'iata': hub_code,
                        'name': f'{hub_code} Hub',
                        'city': hub_code
                    })
            return hubs

        # 基于目的地国家/地区选择主要枢纽
        candidate_hubs = []

        # 根据目的地选择合适的枢纽区域
        if self._is_china_airport(destination):
            candidate_hubs.extend(self.hub_mappings['china'])
            candidate_hubs.extend(self.hub_mappings['asia'][:3])
        elif self._is_asia_airport(destination):
            candidate_hubs.extend(self.hub_mappings['asia'])
            candidate_hubs.extend(self.hub_mappings['china'][:3])
        elif self._is_europe_airport(destination):
            candidate_hubs.extend(self.hub_mappings['europe'])
        elif self._is_north_america_airport(destination):
            candidate_hubs.extend(self.hub_mappings['north_america'])
        else:
            # 全球性搜索，选择各区域主要枢纽
            candidate_hubs.extend(self.hub_mappings['asia'][:2])
            candidate_hubs.extend(self.hub_mappings['europe'][:2])
            candidate_hubs.extend(self.hub_mappings['north_america'][:2])

        # 过滤掉起始地和目的地
        filtered_hubs = [
            hub for hub in candidate_hubs
            if hub['iata'] != origin and hub['iata'] != destination
        ]

        return filtered_hubs[:max_hubs]

    async def _probe_single_hub(
        self,
        context: SearchContext,
        hub_info: Dict[str, Any],
        is_one_way: bool,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """探测单个中转城市"""
        hub_iata = hub_info['iata']
        probe_results = {
            'flights': [],
            'analysis': {
                'hub_info': hub_info,
                'direct_to_hub_count': 0,
                'hub_to_destination_count': 0,
                'throwaway_via_hub_count': 0,
                'errors': []
            }
        }

        try:
            self.logger.info(f"[{context.search_id}] 探测中转城市: {hub_iata}")

            # 策略1: 搜索 Origin -> Hub
            origin_to_hub_flights = await self._search_origin_to_hub(
                context, hub_iata, is_one_way, config
            )
            probe_results['flights'].extend(origin_to_hub_flights)
            probe_results['analysis']['direct_to_hub_count'] = len(origin_to_hub_flights)

            # 策略2: 搜索 Hub -> Destination（可选，主要用于分析）
            # 这里暂时跳过，因为用户主要关心从起始地出发的完整行程

            # 策略3: 搜索甩尾票（Origin -> X via Hub，X为甩尾目的地）
            if config.get('enable_throwaway_ticketing', True):
                throwaway_flights = await self._search_throwaway_via_hub(
                    context, hub_iata, is_one_way, config
                )
                probe_results['flights'].extend(throwaway_flights)
                probe_results['analysis']['throwaway_via_hub_count'] = len(throwaway_flights)

            self.logger.info(
                f"[{context.search_id}] 中转城市 {hub_iata} 探测完成: "
                f"直飞到中转 {probe_results['analysis']['direct_to_hub_count']}, "
                f"甩尾经中转 {probe_results['analysis']['throwaway_via_hub_count']}"
            )

        except Exception as e:
            error_msg = f"探测中转城市 {hub_iata} 时出错: {str(e)}"
            probe_results['analysis']['errors'].append(error_msg)
            self.logger.warning(f"[{context.search_id}] {error_msg}")

        return probe_results

    async def _search_origin_to_hub(
        self,
        context: SearchContext,
        hub_iata: str,
        is_one_way: bool,
        config: Dict[str, Any]
    ) -> List[FlightItinerary]:
        """搜索从起始地到中转城市的航班"""
        try:
            # 构建查询变量（搜索 Origin -> Hub）
            variables = self._build_hub_variables(context, hub_iata, is_one_way)

            # 执行搜索
            context.increment_api_calls()
            raw_results = await self._perform_search(context, variables, is_one_way)

            # 解析结果
            flights = await self._parse_hub_results(context, raw_results, is_one_way)

            # 标记为中转航班
            for flight in flights:
                flight.isProbeSuggestion = True
                flight.probeHub = hub_iata
                flight.probeDisclaimer = f"此航班到达{hub_iata}，您需要另行安排前往最终目的地的交通"

            return flights

        except Exception as e:
            self.logger.error(f"[{context.search_id}] 搜索到中转城市 {hub_iata} 失败: {e}")
            return []

    async def _search_throwaway_via_hub(
        self,
        context: SearchContext,
        hub_iata: str,
        is_one_way: bool,
        config: Dict[str, Any]
    ) -> List[FlightItinerary]:
        """搜索经过中转城市的甩尾票"""
        throwaway_destinations = ['HKG', 'TPE', 'NRT', 'SIN', 'BKK']  # 常用甩尾目的地
        all_throwaway_flights = []

        for dest in throwaway_destinations:
            if dest == hub_iata or dest == context.request.origin_iata.upper():
                continue

            try:
                # 构建查询变量（搜索 Origin -> Dest via Hub）
                variables = self._build_throwaway_via_hub_variables(
                    context, dest, hub_iata, is_one_way
                )

                # 执行搜索
                context.increment_api_calls()
                raw_results = await self._perform_search(context, variables, is_one_way)

                # 解析并筛选经过目标城市的航班
                throwaway_flights = await self._extract_throwaway_via_hub(
                    context, raw_results, hub_iata, dest, is_one_way
                )

                all_throwaway_flights.extend(throwaway_flights)

            except Exception as e:
                self.logger.warning(f"[{context.search_id}] 搜索甩尾路线经 {hub_iata} 到 {dest} 失败: {e}")
                continue

        return all_throwaway_flights

    def _build_hub_variables(self, context: SearchContext, hub_iata: str, is_one_way: bool) -> Dict[str, Any]:
        """构建中转城市搜索变量"""
        from app.apis.v1.schemas import FlightSearchRequest

        temp_request = FlightSearchRequest(
            origin_iata=context.request.origin_iata,
            destination_iata=hub_iata,  # 目的地设为中转城市
            departure_date_from=context.request.departure_date_from,
            departure_date_to=context.request.departure_date_to,
            return_date_from=context.request.return_date_from,
            return_date_to=context.request.return_date_to,
            cabin_class=context.request.cabin_class,
            adults=context.request.adults,
            preferred_currency=context.request.preferred_currency,
            market=context.request.market
        )

        variables = _task_build_kiwi_variables(temp_request, is_one_way)
        variables["filter"]["maxStopsCount"] = 3  # 允许最多3次中转
        variables["search_id"] = f"{context.search_id}_hub_{hub_iata}"

        return variables

    def _build_throwaway_via_hub_variables(
        self,
        context: SearchContext,
        final_dest: str,
        hub_iata: str,
        is_one_way: bool
    ) -> Dict[str, Any]:
        """构建经过中转城市的甩尾搜索变量"""
        from app.apis.v1.schemas import FlightSearchRequest

        temp_request = FlightSearchRequest(
            origin_iata=context.request.origin_iata,
            destination_iata=final_dest,  # 甩尾目的地
            departure_date_from=context.request.departure_date_from,
            departure_date_to=context.request.departure_date_to,
            return_date_from=context.request.return_date_from,
            return_date_to=context.request.return_date_to,
            cabin_class=context.request.cabin_class,
            adults=context.request.adults,
            preferred_currency=context.request.preferred_currency,
            market=context.request.market
        )

        variables = _task_build_kiwi_variables(temp_request, is_one_way)
        variables["filter"]["maxStopsCount"] = 3  # 允许更多中转以找到经过hub的路线
        variables["search_id"] = f"{context.search_id}_throwaway_via_{hub_iata}_to_{final_dest}"

        return variables

    async def _perform_search(self, context: SearchContext, variables: Dict[str, Any], is_one_way: bool) -> List[Dict[str, Any]]:
        """执行Kiwi API搜索"""
        try:
            class MockSelf:
                def __init__(self):
                    self.request = type('MockRequest', (), {'id': context.search_id})()

            mock_self = MockSelf()

            from app.apis.v1.schemas import FlightSearchRequest
            temp_request = FlightSearchRequest(
                origin_iata=context.request.origin_iata,
                destination_iata=context.request.destination_iata,
                departure_date_from=context.request.departure_date_from,
                departure_date_to=context.request.departure_date_to,
                return_date_from=context.request.return_date_from,
                return_date_to=context.request.return_date_to,
                cabin_class=context.request.cabin_class,
                adults=context.request.adults
            )

            raw_results = await _task_run_search_with_retry(
                self=mock_self,
                variables=variables,
                attempt_desc="hub_probe",
                request_params=temp_request,
                force_one_way=is_one_way
            )

            return raw_results

        except Exception as e:
            self.logger.error(f"[{context.search_id}] 中转探测API调用失败: {e}", exc_info=True)
            raise

    async def _parse_hub_results(self, context: SearchContext, raw_results: List[Dict[str, Any]], is_one_way: bool) -> List[FlightItinerary]:
        """解析中转搜索结果"""
        flights = []
        requested_currency = context.request.preferred_currency or "CNY"

        for raw_itinerary in raw_results:
            try:
                parsed = await _task_parse_kiwi_itinerary(raw_itinerary, is_one_way, requested_currency)
                if parsed:
                    flights.append(parsed)
            except Exception as e:
                self.logger.warning(f"[{context.search_id}] 解析中转航班时出错: {e}")
                continue

        return flights

    async def _extract_throwaway_via_hub(
        self,
        context: SearchContext,
        raw_results: List[Dict[str, Any]],
        hub_iata: str,
        final_dest: str,
        is_one_way: bool
    ) -> List[FlightItinerary]:
        """提取经过中转城市的甩尾航班"""
        throwaway_flights = []
        target_destination = context.request.destination_iata.upper()
        requested_currency = context.request.preferred_currency or "CNY"

        self.logger.info(f"🔍 甩尾票提取诊断 - search_id: {context.search_id}")
        self.logger.info(f"  - 中转城市: {hub_iata}")
        self.logger.info(f"  - 目标城市: {target_destination}")
        self.logger.info(f"  - 甩尾目的地: {final_dest}")
        self.logger.info(f"  - 原始结果数量: {len(raw_results)}")

        for i, raw_itinerary in enumerate(raw_results):
            try:
                parsed = await _task_parse_kiwi_itinerary(raw_itinerary, is_one_way, requested_currency)
                if not parsed or not parsed.segments:
                    self.logger.info(f"  - 航班{i}: 解析失败或无航段")
                    continue

                # 打印航班路径
                route = " -> ".join([seg.departure_airport for seg in parsed.segments] + [parsed.segments[-1].arrival_airport])
                self.logger.info(f"  - 航班{i} ({parsed.id}): {route}")
                self.logger.info(f"    - is_hidden_city: {parsed.is_hidden_city}")
                self.logger.info(f"    - is_throwaway_deal: {getattr(parsed, 'is_throwaway_deal', False)}")

                # 检查是否经过中转城市和目标城市
                passes_validation = self._passes_through_hub_and_target(parsed, hub_iata, target_destination)
                self.logger.info(f"    - 路径验证结果: {passes_validation}")

                # 🔧 修复: 除了路径验证，也检查Kiwi API直接标记的甩尾票
                is_throwaway_from_api = getattr(parsed, 'is_throwaway_deal', False) or parsed.is_hidden_city

                if passes_validation or is_throwaway_from_api:
                    parsed.is_hidden_city = True
                    parsed.is_throwaway_deal = True
                    parsed.isProbeSuggestion = True
                    parsed.probeHub = hub_iata
                    parsed.probeDisclaimer = f"甩尾票：经{hub_iata}到{target_destination}，最终票面目的地为{final_dest}"

                    throwaway_flights.append(parsed)
                    self.logger.info(f"    - ✅ 识别为甩尾票")
                else:
                    self.logger.info(f"    - ❌ 未识别为甩尾票")

            except Exception as e:
                self.logger.warning(f"[{context.search_id}] 解析甩尾航班时出错: {e}")
                continue

        self.logger.info(f"  - 最终甩尾票数量: {len(throwaway_flights)}")
        return throwaway_flights

    def _passes_through_hub_and_target(self, flight: FlightItinerary, hub_iata: str, target_iata: str) -> bool:
        """检查航班是否经过指定的中转城市和目标城市"""
        if not flight.segments:
            self.logger.info(f"      - 路径验证: 无航段信息")
            return False

        passes_hub = False
        passes_target = False
        hub_segment = -1
        target_segment = -1

        self.logger.info(f"      - 路径验证详情:")
        self.logger.info(f"        - 寻找中转城市: {hub_iata}")
        self.logger.info(f"        - 寻找目标城市: {target_iata}")

        for i, segment in enumerate(flight.segments):
            self.logger.info(f"        - 航段{i}: {segment.departure_airport} -> {segment.arrival_airport}")

            if segment.arrival_airport.upper() == hub_iata.upper():
                passes_hub = True
                hub_segment = i
                self.logger.info(f"          ✅ 找到中转城市 {hub_iata} 在航段{i}")

            if (segment.arrival_airport.upper() == target_iata.upper() and
                i < len(flight.segments) - 1):  # 不是最后一站
                passes_target = True
                target_segment = i
                self.logger.info(f"          ✅ 找到目标城市 {target_iata} 在航段{i} (非最后一站)")

        result = passes_hub and passes_target
        self.logger.info(f"        - 验证结果: passes_hub={passes_hub}, passes_target={passes_target}, 最终={result}")

        if result:
            self.logger.info(f"        - ✅ 甩尾路径确认: 中转城市在航段{hub_segment}, 目标城市在航段{target_segment}")
        else:
            if not passes_hub:
                self.logger.info(f"        - ❌ 未经过中转城市 {hub_iata}")
            if not passes_target:
                self.logger.info(f"        - ❌ 未经过目标城市 {target_iata} 或目标城市是最终目的地")

        return result

    def _is_china_airport(self, iata: str) -> bool:
        """判断是否为中国机场"""
        china_airports = {
            'PEK', 'SHA', 'PVG', 'CAN', 'SZX', 'CTU', 'WUH', 'XMN',
            'CSX', 'TAO', 'NKG', 'HGH', 'TSN', 'DLC', 'SYX', 'KMG'
        }
        return iata.upper() in china_airports

    def _is_asia_airport(self, iata: str) -> bool:
        """判断是否为亚洲机场"""
        asia_airports = {
            'HKG', 'TPE', 'NRT', 'HND', 'ICN', 'SIN', 'BKK', 'KUL',
            'MNL', 'CGK', 'DEL', 'BOM', 'DXB', 'DOH'
        }
        return iata.upper() in asia_airports

    def _is_europe_airport(self, iata: str) -> bool:
        """判断是否为欧洲机场"""
        europe_airports = {
            'LHR', 'CDG', 'FRA', 'AMS', 'FCO', 'MAD', 'BCN', 'VIE',
            'ZUR', 'MUC', 'CPH', 'ARN', 'HEL'
        }
        return iata.upper() in europe_airports

    def _is_north_america_airport(self, iata: str) -> bool:
        """判断是否为北美机场"""
        north_america_airports = {
            'LAX', 'SFO', 'JFK', 'LGA', 'ORD', 'DFW', 'ATL', 'SEA',
            'YVR', 'YYZ', 'DEN', 'LAS', 'MIA'
        }
        return iata.upper() in north_america_airports

    def _deduplicate_flights(self, flights: List[FlightItinerary]) -> List[FlightItinerary]:
        """去除重复的航班"""
        seen_ids = set()
        unique_flights = []

        for flight in flights:
            if flight.id not in seen_ids:
                seen_ids.add(flight.id)
                unique_flights.append(flight)

        # 按价格排序
        unique_flights.sort(key=lambda x: x.price)
        return unique_flights

    def _convert_to_enhanced_flight(self, flight: FlightItinerary, context: SearchContext) -> EnhancedFlightItinerary:
        """将FlightItinerary转换为EnhancedFlightItinerary"""

        enhanced_flight = EnhancedFlightItinerary(
            # 复制基础字段
            id=flight.id,
            price=flight.price,
            currency=flight.currency,
            booking_token=flight.booking_token,
            deep_link=flight.deep_link,
            outbound_segments=flight.outbound_segments,
            inbound_segments=flight.inbound_segments,
            segments=flight.segments,
            total_duration_minutes=flight.total_duration_minutes,
            is_self_transfer=flight.is_self_transfer,
            is_hidden_city=flight.is_hidden_city,
            data_source=flight.data_source,
            is_throwaway_deal=flight.is_throwaway_deal,
            isProbeSuggestion=flight.isProbeSuggestion,
            probeHub=flight.probeHub,
            probeDisclaimer=flight.probeDisclaimer,
            raw_data=flight.raw_data,

            # 新增字段
            search_phase=SearchPhase.PHASE_TWO,
            quality_score=None,
            hub_info={
                'hub_code': flight.probeHub,
                'is_throwaway': flight.is_throwaway_deal,
                'disclaimer': flight.probeDisclaimer
            } if flight.probeHub else None,
            risk_factors=[],
            recommendation_reason=None
        )

        # 根据类型设置风险因素
        if flight.is_throwaway_deal:
            enhanced_flight.risk_factors.extend([
                "甩尾票风险：需要在中转站下机",
                "行李风险：托运行李可能被送到最终目的地",
                "航空公司政策风险"
            ])

        if flight.isProbeSuggestion and not flight.is_throwaway_deal:
            enhanced_flight.risk_factors.append("需要自行安排后续交通到最终目的地")

        # 计算质量评分
        base_score = self._calculate_quality_score(enhanced_flight)
        if flight.is_throwaway_deal:
            enhanced_flight.quality_score = max(0.0, base_score - 25)  # 甩尾票额外扣分
        elif flight.isProbeSuggestion:
            enhanced_flight.quality_score = max(0.0, base_score - 10)  # 中转票轻微扣分
        else:
            enhanced_flight.quality_score = base_score

        # 设置推荐理由
        if flight.is_throwaway_deal:
            enhanced_flight.recommendation_reason = "中转城市甩尾票，价格优惠但有风险"
        elif flight.isProbeSuggestion:
            enhanced_flight.recommendation_reason = f"经{flight.probeHub}中转，可能有价格优势"
        else:
            enhanced_flight.recommendation_reason = "中转城市探测结果"

        # 添加策略相关元数据
        self._enhance_flight_with_metadata(enhanced_flight, context, {
            "is_hub_probe_result": True,
            "hub_code": flight.probeHub,
            "segment_count": len(enhanced_flight.segments or [])
        })

        return enhanced_flight

    def _get_disclaimers(self) -> List[str]:
        """获取中转城市探测的免责声明"""
        return [
            "中转城市探测结果可能需要您自行安排多段行程",
            "甩尾票存在风险，请仔细阅读相关风险提示",
            "中转城市票价可能不包含全程行程，请确认后续交通安排",
            "建议对比完整行程的总成本（包括后续交通费用）",
            "航班时间和价格以实际预订时为准"
        ]