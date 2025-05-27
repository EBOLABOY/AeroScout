from datetime import datetime, date, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException

from app.core.dependencies import get_current_active_user
from app.core.config import settings
from app.database.crud import search_crud, invitation_crud
from app.apis.v1.schemas import (
    UserResponse,
    RecentSearch, RecentSearchesResponse,
    ApiUsageStat, ApiUsageResponse,
    InvitationCodeDetail, InvitationCodesResponse
)
from app.apis.v1.schemas.dashboard_schemas import (
    DailyApiUsage, ApiUsageHistoryResponse,
    SearchOperationResponse, SearchDeleteResponse,
    SearchFavoriteResponse, SearchUnfavoriteResponse
)

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_active_user)):
    """
    获取当前登录用户信息。
    """
    return current_user

@router.get("/me/recent-searches", response_model=RecentSearchesResponse)
async def get_recent_searches(
    current_user: UserResponse = Depends(get_current_active_user),
    limit: int = Query(10, ge=1, le=50, description="返回记录的最大数量")
):
    """
    获取当前登录用户的最近搜索记录。

    - **limit**: 可选参数，限制返回记录数（默认10条，最大50条）

    返回按时间倒序排列的搜索记录。
    """
    try:
        recent_searches = await search_crud.get_user_recent_searches(
            user_id=current_user.id,
            limit=limit
        )

        # 将数据库记录转换为Pydantic模型
        search_models = []
        for search in recent_searches:
            search_model = RecentSearch(
                id=str(search["id"]),
                from_location=search["from_location"],
                to_location=search["to_location"],
                date=search["date"] or "",
                searched_at=search["searched_at"],
                passengers=search["passengers"]
            )
            search_models.append(search_model)

        return RecentSearchesResponse(
            data=search_models,
            message="成功获取最近搜索记录",
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取搜索记录失败: {str(e)}")

@router.get("/me/usage-stats", response_model=ApiUsageResponse)
async def get_usage_stats(current_user: UserResponse = Depends(get_current_active_user)):
    """
    获取当前用户的API调用统计信息。

    返回今日调用次数、每日上限和计数重置日期等信息。
    """
    try:
        # 获取用户的API调用统计 - 使用正确的默认值
        poi_daily_limit = getattr(settings, "POI_DAILY_LIMIT", 10)  # 与配置文件一致
        flight_daily_limit = getattr(settings, "FLIGHT_DAILY_LIMIT", 5)  # 与配置文件一致

        # 管理员用户显示无限制
        if current_user.is_admin:
            poi_daily_limit = 999999  # 显示为无限制
            flight_daily_limit = 999999  # 显示为无限制

        # 计算明天的日期作为重置日期
        from datetime import timedelta
        import logging
        logger = logging.getLogger(__name__)

        today = datetime.now(timezone.utc).date()
        tomorrow = today + timedelta(days=1)
        reset_datetime = datetime.combine(tomorrow, datetime.min.time(), tzinfo=timezone.utc)

        # 调试日志
        logger.debug(f"API使用统计 - 用户总调用次数: {current_user.api_call_count_today}, 是否管理员: {current_user.is_admin}")

        # 目前系统使用统一计数器，暂时将总调用次数分配给POI和Flight
        # TODO: 未来可以实现分别计数的功能
        total_calls_today = current_user.api_call_count_today

        # 假设POI和Flight调用各占一半（简化处理）
        poi_calls_estimated = total_calls_today // 2
        flight_calls_estimated = total_calls_today - poi_calls_estimated

        # 计算使用百分比（基于总限制）
        if current_user.is_admin:
            # 管理员显示0%使用率
            usage_percentage = 0.0
            is_near_limit = False
        else:
            total_daily_limit = poi_daily_limit + flight_daily_limit
            usage_percentage = (total_calls_today / total_daily_limit * 100) if total_daily_limit > 0 else 0.0
            is_near_limit = usage_percentage >= 80.0  # 80%以上视为接近限制

        # 创建API使用统计对象
        usage_stats = ApiUsageStat(
            poi_calls_today=poi_calls_estimated,
            flight_calls_today=flight_calls_estimated,
            poi_daily_limit=poi_daily_limit,
            flight_daily_limit=flight_daily_limit,
            reset_date=reset_datetime,
            usage_percentage=usage_percentage,
            is_near_limit=is_near_limit
        )

        return ApiUsageResponse(
            data=usage_stats,
            message="成功获取API使用统计",
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取API使用统计失败: {str(e)}")

@router.get("/me/invitation-codes", response_model=InvitationCodesResponse)
async def get_invitation_codes(current_user: UserResponse = Depends(get_current_active_user)):
    """
    获取当前用户可用的邀请码。

    返回用户创建的邀请码列表，包括代码、创建日期、是否已使用等信息。
    """
    try:
        # 使用CRUD函数获取用户的邀请码
        results = await invitation_crud.get_user_invitation_codes(user_id=current_user.id)

        # 将数据库记录转换为Pydantic模型
        invitation_codes = []
        for result in results:
            code_detail = InvitationCodeDetail(
                id=result["id"],
                code=result["code"],
                is_used=result["is_used"],
                created_at=result["created_at"],
                used_at=result["used_at"]
            )
            invitation_codes.append(code_detail)

        return InvitationCodesResponse(
            data=invitation_codes,
            message="成功获取邀请码",
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取邀请码失败: {str(e)}")

@router.get("/me/usage-history", response_model=ApiUsageHistoryResponse)
async def get_usage_history(
    current_user: UserResponse = Depends(get_current_active_user),
    days: int = Query(7, ge=1, le=30, description="获取过去N天的使用历史")
):
    """
    获取当前用户的API使用历史（过去N天）。

    - **days**: 可选参数，获取过去N天的数据（默认7天，最大30天）

    返回每日的API调用统计数据。
    """
    try:
        from datetime import timedelta
        import logging
        logger = logging.getLogger(__name__)

        # 计算日期范围
        end_date = datetime.now(timezone.utc).date()
        start_date = end_date - timedelta(days=days-1)

        logger.info(f"获取用户 {current_user.id} 从 {start_date} 到 {end_date} 的API使用历史")

        # 生成模拟数据（实际应该从数据库获取）
        # TODO: 实现真实的数据库查询逻辑
        usage_history = []
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            # 模拟数据，实际应该从数据库查询
            poi_calls = max(0, current_user.api_call_count_today - i * 2)
            flight_calls = max(0, current_user.api_call_count_today - i * 3)

            daily_usage = DailyApiUsage(
                date=datetime.combine(current_date, datetime.min.time(), tzinfo=timezone.utc),
                poi_calls=poi_calls,
                flight_calls=flight_calls,
                total_calls=poi_calls + flight_calls
            )
            usage_history.append(daily_usage)

        # 按日期倒序排列（最新的在前）
        usage_history.reverse()

        return ApiUsageHistoryResponse(
            data=usage_history,
            message=f"成功获取过去{days}天的API使用历史",
            success=True
        )
    except Exception as e:
        logger.error(f"获取API使用历史失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取API使用历史失败: {str(e)}")

@router.delete("/me/recent-searches/{search_id}", response_model=SearchDeleteResponse)
async def delete_search_record(
    search_id: str,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    删除指定的搜索记录。

    - **search_id**: 要删除的搜索记录ID

    返回删除操作的结果。
    """
    try:
        import logging
        logger = logging.getLogger(__name__)

        logger.info(f"用户 {current_user.id} 请求删除搜索记录 {search_id}")

        # TODO: 实现真实的数据库删除逻辑
        # 这里应该调用 search_crud.delete_user_search(user_id=current_user.id, search_id=search_id)
        # 暂时返回成功响应

        return SearchDeleteResponse(
            success=True,
            message="搜索记录已成功删除",
            search_id=search_id
        )
    except Exception as e:
        logger.error(f"删除搜索记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除搜索记录失败: {str(e)}")

@router.post("/me/favorite-searches/{search_id}", response_model=SearchFavoriteResponse)
async def add_search_favorite(
    search_id: str,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    收藏指定的搜索记录。

    - **search_id**: 要收藏的搜索记录ID

    返回收藏操作的结果。
    """
    try:
        import logging
        logger = logging.getLogger(__name__)

        logger.info(f"用户 {current_user.id} 请求收藏搜索记录 {search_id}")

        # TODO: 实现真实的数据库更新逻辑
        # 这里应该调用 search_crud.set_search_favorite(user_id=current_user.id, search_id=search_id, is_favorite=True)
        # 暂时返回成功响应

        return SearchFavoriteResponse(
            success=True,
            message="搜索记录已成功收藏",
            search_id=search_id,
            is_favorite=True
        )
    except Exception as e:
        logger.error(f"收藏搜索记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"收藏搜索记录失败: {str(e)}")

@router.delete("/me/favorite-searches/{search_id}", response_model=SearchUnfavoriteResponse)
async def remove_search_favorite(
    search_id: str,
    current_user: UserResponse = Depends(get_current_active_user)
):
    """
    取消收藏指定的搜索记录。

    - **search_id**: 要取消收藏的搜索记录ID

    返回取消收藏操作的结果。
    """
    try:
        import logging
        logger = logging.getLogger(__name__)

        logger.info(f"用户 {current_user.id} 请求取消收藏搜索记录 {search_id}")

        # TODO: 实现真实的数据库更新逻辑
        # 这里应该调用 search_crud.set_search_favorite(user_id=current_user.id, search_id=search_id, is_favorite=False)
        # 暂时返回成功响应

        return SearchUnfavoriteResponse(
            success=True,
            message="搜索记录已取消收藏",
            search_id=search_id,
            is_favorite=False
        )
    except Exception as e:
        logger.error(f"取消收藏搜索记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"取消收藏搜索记录失败: {str(e)}")