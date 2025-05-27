"""
V2 Flight Search API Endpoints
Enhanced with phased search, quality scoring, and advanced strategies
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
import asyncio
import uuid
from datetime import datetime
import logging

from app.core.dependencies import get_current_active_user, RateLimiter
from app.apis.v1.schemas import UserResponse

from app.apis.v1.schemas.flights_v2 import (
    # Request schemas
    FlightSearchBaseRequest,
    PhaseOneSearchRequest,
    PhaseTwoSearchRequest,
    UnifiedSearchRequest,

    # Response schemas
    PhaseOneSearchResponse,
    PhaseTwoSearchResponse,
    UnifiedSearchResponse,
    SearchStatusResponse,

    # Enums
    SearchPhase,
    HubSelectionStrategy,
    SortStrategy
)

from app.core.search_strategies.base import SearchContext
from app.core.search_strategies.direct_flight import DirectFlightStrategy
from app.core.search_strategies.hidden_city import HiddenCityStrategy
from app.core.search_strategies.hub_probe import HubProbeStrategy

# 获取logger
logger = logging.getLogger(__name__)

def create_enhanced_flight_key(flight):
    """创建基于航班特征的唯一标识"""
    segments = flight.segments or []
    if not segments:
        return f"no_segments_{flight.price}_{flight.total_duration_minutes}"

    # 使用航班号、起降时间、机场代码创建唯一标识
    first_segment = segments[0]
    last_segment = segments[-1]

    flight_numbers = "_".join([seg.flight_number for seg in segments if seg.flight_number])
    departure_time = first_segment.departure_time.strftime("%Y%m%d_%H%M") if first_segment.departure_time else "unknown"
    arrival_time = last_segment.arrival_time.strftime("%Y%m%d_%H%M") if last_segment.arrival_time else "unknown"
    route = f"{first_segment.departure_airport}_{last_segment.arrival_airport}"

    return f"{flight_numbers}_{departure_time}_{arrival_time}_{route}"

def deduplicate_flights_enhanced(flights):
    """增强的航班去重逻辑"""
    flight_groups = {}

    for flight in flights:
        key = create_enhanced_flight_key(flight)
        if key not in flight_groups:
            flight_groups[key] = []
        flight_groups[key].append(flight)

    # 对于每组重复航班，选择最优选项
    deduplicated = []
    for key, group in flight_groups.items():
        if len(group) == 1:
            deduplicated.append(group[0])
        else:
            # 选择价格最低且有有效booking_token的航班
            best_flight = min(group, key=lambda f: (f.price, not bool(f.booking_token)))
            deduplicated.append(best_flight)

            # 记录去重信息用于调试
            logger.info(f"去重航班组 {key}: 从 {len(group)} 个选项中选择价格 ¥{best_flight.price} 的航班")

    return deduplicated

# 创建V2路由器
router = APIRouter(prefix="/flights", tags=["flights-v2"])

# 导入搜索会话管理器
from app.core.search_session_manager import get_search_session_manager

def create_search_context(request: FlightSearchBaseRequest, search_id: str, phase: SearchPhase) -> SearchContext:
    """创建搜索上下文对象"""
    return SearchContext(
        request=request,
        search_id=search_id,
        phase=phase,
        started_at=datetime.utcnow(),
        cache_enabled=True,
        kiwi_headers=None,
        api_call_count=0,
        cache_hits=0,
        total_cache_attempts=0,
        metadata={}
    )

@router.post("/search/phase-one", response_model=PhaseOneSearchResponse)
async def search_phase_one(
    request: PhaseOneSearchRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    _ = Depends(RateLimiter(limit_type="flight")),
    session_manager = Depends(get_search_session_manager)
) -> PhaseOneSearchResponse:
    """
    第一阶段搜索：直飞航班 + throwaway票探测
    """
    try:
        search_id = str(uuid.uuid4())
        logger.info(f"开始第一阶段搜索 - ID: {search_id}")

        # 创建搜索上下文
        context = create_search_context(request, search_id, SearchPhase.PHASE_ONE)

        # 存储搜索会话
        session_data = {
            "search_id": search_id,
            "request": request.model_dump(),
            "phase": SearchPhase.PHASE_ONE.value,
            "started_at": datetime.now().isoformat(),
            "status": "processing"
        }
        await session_manager.set_session(search_id, session_data)

        results = []
        phase_metrics = {}

        # 执行直飞搜索
        if request.include_direct_flights:
            logger.info(f"执行直飞搜索 - 搜索ID: {search_id}")
            direct_strategy = DirectFlightStrategy()
            direct_result = await direct_strategy.execute(context)

            if direct_result.flights:
                results.extend(direct_result.flights)
                phase_metrics["direct_flights"] = {
                    "count": len(direct_result.flights),
                    "search_time_ms": direct_result.metrics.get("search_time_ms", 0),
                    "data_source": "kiwi_api"
                }
                logger.info(f"直飞搜索完成 - 找到 {len(direct_result.flights)} 个航班")

        # 执行throwaway搜索
        if request.include_throwaway_tickets:
            logger.info(f"执行throwaway搜索 - 搜索ID: {search_id}")
            hidden_city_strategy = HiddenCityStrategy()
            throwaway_result = await hidden_city_strategy.execute(context)

            if throwaway_result.flights:
                results.extend(throwaway_result.flights)
                phase_metrics["throwaway_flights"] = {
                    "count": len(throwaway_result.flights),
                    "search_time_ms": throwaway_result.metrics.get("search_time_ms", 0),
                    "data_source": "kiwi_api"
                }
                logger.info(f"Throwaway搜索完成 - 找到 {len(throwaway_result.flights)} 个航班")

        # 应用排序
        if request.sort_strategy == SortStrategy.PRICE_ASC:
            results.sort(key=lambda x: x.price)
        elif request.sort_strategy == SortStrategy.DURATION_ASC:
            results.sort(key=lambda x: x.total_duration_minutes or 0)
        elif request.sort_strategy == SortStrategy.DEPARTURE_TIME_ASC:
            results.sort(key=lambda x: x.segments[0].departure_time if x.segments else datetime.min)
        elif request.sort_strategy == SortStrategy.QUALITY_SCORE:
            results.sort(key=lambda x: x.quality_score or 0, reverse=True)

        # 应用限制
        if request.max_results:
            results = results[:request.max_results]

        # 更新搜索会话
        session_updates = {
            "status": "completed",
            "completed_at": datetime.now().isoformat(),
            "results_count": len(results)
        }
        await session_manager.update_session(search_id, session_updates)

        # 分离直飞和throwaway航班
        direct_flights = []
        hidden_city_flights = []

        for flight in results:
            if hasattr(flight, 'is_hidden_city') and flight.is_hidden_city:
                hidden_city_flights.append(flight)
            else:
                direct_flights.append(flight)

        # 获取会话数据计算执行时间
        session_data = await session_manager.get_session(search_id)
        started_at_str = session_data.get("started_at") if session_data else datetime.now().isoformat()
        started_at = datetime.fromisoformat(started_at_str.replace('Z', '+00:00'))
        execution_time_ms = int((datetime.now() - started_at).total_seconds() * 1000)

        # 创建搜索阶段结果
        from app.apis.v1.schemas.flights_v2 import SearchPhaseResult
        metrics = SearchPhaseResult(
            phase=SearchPhase.PHASE_ONE,
            status="completed",
            execution_time_ms=execution_time_ms,
            results_count=len(results),
            cache_hit=False,
            started_at=started_at,
            completed_at=datetime.now()
        )

        response = PhaseOneSearchResponse(
            search_id=search_id,
            direct_flights=direct_flights,
            hidden_city_flights=hidden_city_flights,
            metrics=metrics,
            disclaimers=[
                "第一阶段搜索结果，包含直飞和throwaway票选项",
                "价格可能发生变化，请以最终预订页面为准",
                "Throwaway票存在一定风险，请仔细阅读条款"
            ],
            next_phase_available=True if len(results) > 0 else False
        )

        logger.info(f"第一阶段搜索完成 - ID: {search_id}, 结果数: {len(results)}")
        return response

    except Exception as e:
        logger.error(f"第一阶段搜索失败: {str(e)}")
        # 更新搜索会话状态为失败
        try:
            if await session_manager.exists(search_id):
                await session_manager.update_session(search_id, {
                    "status": "failed",
                    "error": str(e),
                    "completed_at": datetime.now().isoformat()
                })
        except Exception as session_error:
            logger.error(f"更新搜索会话状态失败: {session_error}")
        raise HTTPException(status_code=500, detail=f"第一阶段搜索失败: {str(e)}")

@router.post("/search/phase-two", response_model=PhaseTwoSearchResponse)
async def search_phase_two(
    request: PhaseTwoSearchRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    _ = Depends(RateLimiter(limit_type="flight"))
) -> PhaseTwoSearchResponse:
    """
    第二阶段搜索：枢纽城市探测和复杂路由
    """
    try:
        search_id = str(uuid.uuid4())
        logger.info(f"开始第二阶段搜索 - ID: {search_id}")

        # 创建搜索上下文
        context = create_search_context(request, search_id, SearchPhase.PHASE_TWO)

        # 存储搜索会话
        search_sessions[search_id] = {
            "search_id": search_id,
            "request": request.dict(),
            "phase": SearchPhase.PHASE_TWO,
            "started_at": datetime.utcnow(),
            "status": "processing"
        }

        results = []
        phase_metrics = {}
        hub_details = {}

        # 执行枢纽探测搜索
        logger.info(f"执行枢纽探测搜索 - 搜索ID: {search_id}")
        hub_strategy = HubProbeStrategy()

        # 设置枢纽选择策略
        hub_strategy.hub_selection_strategy = request.hub_selection_strategy
        if request.custom_hubs:
            hub_strategy.custom_hubs = request.custom_hubs

        hub_result = await hub_strategy.execute(context)

        if hub_result.flights:
            results.extend(hub_result.flights)
            phase_metrics["hub_exploration"] = {
                "count": len(hub_result.flights),
                "search_time_ms": hub_result.metrics.get("search_time_ms", 0),
                "hubs_explored": hub_result.metadata.get("hubs_explored", []),
                "successful_hubs": hub_result.metadata.get("successful_hubs", [])
            }
            hub_details = hub_result.metadata.get("hub_details", {})
            logger.info(f"枢纽探测完成 - 找到 {len(hub_result.flights)} 个航班")

        # 应用排序
        if request.sort_strategy == SortStrategy.PRICE_ASC:
            results.sort(key=lambda x: x.price)
        elif request.sort_strategy == SortStrategy.DURATION_ASC:
            results.sort(key=lambda x: x.total_duration_minutes or 0)
        elif request.sort_strategy == SortStrategy.DEPARTURE_TIME_ASC:
            results.sort(key=lambda x: x.segments[0].departure_time if x.segments else datetime.min)
        elif request.sort_strategy == SortStrategy.QUALITY_SCORE:
            results.sort(key=lambda x: x.quality_score or 0, reverse=True)

        # 应用限制
        if request.max_results:
            results = results[:request.max_results]

        # 更新搜索会话
        search_sessions[search_id].update({
            "status": "completed",
            "completed_at": datetime.utcnow(),
            "results_count": len(results)
        })

        # 分离中转航班和throwaway优惠
        hub_flights = []
        throwaway_deals = []

        for flight in results:
            if hasattr(flight, 'is_throwaway_deal') and flight.is_throwaway_deal:
                throwaway_deals.append(flight)
            else:
                hub_flights.append(flight)

        # 创建搜索阶段结果
        from app.apis.v1.schemas.flights_v2 import SearchPhaseResult
        metrics = SearchPhaseResult(
            phase=SearchPhase.PHASE_TWO,
            status="completed",
            execution_time_ms=int((datetime.utcnow() - search_sessions[search_id]["started_at"]).total_seconds() * 1000),
            results_count=len(results),
            cache_hit=False,
            started_at=search_sessions[search_id]["started_at"],
            completed_at=datetime.utcnow()
        )

        response = PhaseTwoSearchResponse(
            search_id=search_id,
            base_search_id=request.base_search_id,
            hub_flights=hub_flights,
            throwaway_deals=throwaway_deals,
            hub_analysis=hub_details,
            metrics=metrics,
            disclaimers=[
                "第二阶段搜索结果，基于枢纽城市探测",
                "复杂路由可能涉及多个航空公司，请注意中转要求",
                "价格可能发生变化，请以最终预订页面为准"
            ]
        )

        logger.info(f"第二阶段搜索完成 - ID: {search_id}, 结果数: {len(results)}")
        return response

    except Exception as e:
        logger.error(f"第二阶段搜索失败: {str(e)}")
        if search_id in search_sessions:
            search_sessions[search_id]["status"] = "failed"
            search_sessions[search_id]["error"] = str(e)
        raise HTTPException(status_code=500, detail=f"第二阶段搜索失败: {str(e)}")

@router.post("/search-sync", response_model=UnifiedSearchResponse)
async def unified_search_sync(
    request: UnifiedSearchRequest,
    current_user: UserResponse = Depends(get_current_active_user),
    _ = Depends(RateLimiter(limit_type="flight"))
) -> UnifiedSearchResponse:
    """
    统一同步搜索：执行完整的两阶段搜索
    兼容V1 API格式，同时提供V2增强功能
    """
    try:
        search_id = str(uuid.uuid4())
        logger.info(f"[DEBUG V2] 开始统一搜索 - ID: {search_id}")
        logger.info(f"[DEBUG V2] 请求参数: {request.model_dump()}")

        # 创建搜索上下文
        context = create_search_context(request, search_id, SearchPhase.UNIFIED)

        # 存储搜索会话
        search_sessions[search_id] = {
            "search_id": search_id,
            "request": request.dict(),
            "phase": "unified",
            "started_at": datetime.utcnow(),
            "status": "processing"
        }

        all_flights = []
        direct_flights = []
        combo_deals = []
        disclaimers = []
        phase_metrics = {}
        probe_details = {}

        # 第一阶段：直飞 + throwaway
        if request.include_direct_flights or request.include_throwaway_tickets:
            logger.info(f"执行第一阶段搜索 - 搜索ID: {search_id}")

            # 直飞搜索
            if request.include_direct_flights:
                logger.info(f"[DEBUG V2] 开始执行直飞搜索 - 搜索ID: {search_id}")
                direct_strategy = DirectFlightStrategy()
                logger.info(f"[DEBUG V2] 直飞策略实例化完成")
                logger.info(f"[DEBUG V2] 搜索上下文: {context}")

                direct_result = await direct_strategy.execute(context)
                logger.info(f"[DEBUG V2] 直飞搜索执行完成 - 状态: {direct_result.status}, 结果数: {len(direct_result.flights)}")

                if direct_result.error_message:
                    logger.error(f"[DEBUG V2] 直飞搜索错误: {direct_result.error_message}")

                if direct_result.flights:
                    direct_flights.extend(direct_result.flights)
                    all_flights.extend(direct_result.flights)
                    phase_metrics["direct_flights"] = {
                        "count": len(direct_result.flights),
                        "search_time_ms": direct_result.metrics.get("search_time_ms", 0)
                    }
                    logger.info(f"[DEBUG V2] 直飞航班添加完成，当前总数: {len(all_flights)}")
                else:
                    logger.warning(f"[DEBUG V2] 直飞搜索未返回任何结果")

            # Throwaway搜索
            if request.include_throwaway_tickets:
                hidden_city_strategy = HiddenCityStrategy()
                throwaway_result = await hidden_city_strategy.execute(context)
                if throwaway_result.flights:
                    combo_deals.extend(throwaway_result.flights)
                    all_flights.extend(throwaway_result.flights)
                    phase_metrics["throwaway_flights"] = {
                        "count": len(throwaway_result.flights),
                        "search_time_ms": throwaway_result.metrics.get("search_time_ms", 0)
                    }

        # 第二阶段：枢纽探测（如果启用）
        if request.enable_hub_probe:
            logger.info(f"执行第二阶段枢纽搜索 - 搜索ID: {search_id}")
            hub_strategy = HubProbeStrategy()
            hub_result = await hub_strategy.execute(context)

            if hub_result.flights:
                combo_deals.extend(hub_result.flights)
                all_flights.extend(hub_result.flights)
                phase_metrics["hub_exploration"] = {
                    "count": len(hub_result.flights),
                    "search_time_ms": hub_result.metrics.get("search_time_ms", 0),
                    "hubs_explored": hub_result.metadata.get("hubs_explored", [])
                }
                probe_details = hub_result.metadata.get("hub_details", {})

        # 增强的去重逻辑
        unique_flights = deduplicate_flights_enhanced(all_flights)

        # 应用排序
        if request.sort_strategy == SortStrategy.PRICE_ASC:
            unique_flights.sort(key=lambda x: x.price)
            direct_flights.sort(key=lambda x: x.price)
            combo_deals.sort(key=lambda x: x.price)
        elif request.sort_strategy == SortStrategy.DURATION_ASC:
            unique_flights.sort(key=lambda x: x.total_duration_minutes or 0)
            direct_flights.sort(key=lambda x: x.total_duration_minutes or 0)
            combo_deals.sort(key=lambda x: x.total_duration_minutes or 0)
        elif request.sort_strategy == SortStrategy.DEPARTURE_TIME_ASC:
            unique_flights.sort(key=lambda x: x.segments[0].departure_time if x.segments else datetime.min)
            direct_flights.sort(key=lambda x: x.segments[0].departure_time if x.segments else datetime.min)
            combo_deals.sort(key=lambda x: x.segments[0].departure_time if x.segments else datetime.min)
        elif request.sort_strategy == SortStrategy.QUALITY_SCORE:
            unique_flights.sort(key=lambda x: x.quality_score or 0, reverse=True)
            direct_flights.sort(key=lambda x: x.quality_score or 0, reverse=True)
            combo_deals.sort(key=lambda x: x.quality_score or 0, reverse=True)

        # 应用结果限制
        if request.max_results:
            direct_flights = direct_flights[:request.max_results]
            combo_deals = combo_deals[:request.max_results]

        # 生成免责声明
        disclaimers = [
            "搜索结果包含多种票型和路由选择",
            "价格可能随时变化，请以最终预订页面为准"
        ]

        if phase_metrics.get("throwaway_flights"):
            disclaimers.append("部分结果包含throwaway票，存在一定使用风险")

        if phase_metrics.get("hub_exploration"):
            disclaimers.append("枢纽探测结果可能涉及复杂中转，请注意航班衔接时间")

        # 更新搜索会话
        search_sessions[search_id].update({
            "status": "completed",
            "completed_at": datetime.utcnow(),
            "results_count": len(unique_flights),
            "direct_count": len(direct_flights),
            "combo_count": len(combo_deals)
        })

        # 构建响应（兼容V1格式，同时包含V2增强信息）
        response = UnifiedSearchResponse(
            search_id=search_id,
            direct_flights=direct_flights,
            combo_deals=combo_deals,
            disclaimers=disclaimers,
            probe_details=probe_details if probe_details else None,
            phase_metrics=phase_metrics,
            total_results=len(unique_flights)
        )

        logger.info(f"统一搜索完成 - ID: {search_id}, 总结果: {len(unique_flights)}, 直飞: {len(direct_flights)}, 组合: {len(combo_deals)}")
        return response

    except Exception as e:
        logger.error(f"统一搜索失败: {str(e)}")
        if search_id in search_sessions:
            search_sessions[search_id]["status"] = "failed"
            search_sessions[search_id]["error"] = str(e)
        raise HTTPException(status_code=500, detail=f"统一搜索失败: {str(e)}")

@router.get("/search/status/{search_id}", response_model=SearchStatusResponse)
async def get_search_status(
    search_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
    session_manager = Depends(get_search_session_manager)
) -> SearchStatusResponse:
    """
    获取搜索状态
    """
    session = await session_manager.get_session(search_id)
    if not session:
        raise HTTPException(status_code=404, detail="搜索会话不存在")

    # 解析时间字符串
    started_at_str = session.get("started_at")
    completed_at_str = session.get("completed_at")

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
        status=session.get("status", "unknown"),
        phase=session.get("phase", "unknown"),
        started_at=started_at,
        completed_at=completed_at,
        results_count=session.get("results_count", 0),
        error_message=session.get("error")
    )

@router.delete("/search/{search_id}")
async def cleanup_search_session(
    search_id: str,
    current_user: UserResponse = Depends(get_current_active_user),
    session_manager = Depends(get_search_session_manager)
):
    """
    清理搜索会话
    """
    if await session_manager.exists(search_id):
        success = await session_manager.delete_session(search_id)
        if success:
            return {"message": f"搜索会话 {search_id} 已清理"}
        else:
            raise HTTPException(status_code=500, detail="清理搜索会话失败")
    else:
        raise HTTPException(status_code=404, detail="搜索会话不存在")

# 健康检查端点
@router.get("/health")
async def health_check(session_manager = Depends(get_search_session_manager)):
    """
    V2 API健康检查
    """
    # 检查搜索会话管理器状态
    session_health = await session_manager.health_check()

    return {
        "status": "healthy",
        "version": "v2",
        "message": "V2 API is running",
        "timestamp": datetime.now().isoformat(),
        "search_session_storage": session_health
    }

# 搜索会话管理端点
@router.get("/sessions")
async def list_search_sessions(
    pattern: str = "*",
    current_user: UserResponse = Depends(get_current_active_user),
    session_manager = Depends(get_search_session_manager)
):
    """
    列出搜索会话
    """
    try:
        sessions = await session_manager.list_sessions(pattern)
        return {
            "sessions": sessions,
            "count": len(sessions),
            "storage_type": "redis" if session_manager.is_using_redis() else "memory"
        }
    except Exception as e:
        logger.error(f"列出搜索会话失败: {e}")
        raise HTTPException(status_code=500, detail="列出搜索会话失败")

@router.get("/sessions/{search_id}/info")
async def get_search_session_info(
    search_id: str,
    session_manager = Depends(get_search_session_manager)
):
    """
    获取搜索会话详细信息
    """
    try:
        info = await session_manager.get_session_info(search_id)
        if not info:
            raise HTTPException(status_code=404, detail="搜索会话不存在")
        return info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取搜索会话信息失败: {e}")
        raise HTTPException(status_code=500, detail="获取搜索会话信息失败")
