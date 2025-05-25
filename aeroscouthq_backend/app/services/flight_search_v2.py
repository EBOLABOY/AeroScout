"""
V2航班搜索服务层
负责协调和管理分阶段搜索策略，提供统一的搜索接口
"""

import uuid
import time
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.core.search_strategies import (
    SearchStrategy, SearchContext, SearchResult,
    DirectFlightStrategy, HiddenCityStrategy, HubProbeStrategy
)
from app.core.search_session_manager import search_session_manager
from app.apis.v1.schemas.flights_v2 import (
    FlightSearchBaseRequest,
    PhaseOneSearchRequest,
    PhaseTwoSearchRequest,
    UnifiedSearchRequest,
    PhaseOneSearchResponse,
    PhaseTwoSearchResponse,
    UnifiedSearchResponse,
    SearchStatusResponse,
    SearchPhase,
    SearchPhaseResult,
    FlightSearchMetrics,
    EnhancedFlightItinerary,
    SortStrategy
)

import logging

logger = logging.getLogger(__name__)

class FlightSearchServiceV2:
    """V2航班搜索服务"""

    def __init__(self):
        # 初始化搜索策略
        self.strategies = {
            'direct_flight': DirectFlightStrategy(),
            'hidden_city': HiddenCityStrategy(),
            'hub_probe': HubProbeStrategy()
        }

        # 使用全局搜索会话管理器（支持Redis存储）
        self.session_manager = search_session_manager

    async def execute_phase_one(self, request: PhaseOneSearchRequest) -> PhaseOneSearchResponse:
        """执行第一阶段搜索：直飞 + 甩尾航班"""
        search_id = request.search_id or self._generate_search_id()

        logger.info(f"[{search_id}] 开始执行第一阶段搜索")
        start_time = datetime.now()

        try:
            # 创建搜索上下文
            context = SearchContext(
                request=request,
                search_id=search_id,
                phase=SearchPhase.PHASE_ONE,
                started_at=start_time,
                cache_enabled=request.enable_cache
            )

            # 记录搜索状态
            await self._update_search_state(search_id, {
                'phase': SearchPhase.PHASE_ONE.value,
                'status': 'running',
                'started_at': start_time.isoformat(),
                'request': request.model_dump()
            })

            # 并行执行直飞和甩尾搜索策略
            direct_task = self._execute_strategy('direct_flight', context)
            hidden_task = None

            if request.include_hidden_city:
                hidden_task = self._execute_strategy('hidden_city', context)

            # 等待搜索完成
            direct_result = await direct_task
            hidden_result = await hidden_task if hidden_task else SearchResult(
                status="skipped", flights=[], execution_time_ms=0
            )

            # 合并和处理结果
            direct_flights = direct_result.flights if direct_result.success else []
            hidden_flights = hidden_result.flights if hidden_result.success else []

            # 简化第一阶段结果日志
            logger.debug(f"第一阶段搜索完成 - search_id: {search_id}, 直飞: {len(direct_flights)}, 甩尾: {len(hidden_flights)}")

            # 应用排序策略
            direct_flights = self._apply_sort_strategy(direct_flights, request.sort_strategy)
            hidden_flights = self._apply_sort_strategy(hidden_flights, request.sort_strategy)

            # 限制结果数量
            direct_flights = direct_flights[:request.max_results]
            hidden_flights = hidden_flights[:request.max_results // 2]  # 甩尾票数量限制为一半

            # 计算执行指标
            total_execution_time = int((datetime.now() - start_time).total_seconds() * 1000)

            metrics = SearchPhaseResult(
                phase=SearchPhase.PHASE_ONE,
                status="completed",
                execution_time_ms=total_execution_time,
                results_count=len(direct_flights) + len(hidden_flights),
                cache_hit=direct_result.cache_hit or hidden_result.cache_hit,
                started_at=start_time,
                completed_at=datetime.now()
            )

            # 收集免责声明
            disclaimers = []
            if direct_result.disclaimers:
                disclaimers.extend(direct_result.disclaimers)
            if hidden_result.disclaimers:
                disclaimers.extend(hidden_result.disclaimers)

            # 创建响应
            response = PhaseOneSearchResponse(
                search_id=search_id,
                direct_flights=direct_flights,
                hidden_city_flights=hidden_flights,
                metrics=metrics,
                disclaimers=disclaimers,
                next_phase_available=len(direct_flights) > 0  # 有直飞结果才能进行第二阶段
            )

            # 更新搜索状态
            await self._update_search_state(search_id, {
                'phase': SearchPhase.PHASE_ONE.value,
                'status': 'completed',
                'completed_at': datetime.now().isoformat(),
                'phase_one_results': response.model_dump(),
                'api_calls': context.api_call_count,
                'cache_hit_rate': context.cache_hit_rate
            })

            logger.debug(f"[{search_id}] 第一阶段完成: 直飞 {len(direct_flights)}, 甩尾 {len(hidden_flights)}, 用时 {total_execution_time}ms")

            return response

        except Exception as e:
            logger.error(f"[{search_id}] 第一阶段搜索失败: {e}", exc_info=True)

            # 更新搜索状态
            await self._update_search_state(search_id, {
                'status': 'failed',
                'error': str(e),
                'completed_at': datetime.now().isoformat()
            })

            # 返回错误响应
            return PhaseOneSearchResponse(
                search_id=search_id,
                direct_flights=[],
                hidden_city_flights=[],
                metrics=SearchPhaseResult(
                    phase=SearchPhase.PHASE_ONE,
                    status="failed",
                    execution_time_ms=int((datetime.now() - start_time).total_seconds() * 1000),
                    results_count=0,
                    cache_hit=False,
                    error_message=str(e),
                    started_at=start_time,
                    completed_at=datetime.now()
                ),
                disclaimers=["搜索过程中发生错误，请稍后重试"],
                next_phase_available=False
            )

    async def execute_phase_two(self, request: PhaseTwoSearchRequest) -> PhaseTwoSearchResponse:
        """执行第二阶段搜索：中转城市探测"""
        search_id = self._generate_search_id()
        base_search_id = request.base_search_id

        logger.debug(f"[{search_id}] 开始第二阶段搜索，基于 {base_search_id}")
        start_time = datetime.now()

        try:
            # 验证第一阶段搜索是否存在
            base_state = await self.session_manager.get_session(base_search_id)
            if not base_state:
                raise ValueError(f"第一阶段搜索 {base_search_id} 不存在")

            if base_state.get('status') != 'completed':
                raise ValueError(f"第一阶段搜索 {base_search_id} 未完成")

            # 获取第一阶段的请求参数
            phase_one_request_data = base_state.get('request', {})

            # 创建基础请求对象
            base_request = FlightSearchBaseRequest(**{
                k: v for k, v in phase_one_request_data.items()
                if k in FlightSearchBaseRequest.model_fields
            })

            # 创建搜索上下文
            context = SearchContext(
                request=base_request,
                search_id=search_id,
                phase=SearchPhase.PHASE_TWO,
                started_at=start_time,
                cache_enabled=request.enable_cache,
                metadata={
                    'phase_two_config': {
                        'hub_selection_strategy': request.hub_selection_strategy,
                        'max_hubs_to_probe': request.max_hubs_to_probe,
                        'custom_hubs': request.custom_hubs,
                        'enable_throwaway_ticketing': request.enable_throwaway_ticketing,
                        'price_threshold_factor': request.price_threshold_factor,
                        'max_results_per_hub': request.max_results_per_hub
                    },
                    'base_search_id': base_search_id
                }
            )

            # 记录搜索状态
            await self._update_search_state(search_id, {
                'phase': SearchPhase.PHASE_TWO.value,
                'status': 'running',
                'started_at': start_time.isoformat(),
                'base_search_id': base_search_id,
                'request': request.model_dump()
            })

            # 执行中转城市探测策略
            hub_result = await self._execute_strategy('hub_probe', context)

            # 处理结果
            hub_flights = hub_result.flights if hub_result.success else []
            throwaway_deals = [f for f in hub_flights if f.is_throwaway_deal]
            regular_hub_flights = [f for f in hub_flights if not f.is_throwaway_deal]

            # 计算执行指标
            total_execution_time = int((datetime.now() - start_time).total_seconds() * 1000)

            metrics = SearchPhaseResult(
                phase=SearchPhase.PHASE_TWO,
                status="completed",
                execution_time_ms=total_execution_time,
                results_count=len(hub_flights),
                cache_hit=hub_result.cache_hit,
                started_at=start_time,
                completed_at=datetime.now()
            )

            # 创建响应
            response = PhaseTwoSearchResponse(
                search_id=search_id,
                base_search_id=base_search_id,
                hub_flights=regular_hub_flights,
                throwaway_deals=throwaway_deals,
                hub_analysis=hub_result.metadata.get('hub_analysis', {}),
                metrics=metrics,
                disclaimers=hub_result.disclaimers or []
            )

            # 更新搜索状态
            await self._update_search_state(search_id, {
                'phase': SearchPhase.PHASE_TWO.value,
                'status': 'completed',
                'completed_at': datetime.now().isoformat(),
                'phase_two_results': response.model_dump(),
                'api_calls': context.api_call_count,
                'cache_hit_rate': context.cache_hit_rate
            })

            logger.debug(f"[{search_id}] 第二阶段完成: 中转 {len(regular_hub_flights)}, 甩尾 {len(throwaway_deals)}, 用时 {total_execution_time}ms")

            return response

        except Exception as e:
            logger.error(f"[{search_id}] 第二阶段搜索失败: {e}", exc_info=True)

            # 更新搜索状态
            await self._update_search_state(search_id, {
                'status': 'failed',
                'error': str(e),
                'completed_at': datetime.now().isoformat()
            })

            # 返回错误响应
            return PhaseTwoSearchResponse(
                search_id=search_id,
                base_search_id=base_search_id,
                hub_flights=[],
                throwaway_deals=[],
                hub_analysis={},
                metrics=SearchPhaseResult(
                    phase=SearchPhase.PHASE_TWO,
                    status="failed",
                    execution_time_ms=int((datetime.now() - start_time).total_seconds() * 1000),
                    results_count=0,
                    cache_hit=False,
                    error_message=str(e),
                    started_at=start_time,
                    completed_at=datetime.now()
                ),
                disclaimers=["第二阶段搜索过程中发生错误，请稍后重试"]
            )

    async def execute_unified_search(self, request: UnifiedSearchRequest) -> UnifiedSearchResponse:
        """执行统一搜索：自动执行所有阶段"""
        search_id = request.search_id or self._generate_search_id()

        logger.debug(f"[{search_id}] 开始统一搜索")
        start_time = datetime.now()

        try:
            # 第一阶段搜索
            phase_one_config = request.phase_one_config or {}
            phase_one_request = PhaseOneSearchRequest(
                **request.model_dump(exclude={'phase_one_config', 'phase_two_config', 'enable_phase_two', 'async_execution'}),
                **phase_one_config,
                search_id=search_id
            )

            phase_one_response = await self.execute_phase_one(phase_one_request)

            # 第二阶段搜索（如果启用）
            phase_two_response = None
            if request.enable_phase_two and phase_one_response.next_phase_available:
                phase_two_config = request.phase_two_config or {}
                phase_two_request = PhaseTwoSearchRequest(
                    base_search_id=phase_one_response.search_id,
                    **phase_two_config
                )

                if request.async_execution:
                    # 异步执行第二阶段（实际应用中可以使用消息队列）
                    asyncio.create_task(self.execute_phase_two(phase_two_request))
                    logger.debug(f"[{search_id}] 第二阶段搜索已异步启动")
                else:
                    # 同步执行第二阶段
                    phase_two_response = await self.execute_phase_two(phase_two_request)

            # 生成综合推荐
            combined_recommendations = self._generate_combined_recommendations(
                phase_one_response, phase_two_response
            )

            # 计算总体指标
            total_execution_time = int((datetime.now() - start_time).total_seconds() * 1000)

            phases = [phase_one_response.metrics]
            if phase_two_response:
                phases.append(phase_two_response.metrics)

            overall_metrics = FlightSearchMetrics(
                total_execution_time_ms=total_execution_time,
                api_calls_count=sum(
                    self.search_states.get(p.metadata.get('search_id', ''), {}).get('api_calls', 0)
                    for p in phases
                ),
                cache_hit_rate=sum(
                    self.search_states.get(p.metadata.get('search_id', ''), {}).get('cache_hit_rate', 0.0)
                    for p in phases
                ) / len(phases) if phases else 0.0,
                phases=phases
            )

            # 创建响应
            response = UnifiedSearchResponse(
                search_id=search_id,
                phase_one_results=phase_one_response,
                phase_two_results=phase_two_response,
                combined_recommendations=combined_recommendations,
                overall_metrics=overall_metrics,
                processing_summary={
                    'total_direct_flights': len(phase_one_response.direct_flights),
                    'total_hidden_city_flights': len(phase_one_response.hidden_city_flights),
                    'total_hub_flights': len(phase_two_response.hub_flights) if phase_two_response else 0,
                    'total_throwaway_deals': len(phase_two_response.throwaway_deals) if phase_two_response else 0,
                    'phase_two_executed': phase_two_response is not None,
                    'async_execution': request.async_execution
                }
            )

            logger.debug(f"[{search_id}] 统一搜索完成，用时 {total_execution_time}ms")
            return response

        except Exception as e:
            logger.error(f"[{search_id}] 统一搜索失败: {e}", exc_info=True)
            raise

    async def get_search_status(self, search_id: str) -> SearchStatusResponse:
        """获取搜索状态"""
        state = await self.session_manager.get_session(search_id)
        if not state:
            raise ValueError(f"搜索 {search_id} 不存在")

        # 解析时间字符串
        started_at_str = state.get('started_at')
        completed_at_str = state.get('completed_at')

        started_at = None
        completed_at = None

        if started_at_str:
            try:
                started_at = datetime.fromisoformat(started_at_str.replace('Z', '+00:00'))
            except ValueError:
                started_at = datetime.now()

        if completed_at_str:
            try:
                completed_at = datetime.fromisoformat(completed_at_str.replace('Z', '+00:00'))
            except ValueError:
                pass

        return SearchStatusResponse(
            search_id=search_id,
            current_phase=SearchPhase(state.get('phase', 'phase_one')),
            overall_status=state.get('status', 'unknown'),
            phases_completed=[SearchPhase(state['phase'])] if state.get('status') == 'completed' else [],
            estimated_completion_time=None,  # 可以根据历史数据估算
            partial_results=state.get('partial_results'),
            error_info={'error': state.get('error')} if state.get('error') else None
        )

    async def _execute_strategy(self, strategy_name: str, context: SearchContext) -> SearchResult:
        """执行单个搜索策略"""
        strategy = self.strategies.get(strategy_name)
        if not strategy:
            raise ValueError(f"未知的搜索策略: {strategy_name}")

        if not strategy.can_execute(context):
            logger.warning(f"[{context.search_id}] 策略 {strategy_name} 无法在当前阶段执行")
            return SearchResult(
                status="skipped",
                flights=[],
                execution_time_ms=0,
                error_message=f"策略 {strategy_name} 无法在当前阶段执行"
            )

        return await strategy.execute(context)

    def _apply_sort_strategy(self, flights: List[EnhancedFlightItinerary], sort_strategy: SortStrategy) -> List[EnhancedFlightItinerary]:
        """应用排序策略"""
        if not flights:
            return flights

        if sort_strategy == SortStrategy.PRICE_ASC:
            return sorted(flights, key=lambda x: x.price)
        elif sort_strategy == SortStrategy.DURATION_ASC:
            return sorted(flights, key=lambda x: x.total_duration_minutes or 0)
        elif sort_strategy == SortStrategy.DEPARTURE_TIME_ASC:
            # 按出发时间排序（需要从segments中提取）
            def get_departure_time(flight):
                if flight.segments and len(flight.segments) > 0:
                    return flight.segments[0].departure_time
                return datetime.min
            return sorted(flights, key=get_departure_time)
        elif sort_strategy == SortStrategy.QUALITY_SCORE:
            return sorted(flights, key=lambda x: x.quality_score or 0, reverse=True)
        else:
            return flights

    def _generate_combined_recommendations(
        self,
        phase_one: PhaseOneSearchResponse,
        phase_two: Optional[PhaseTwoSearchResponse]
    ) -> List[EnhancedFlightItinerary]:
        """生成综合推荐"""
        recommendations = []

        # 添加最佳直飞航班
        if phase_one.direct_flights:
            best_direct = min(phase_one.direct_flights, key=lambda x: x.price)
            recommendations.append(best_direct)

        # 添加性价比最好的甩尾航班
        if phase_one.hidden_city_flights:
            best_hidden = max(
                phase_one.hidden_city_flights,
                key=lambda x: (x.quality_score or 0) - (x.price / 1000)  # 简单的性价比计算
            )
            recommendations.append(best_hidden)

        # 添加第二阶段的最佳选择
        if phase_two:
            if phase_two.hub_flights:
                best_hub = min(phase_two.hub_flights, key=lambda x: x.price)
                recommendations.append(best_hub)

            if phase_two.throwaway_deals:
                best_throwaway = max(
                    phase_two.throwaway_deals,
                    key=lambda x: (x.quality_score or 0) - (x.price / 1000)
                )
                recommendations.append(best_throwaway)

        # 去重并按质量评分排序
        unique_recommendations = []
        seen_ids = set()

        for flight in recommendations:
            if flight.id not in seen_ids:
                seen_ids.add(flight.id)
                unique_recommendations.append(flight)

        return sorted(unique_recommendations, key=lambda x: x.quality_score or 0, reverse=True)[:5]

    def _generate_search_id(self) -> str:
        """生成搜索ID"""
        return f"search_{uuid.uuid4().hex[:8]}_{int(time.time())}"

    async def _update_search_state(self, search_id: str, state_update: Dict[str, Any]) -> None:
        """更新搜索状态"""
        try:
            # 获取现有状态
            existing_state = await self.session_manager.get_session(search_id)

            if existing_state:
                # 更新现有状态
                await self.session_manager.update_session(search_id, state_update)
            else:
                # 创建新状态
                await self.session_manager.set_session(search_id, state_update)

        except Exception as e:
            logger.error(f"更新搜索状态失败 {search_id}: {e}")
            # 如果Redis失败，可以考虑回退到内存存储或其他处理方式