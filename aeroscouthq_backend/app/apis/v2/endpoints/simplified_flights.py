"""
简化的航班搜索API端点
"""

import logging
import time
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from typing import Optional

from app.apis.v1.schemas import FlightSearchRequest, UserResponse
from app.services.simplified_flight_service import SimplifiedFlightService
from app.core.dependencies import get_current_active_user, RateLimiter

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/search-simple")
async def search_flights_simple(
    request: FlightSearchRequest,
    include_direct: bool = Query(True, description="是否包含直飞航班"),
    include_hidden_city: bool = Query(True, description="是否包含隐藏城市航班"),
    current_user: UserResponse = Depends(get_current_active_user),
    _ = Depends(RateLimiter(limit_type="flight"))
) -> Dict[str, Any]:
    """
    简化的航班搜索API

    基于Kiwi.com GraphQL API实现直飞和隐藏城市航班搜索

    Args:
        request: 航班搜索请求参数
        include_direct: 是否包含直飞航班
        include_hidden_city: 是否包含隐藏城市航班
        current_user: 当前用户信息

    Returns:
        包含直飞和隐藏城市航班的搜索结果
    """
    try:
        logger.info(f"用户 {current_user.email} 发起简化航班搜索")
        logger.info(f"搜索参数: {request.origin_iata} -> {request.destination_iata}")
        logger.info(f"出发日期: {request.departure_date_from}")
        logger.info(f"包含类型: 直飞={include_direct}, 隐藏城市={include_hidden_city}")

        # 验证搜索参数
        if not request.origin_iata or not request.destination_iata:
            raise HTTPException(
                status_code=400,
                detail="起始机场和目的地机场代码不能为空"
            )

        if not request.departure_date_from:
            raise HTTPException(
                status_code=400,
                detail="出发日期不能为空"
            )

        if request.origin_iata.upper() == request.destination_iata.upper():
            raise HTTPException(
                status_code=400,
                detail="起始机场和目的地机场不能相同"
            )

        if not include_direct and not include_hidden_city:
            raise HTTPException(
                status_code=400,
                detail="至少需要选择一种搜索类型（直飞或隐藏城市）"
            )

        # 创建简化搜索服务
        flight_service = SimplifiedFlightService()

        # 执行搜索
        results = await flight_service.search_flights(
            request=request,
            include_direct=include_direct,
            include_hidden_city=include_hidden_city
        )

        # 添加用户信息到结果中
        results["user_id"] = current_user.id
        results["search_params"] = {
            "origin": request.origin_iata,
            "destination": request.destination_iata,
            "departure_date": request.departure_date_from,
            "return_date": request.return_date_from,
            "adults": request.adults,
            "cabin_class": request.cabin_class,
            "preferred_currency": request.preferred_currency
        }

        # 简化搜索结果统计
        direct_count = len(results.get("direct_flights", []))
        hidden_count = len(results.get("hidden_city_flights", []))

        logger.debug(f"搜索完成: 直飞={direct_count}, 甩尾={hidden_count}, 耗时={results.get('search_time_ms', 0)}ms")

        return results

    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except Exception as e:
        logger.error(f"简化航班搜索失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"航班搜索服务暂时不可用: {str(e)}"
        )

@router.get("/search-status/{search_id}")
async def get_search_status(
    search_id: str,
    current_user: UserResponse = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    获取搜索状态（为了兼容性保留，简化版本是同步的）

    Args:
        search_id: 搜索ID
        current_user: 当前用户信息

    Returns:
        搜索状态信息
    """
    try:
        # 简化版本是同步搜索，所以总是返回完成状态
        return {
            "search_id": search_id,
            "status": "completed",
            "message": "简化搜索已完成",
            "progress": 100,
            "user_id": current_user.id
        }

    except Exception as e:
        logger.error(f"获取搜索状态失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"获取搜索状态失败: {str(e)}"
        )

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    健康检查端点

    Returns:
        服务健康状态
    """
    return {
        "status": "healthy",
        "service": "simplified_flight_search",
        "version": "1.0.0",
        "features": {
            "direct_flights": True,
            "hidden_city_flights": True,
            "kiwi_graphql_api": True
        }
    }

@router.get("/disclaimers")
async def get_disclaimers() -> Dict[str, Any]:
    """
    获取免责声明

    Returns:
        免责声明信息
    """
    from app.services.simplified_flight_helpers import SimplifiedFlightHelpers

    return {
        "direct_flight_disclaimers": SimplifiedFlightHelpers.get_disclaimers(True, False),
        "hidden_city_disclaimers": SimplifiedFlightHelpers.get_disclaimers(False, True),
        "all_disclaimers": SimplifiedFlightHelpers.get_disclaimers(True, True)
    }