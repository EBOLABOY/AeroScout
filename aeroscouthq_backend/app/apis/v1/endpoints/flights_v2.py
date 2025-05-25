"""
V2航班搜索API端点
提供分阶段搜索接口，支持第一阶段、第二阶段和统一搜索
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging

from app.apis.v1.schemas.flights_v2 import (
    PhaseOneSearchRequest,
    PhaseTwoSearchRequest,
    UnifiedSearchRequest,
    SearchStatusRequest,
    PhaseOneSearchResponse,
    PhaseTwoSearchResponse,
    UnifiedSearchResponse,
    SearchStatusResponse
)
from app.services.flight_search_v2 import FlightSearchServiceV2

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v2/flights", tags=["Flights V2"])

# 创建服务实例（实际应用中应该使用依赖注入）
flight_search_service = FlightSearchServiceV2()

def get_flight_search_service() -> FlightSearchServiceV2:
    """获取航班搜索服务实例"""
    return flight_search_service

@router.post(
    "/search/phase-one",
    response_model=PhaseOneSearchResponse,
    summary="第一阶段搜索：直飞+甩尾航班",
    description="""
    执行第一阶段航班搜索，包括：
    1. 直飞航班搜索（快速、便利）
    2. 甩尾航班搜索（价格优势，有风险）

    这是分阶段搜索的第一步，提供基础的航班选择。
    后续可基于此结果执行第二阶段搜索以获得更多选择。
    """,
    response_description="第一阶段搜索结果，包含直飞和甩尾航班"
)
async def search_phase_one(
    request: PhaseOneSearchRequest,
    service: FlightSearchServiceV2 = Depends(get_flight_search_service)
) -> PhaseOneSearchResponse:
    """第一阶段搜索：直飞+甩尾航班"""
    try:
        logger.info(f"收到第一阶段搜索请求: {request.origin_iata} -> {request.destination_iata}")

        response = await service.execute_phase_one(request)

        logger.info(
            f"第一阶段搜索完成: {response.search_id}, "
            f"直飞 {len(response.direct_flights)}, 甩尾 {len(response.hidden_city_flights)}"
        )

        return response

    except Exception as e:
        logger.error(f"第一阶段搜索失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"第一阶段搜索失败: {str(e)}"
        )

@router.post(
    "/search/phase-two",
    response_model=PhaseTwoSearchResponse,
    summary="第二阶段搜索：中转城市探测",
    description="""
    执行第二阶段航班搜索，基于第一阶段的结果进行中转城市探测：
    1. 探测目的地国家的主要中转城市
    2. 搜索经过中转城市的甩尾航班
    3. 提供更多航班选择和潜在的价格优势

    需要提供有效的第一阶段搜索ID作为基础。
    """,
    response_description="第二阶段搜索结果，包含中转城市航班和甩尾优惠"
)
async def search_phase_two(
    request: PhaseTwoSearchRequest,
    service: FlightSearchServiceV2 = Depends(get_flight_search_service)
) -> PhaseTwoSearchResponse:
    """第二阶段搜索：中转城市探测"""
    try:
        logger.info(f"收到第二阶段搜索请求，基于搜索: {request.base_search_id}")

        response = await service.execute_phase_two(request)

        logger.info(
            f"第二阶段搜索完成: {response.search_id}, "
            f"中转 {len(response.hub_flights)}, 甩尾 {len(response.throwaway_deals)}"
        )

        return response

    except ValueError as e:
        logger.error(f"第二阶段搜索参数错误: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"第二阶段搜索失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"第二阶段搜索失败: {str(e)}"
        )

@router.post(
    "/search/unified",
    response_model=UnifiedSearchResponse,
    summary="统一搜索：自动执行所有阶段",
    description="""
    执行完整的分阶段航班搜索：
    1. 自动执行第一阶段搜索（直飞+甩尾）
    2. 根据配置决定是否执行第二阶段搜索（中转城市探测）
    3. 提供综合推荐和完整的搜索结果

    支持同步和异步执行模式：
    - 同步模式：等待所有阶段完成后返回完整结果
    - 异步模式：先返回第一阶段结果，第二阶段在后台执行
    """,
    response_description="统一搜索结果，包含所有阶段的航班信息和综合推荐"
)
async def search_unified(
    request: UnifiedSearchRequest,
    service: FlightSearchServiceV2 = Depends(get_flight_search_service)
) -> UnifiedSearchResponse:
    """统一搜索：自动执行所有阶段"""
    try:
        logger.info(f"收到统一搜索请求: {request.origin_iata} -> {request.destination_iata}")

        response = await service.execute_unified_search(request)

        logger.info(
            f"统一搜索完成: {response.search_id}, "
            f"推荐 {len(response.combined_recommendations)}, "
            f"用时 {response.overall_metrics.total_execution_time_ms}ms"
        )

        return response

    except Exception as e:
        logger.error(f"统一搜索失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"统一搜索失败: {str(e)}"
        )

@router.get(
    "/search/{search_id}/status",
    response_model=SearchStatusResponse,
    summary="查询搜索状态",
    description="""
    查询指定搜索的执行状态和进度：
    1. 当前执行阶段
    2. 整体执行状态
    3. 已完成的阶段
    4. 部分结果（如果有）
    5. 错误信息（如果有）

    适用于异步搜索的状态跟踪。
    """,
    response_description="搜索状态信息"
)
async def get_search_status(
    search_id: str,
    service: FlightSearchServiceV2 = Depends(get_flight_search_service)
) -> SearchStatusResponse:
    """查询搜索状态"""
    try:
        logger.info(f"查询搜索状态: {search_id}")

        response = await service.get_search_status(search_id)

        return response

    except ValueError as e:
        logger.error(f"搜索状态查询参数错误: {e}")
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"搜索状态查询失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"搜索状态查询失败: {str(e)}"
        )

@router.post(
    "/search-sync",
    response_model=UnifiedSearchResponse,
    summary="同步搜索接口（兼容现有API）",
    description="""
    兼容现有 /api/v1/flights/search-sync 接口的V2版本。

    按照您的需求实现分阶段搜索：
    1. 先查询直飞航班和以目的地为中转的甩尾航班
    2. 再探测目的地国家的主要中转城市
    3. 返回所有结果的综合推荐

    这是推荐使用的主要搜索接口。
    """,
    response_description="完整的搜索结果，包含所有类型的航班"
)
async def search_sync_v2(
    request: PhaseOneSearchRequest,
    service: FlightSearchServiceV2 = Depends(get_flight_search_service)
) -> UnifiedSearchResponse:
    """同步搜索接口（兼容现有API，但使用V2逻辑）"""
    try:
        logger.info(f"收到V2同步搜索请求: {request.origin_iata} -> {request.destination_iata}")

        # 转换为统一搜索请求
        unified_request = UnifiedSearchRequest(
            **request.model_dump(exclude={'search_id'}),
            enable_phase_two=True,
            async_execution=False,  # 同步执行
            phase_one_config={
                'include_hidden_city': request.include_hidden_city,
                'max_stopover_count': request.max_stopover_count,
                'direct_flights_only': request.direct_flights_only,
                'max_results': request.max_results,
                'enable_cache': request.enable_cache,
                'sort_strategy': request.sort_strategy
            },
            phase_two_config={
                'hub_selection_strategy': 'country_major',
                'max_hubs_to_probe': 5,
                'enable_throwaway_ticketing': True,
                'price_threshold_factor': 0.9,
                'max_results_per_hub': 10
            }
        )

        response = await service.execute_unified_search(unified_request)

        logger.debug(
            f"V2同步搜索完成: {response.search_id}, "
            f"第一阶段: 直飞 {len(response.phase_one_results.direct_flights)}, "
            f"甩尾 {len(response.phase_one_results.hidden_city_flights)}"
        )

        return response

    except Exception as e:
        logger.error(f"V2同步搜索失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"V2同步搜索失败: {str(e)}"
        )

@router.get(
    "/health",
    summary="健康检查",
    description="检查V2航班搜索服务的健康状态",
    response_description="服务健康状态"
)
async def health_check() -> Dict[str, Any]:
    """健康检查"""
    return {
        "status": "healthy",
        "service": "FlightSearchV2",
        "version": "2.0.0",
        "features": [
            "phase_one_search",
            "phase_two_search",
            "unified_search",
            "status_tracking",
            "enhanced_flight_data",
            "quality_scoring",
            "risk_assessment"
        ]
    }

@router.get(
    "/strategies",
    summary="获取可用的搜索策略",
    description="列出当前可用的所有搜索策略及其描述",
    response_description="搜索策略列表"
)
async def get_available_strategies(
    service: FlightSearchServiceV2 = Depends(get_flight_search_service)
) -> Dict[str, Any]:
    """获取可用的搜索策略"""
    return {
        "strategies": {
            "direct_flight": {
                "name": "直飞航班搜索",
                "description": "搜索起始地到目的地的直飞航班，无中转",
                "phase": "phase_one",
                "features": ["fast", "convenient", "higher_price"]
            },
            "hidden_city": {
                "name": "甩尾航班搜索",
                "description": "搜索经过目的地的甩尾航班，价格优势明显但有风险",
                "phase": "phase_one",
                "features": ["price_advantage", "risky", "baggage_restriction"]
            },
            "hub_probe": {
                "name": "中转城市探测",
                "description": "探测目的地国家主要中转城市，寻找更多航班选择",
                "phase": "phase_two",
                "features": ["more_options", "complex_routing", "potential_savings"]
            }
        },
        "phases": {
            "phase_one": {
                "name": "第一阶段",
                "description": "基础搜索，包含直飞和甩尾航班",
                "strategies": ["direct_flight", "hidden_city"]
            },
            "phase_two": {
                "name": "第二阶段",
                "description": "深度搜索，探测中转城市选择",
                "strategies": ["hub_probe"]
            }
        }
    }