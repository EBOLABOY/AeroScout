from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List

# --- 最近搜索记录模型 ---

class RecentSearch(BaseModel):
    """单条搜索记录的模型"""
    id: str = Field(..., json_schema_extra={"example": "1"})
    from_location: str = Field(..., alias="from", json_schema_extra={"example": "北京 (PEK)"})
    to_location: str = Field(..., alias="to", json_schema_extra={"example": "上海 (SHA)"})
    date: str = Field(..., json_schema_extra={"example": "2025-06-10"})
    searched_at: datetime = Field(..., json_schema_extra={"example": "2025-05-18T16:30:00"})
    passengers: int = Field(default=1, json_schema_extra={"example": 1})
    is_favorite: bool = Field(default=False, json_schema_extra={"example": False})

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

class RecentSearchesResponse(BaseModel):
    """最近搜索记录响应模型"""
    data: List[RecentSearch]
    message: str = "成功获取最近搜索记录"
    success: bool = True

# --- API使用统计模型 ---

class ApiUsageStat(BaseModel):
    """API使用统计模型"""
    poi_calls_today: int = Field(..., json_schema_extra={"example": 10})
    flight_calls_today: int = Field(..., json_schema_extra={"example": 5})
    poi_daily_limit: int = Field(..., json_schema_extra={"example": 50})
    flight_daily_limit: int = Field(..., json_schema_extra={"example": 20})
    reset_date: datetime = Field(..., json_schema_extra={"example": "2025-05-21T00:00:00"})
    usage_percentage: float = Field(..., json_schema_extra={"example": 32.5})
    is_near_limit: bool = Field(..., json_schema_extra={"example": False})

    model_config = ConfigDict(from_attributes=True)

class ApiUsageResponse(BaseModel):
    """API使用统计响应模型"""
    data: ApiUsageStat
    message: str = "成功获取API使用统计"
    success: bool = True

# --- 邀请码模型 ---

class InvitationCodeDetail(BaseModel):
    """邀请码详情模型"""
    id: int = Field(..., json_schema_extra={"example": 1})
    code: str = Field(..., json_schema_extra={"example": "INVITE123"})
    is_used: bool = Field(..., json_schema_extra={"example": False})
    created_at: datetime = Field(..., json_schema_extra={"example": "2025-04-01T10:00:00"})
    used_at: Optional[datetime] = Field(None, json_schema_extra={"example": None})

    model_config = ConfigDict(from_attributes=True)

class InvitationCodesResponse(BaseModel):
    """邀请码响应模型"""
    data: List[InvitationCodeDetail]
    message: str = "成功获取邀请码"
    success: bool = True

# --- API使用历史模型 ---

class DailyApiUsage(BaseModel):
    """每日API使用统计"""
    date: datetime = Field(..., json_schema_extra={"example": "2025-05-14T00:00:00"})
    poi_calls: int = Field(..., json_schema_extra={"example": 15})
    flight_calls: int = Field(..., json_schema_extra={"example": 8})
    total_calls: int = Field(..., json_schema_extra={"example": 23})
    
    model_config = ConfigDict(from_attributes=True)

class ApiUsageHistoryResponse(BaseModel):
    """API使用历史响应模型"""
    data: List[DailyApiUsage]
    message: str = "成功获取API使用历史"
    success: bool = True

# --- 搜索记录操作响应模型 ---

class SearchOperationResponse(BaseModel):
    """搜索记录操作响应模型"""
    success: bool = True
    message: str
    search_id: str

class SearchDeleteResponse(SearchOperationResponse):
    """搜索记录删除响应模型"""
    message: str = "搜索记录已成功删除"

class SearchFavoriteResponse(SearchOperationResponse):
    """搜索记录收藏响应模型"""
    message: str = "搜索记录已成功收藏"
    is_favorite: bool = True

class SearchUnfavoriteResponse(SearchOperationResponse):
    """搜索记录取消收藏响应模型"""
    message: str = "搜索记录已取消收藏"
    is_favorite: bool = False