"""
直飞航班搜索策略
"""

import time
from typing import List, Dict, Any

from .base import SearchStrategy, SearchContext, SearchResult, SearchResultStatus
from app.apis.v1.schemas.flights_v2 import EnhancedFlightItinerary, SearchPhase
from app.apis.v1.schemas import FlightItinerary

# 导入现有的任务函数
from app.core.tasks import (
    _task_build_kiwi_variables,
    _task_run_search_with_retry,
    _task_parse_kiwi_itinerary
)

class DirectFlightStrategy(SearchStrategy):
    """直飞航班搜索策略"""

    def __init__(self):
        super().__init__("direct_flight")

    def can_execute(self, context: SearchContext) -> bool:
        """检查是否可以执行直飞搜索"""
        # 直飞搜索总是可以执行
        return True

    async def execute(self, context: SearchContext) -> SearchResult:
        """执行直飞航班搜索"""
        start_time = time.time()
        await self._log_execution_start(context)

        self.logger.debug(f"[{context.search_id}] 开始直飞搜索")

        # 验证请求参数
        validation_result = await self._validate_request(context)

        if not validation_result:
            error_msg = "请求参数验证失败"
            self.logger.error(f"[{context.search_id}] {error_msg}")
            return SearchResult(
                status=SearchResultStatus.FAILED,
                flights=[],
                execution_time_ms=int((time.time() - start_time) * 1000),
                error_message=error_msg
            )

        try:
            # 构建Kiwi API查询参数
            is_one_way = context.request.return_date_from is None

            # 构建查询变量，限制为直飞（maxStopsCount=0）
            variables = self._build_direct_flight_variables(context, is_one_way)

            # 执行搜索
            context.increment_api_calls()
            raw_results = await self._perform_search(context, variables, is_one_way)

            # 解析结果
            flights = await self._parse_results(context, raw_results, is_one_way)

            # 增强航班信息
            enhanced_flights = []
            for flight in flights:
                enhanced_flight = self._convert_to_enhanced_flight(flight, context)
                enhanced_flights.append(enhanced_flight)

            execution_time = int((time.time() - start_time) * 1000)

            result = SearchResult(
                status=SearchResultStatus.SUCCESS,
                flights=enhanced_flights,
                execution_time_ms=execution_time,
                metadata={
                    "total_raw_results": len(raw_results),
                    "parsed_flights": len(flights),
                    "enhanced_flights": len(enhanced_flights),
                    "is_one_way": is_one_way
                },
                disclaimers=self._get_disclaimers()
            )

            await self._log_execution_end(context, result)
            return result

        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            self.logger.error(f"[{context.search_id}] 直飞搜索执行失败: {e}", exc_info=True)

            return SearchResult(
                status=SearchResultStatus.FAILED,
                flights=[],
                execution_time_ms=execution_time,
                error_message=f"直飞搜索执行失败: {str(e)}"
            )

    def _build_direct_flight_variables(self, context: SearchContext, is_one_way: bool) -> Dict[str, Any]:
        """构建直飞航班查询变量"""
        # 创建一个临时的FlightSearchRequest对象来使用现有函数
        from app.apis.v1.schemas import FlightSearchRequest

        temp_request = FlightSearchRequest(
            origin_iata=context.request.origin_iata,
            destination_iata=context.request.destination_iata,
            departure_date_from=context.request.departure_date_from,
            departure_date_to=context.request.departure_date_to,
            return_date_from=context.request.return_date_from,
            return_date_to=context.request.return_date_to,
            cabin_class=context.request.cabin_class,
            adults=context.request.adults,
            preferred_currency=context.request.preferred_currency,
            market=context.request.market
        )

        # 使用现有函数构建基础变量
        variables = _task_build_kiwi_variables(temp_request, is_one_way)

        # 强制设置为直飞（无中转）
        variables["filter"]["maxStopsCount"] = 0

        # 添加搜索ID
        variables["search_id"] = context.search_id

        return variables

    async def _perform_search(self, context: SearchContext, variables: Dict[str, Any], is_one_way: bool) -> List[Dict[str, Any]]:
        """执行Kiwi API搜索"""
        try:
            # 创建一个模拟的self对象用于现有函数
            class MockSelf:
                def __init__(self):
                    self.request = type('MockRequest', (), {'id': context.search_id})()
                    self.max_retries = 3  # 添加重试次数

                def retry(self, exc=None, countdown=30):
                    """模拟Celery任务的retry方法"""
                    self.logger.warning(f"MockSelf.retry called with exc={exc}, countdown={countdown}")
                    # 对于非Celery环境，我们直接抛出异常而不是重试
                    if exc:
                        raise exc
                    else:
                        raise Exception("Retry requested but no exception provided")

            mock_self = MockSelf()
            mock_self.logger = self.logger  # 添加logger引用

            # 创建临时请求对象
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

            # 使用现有的搜索函数
            raw_results = await _task_run_search_with_retry(
                self=mock_self,
                variables=variables,
                attempt_desc="direct_flight",
                request_params=temp_request,
                force_one_way=is_one_way
            )

            return raw_results

        except Exception as e:
            self.logger.error(f"[{context.search_id}] Kiwi API搜索失败: {e}", exc_info=True)
            raise

    async def _parse_results(self, context: SearchContext, raw_results: List[Dict[str, Any]], is_one_way: bool) -> List[FlightItinerary]:
        """解析原始搜索结果"""
        flights = []
        requested_currency = context.request.preferred_currency or "CNY"

        for raw_itinerary in raw_results:
            try:
                parsed = await _task_parse_kiwi_itinerary(raw_itinerary, is_one_way, requested_currency)
                if parsed:
                    # 验证确实是直飞（虽然我们已经在查询中限制了）
                    if self._is_direct_flight(parsed):
                        flights.append(parsed)
                    else:
                        self.logger.debug(f"[{context.search_id}] 过滤非直飞航班: {parsed.id}")
                else:
                    self.logger.warning(f"[{context.search_id}] 解析航班失败: {raw_itinerary.get('id', 'UNKNOWN')}")

            except Exception as e:
                self.logger.warning(f"[{context.search_id}] 解析航班时出错: {e}")
                continue

        self.logger.debug(f"[{context.search_id}] 直飞搜索解析完成: {len(flights)}/{len(raw_results)} 有效")
        return flights

    def _is_direct_flight(self, flight: FlightItinerary) -> bool:
        """验证是否为直飞航班"""
        if not flight.segments:
            return False

        # 单程直飞：只有1个航段
        if flight.inbound_segments is None:
            return len(flight.segments) == 1

        # 往返直飞：去程1个航段，返程1个航段
        outbound_count = len(flight.outbound_segments or [])
        inbound_count = len(flight.inbound_segments or [])
        return outbound_count == 1 and inbound_count == 1

    def _convert_to_enhanced_flight(self, flight: FlightItinerary, context: SearchContext) -> EnhancedFlightItinerary:
        """将FlightItinerary转换为EnhancedFlightItinerary"""

        # 创建增强的航班对象
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
            search_phase=SearchPhase.PHASE_ONE,
            quality_score=None,
            hub_info=None,
            risk_factors=[],
            recommendation_reason=None
        )

        # 计算质量评分
        enhanced_flight.quality_score = self._calculate_quality_score(enhanced_flight)

        # 设置推荐理由
        if enhanced_flight.quality_score >= 80:
            enhanced_flight.recommendation_reason = "高质量直飞航班，性价比优秀"
        elif enhanced_flight.quality_score >= 60:
            enhanced_flight.recommendation_reason = "直飞航班，出行便利"
        else:
            enhanced_flight.recommendation_reason = "直飞航班"

        # 添加策略相关元数据
        self._enhance_flight_with_metadata(enhanced_flight, context, {
            "is_direct_flight": True,
            "segment_count": len(enhanced_flight.segments or [])
        })

        return enhanced_flight

    def _get_disclaimers(self) -> List[str]:
        """获取直飞搜索的免责声明"""
        return [
            "直飞航班价格可能高于中转航班，但出行时间更短，便利性更高",
            "票价不包含行李费用，具体费用请在预订时确认",
            "航班时间以出票时的最终确认为准"
        ]