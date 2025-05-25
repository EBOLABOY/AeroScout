from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from enum import Enum

# 枚举定义
class SearchPhase(str, Enum):
    """搜索阶段枚举"""
    PHASE_ONE = "phase_one"
    PHASE_TWO = "phase_two"
    UNIFIED = "unified"

class HubSelectionStrategy(str, Enum):
    """中转城市选择策略"""
    COUNTRY_MAJOR = "country_major"  # 基于目的地国家的主要枢纽
    REGION_POPULAR = "region_popular"  # 基于地区的热门中转城市
    CUSTOM_LIST = "custom_list"  # 自定义中转城市列表

class SortStrategy(str, Enum):
    """排序策略"""
    PRICE_ASC = "PRICE_ASC"
    DURATION_ASC = "DURATION_ASC"
    DEPARTURE_TIME_ASC = "DEPARTURE_TIME_ASC"
    QUALITY_SCORE = "QUALITY_SCORE"

# 基础请求schema
class FlightSearchBaseRequest(BaseModel):
    """航班搜索基础请求模型"""
    search_id: Optional[str] = Field(None, description="可选的搜索ID，用于缓存和追踪")
    origin_iata: str = Field(..., description="起始机场IATA代码", json_schema_extra={"example": "PVG"})
    destination_iata: str = Field(..., description="目的地机场IATA代码", json_schema_extra={"example": "LAX"})
    departure_date_from: str = Field(..., description="出发日期开始 (YYYY-MM-DD)", json_schema_extra={"example": "2024-12-01"})
    departure_date_to: str = Field(..., description="出发日期结束 (YYYY-MM-DD)", json_schema_extra={"example": "2024-12-03"})
    return_date_from: Optional[str] = Field(None, description="返程日期开始 (YYYY-MM-DD, 往返票)", json_schema_extra={"example": "2024-12-10"})
    return_date_to: Optional[str] = Field(None, description="返程日期结束 (YYYY-MM-DD, 往返票)", json_schema_extra={"example": "2024-12-12"})
    cabin_class: str = Field("ECONOMY", description="舱位等级", json_schema_extra={"example": "ECONOMY"})
    adults: int = Field(1, description="成人乘客数量", ge=1, le=9, json_schema_extra={"example": 1})
    children: int = Field(0, description="儿童乘客数量", ge=0, le=8, json_schema_extra={"example": 0})
    infants: int = Field(0, description="婴儿乘客数量", ge=0, le=8, json_schema_extra={"example": 0})
    preferred_currency: str = Field("CNY", description="首选货币", json_schema_extra={"example": "CNY"})
    preferred_locale: str = Field("zh", description="首选语言", json_schema_extra={"example": "zh"})
    market: str = Field("cn", description="市场代码", json_schema_extra={"example": "cn"})
    is_one_way: bool = Field(True, description="是否为单程票", json_schema_extra={"example": True})

    model_config = ConfigDict(from_attributes=True)

# 第一阶段请求schema
class PhaseOneSearchRequest(FlightSearchBaseRequest):
    """第一阶段搜索请求：直飞+甩尾航班"""
    include_hidden_city: bool = Field(True, description="是否包含甩尾航班")
    max_stopover_count: int = Field(3, description="最大中转次数", ge=0, le=3)
    direct_flights_only: bool = Field(False, description="仅搜索直飞航班")
    max_results: int = Field(50, description="最大结果数量", ge=1, le=100)
    enable_cache: bool = Field(True, description="是否启用缓存")
    sort_strategy: SortStrategy = Field(SortStrategy.PRICE_ASC, description="排序策略")

# 第二阶段请求schema
class PhaseTwoSearchRequest(BaseModel):
    """第二阶段搜索请求：中转城市探测"""
    base_search_id: str = Field(..., description="第一阶段搜索ID")
    hub_selection_strategy: HubSelectionStrategy = Field(HubSelectionStrategy.COUNTRY_MAJOR, description="中转城市选择策略")
    max_hubs_to_probe: int = Field(5, description="最大探测中转城市数量", ge=1, le=10)
    custom_hubs: Optional[List[str]] = Field(None, description="自定义中转城市IATA代码列表")
    enable_throwaway_ticketing: bool = Field(True, description="是否启用甩尾票搜索")
    price_threshold_factor: float = Field(0.9, description="价格阈值因子（相对于第一阶段最低价）", ge=0.1, le=1.0)
    max_results_per_hub: int = Field(10, description="每个中转城市最大结果数", ge=1, le=20)
    max_results: Optional[int] = Field(50, description="最大总结果数", ge=1, le=100)
    sort_strategy: SortStrategy = Field(SortStrategy.PRICE_ASC, description="排序策略")
    enable_cache: bool = Field(True, description="是否启用缓存")

    model_config = ConfigDict(from_attributes=True)

# 统一搜索请求schema
class UnifiedSearchRequest(FlightSearchBaseRequest):
    """统一搜索请求：执行所有搜索阶段"""
    include_direct_flights: bool = Field(True, description="是否包含直飞航班")
    include_throwaway_tickets: bool = Field(True, description="是否包含throwaway票")
    enable_hub_probe: bool = Field(True, description="是否启用枢纽探测")
    sort_strategy: SortStrategy = Field(SortStrategy.PRICE_ASC, description="排序策略")
    max_results: Optional[int] = Field(50, description="最大结果数量", ge=1, le=100)
    phase_one_config: Optional[Dict[str, Any]] = Field(None, description="第一阶段配置参数")
    phase_two_config: Optional[Dict[str, Any]] = Field(None, description="第二阶段配置参数")
    enable_phase_two: bool = Field(True, description="是否启用第二阶段搜索")
    async_execution: bool = Field(False, description="是否异步执行第二阶段")

# 搜索结果相关schema
class SearchPhaseResult(BaseModel):
    """搜索阶段结果"""
    phase: SearchPhase = Field(..., description="搜索阶段")
    status: str = Field(..., description="执行状态", json_schema_extra={"example": "completed"})
    execution_time_ms: int = Field(..., description="执行时间（毫秒）")
    results_count: int = Field(..., description="结果数量")
    cache_hit: bool = Field(..., description="是否命中缓存")
    error_message: Optional[str] = Field(None, description="错误信息")
    started_at: datetime = Field(..., description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")

class FlightSearchMetrics(BaseModel):
    """搜索指标"""
    total_execution_time_ms: int = Field(..., description="总执行时间（毫秒）")
    api_calls_count: int = Field(..., description="API调用次数")
    cache_hit_rate: float = Field(..., description="缓存命中率")
    phases: List[SearchPhaseResult] = Field(..., description="各阶段执行详情")

# 从现有schema继承航班相关模型
from app.apis.v1.schemas import FlightSegment, FlightItinerary

class EnhancedFlightItinerary(FlightItinerary):
    """增强的航班行程模型"""
    search_phase: SearchPhase = Field(..., description="发现此航班的搜索阶段")
    quality_score: Optional[float] = Field(None, description="质量评分 (0-100)")
    hub_info: Optional[Dict[str, Any]] = Field(None, description="中转信息（第二阶段结果）")
    risk_factors: List[str] = Field([], description="风险因素列表")
    recommendation_reason: Optional[str] = Field(None, description="推荐理由")

# 响应schema
class PhaseOneSearchResponse(BaseModel):
    """第一阶段搜索响应"""
    search_id: str = Field(..., description="搜索ID")
    direct_flights: List[EnhancedFlightItinerary] = Field(..., description="直飞航班列表")
    hidden_city_flights: List[EnhancedFlightItinerary] = Field(..., description="甩尾航班列表")
    metrics: SearchPhaseResult = Field(..., description="搜索指标")
    disclaimers: List[str] = Field([], description="免责声明")
    next_phase_available: bool = Field(..., description="是否可以执行第二阶段")

    model_config = ConfigDict(from_attributes=True)

class PhaseTwoSearchResponse(BaseModel):
    """第二阶段搜索响应"""
    search_id: str = Field(..., description="搜索ID")
    base_search_id: str = Field(..., description="基础搜索ID")
    hub_flights: List[EnhancedFlightItinerary] = Field(..., description="中转城市航班列表")
    throwaway_deals: List[EnhancedFlightItinerary] = Field(..., description="甩尾优惠航班列表")
    hub_analysis: Dict[str, Any] = Field(..., description="中转城市分析结果")
    metrics: SearchPhaseResult = Field(..., description="搜索指标")
    disclaimers: List[str] = Field([], description="免责声明")

    model_config = ConfigDict(from_attributes=True)

class UnifiedSearchResponse(BaseModel):
    """统一搜索响应（兼容V1格式）"""
    search_id: str = Field(..., description="搜索ID")
    direct_flights: List[EnhancedFlightItinerary] = Field([], description="直飞航班列表")
    combo_deals: List[EnhancedFlightItinerary] = Field([], description="组合优惠航班列表")
    disclaimers: List[str] = Field([], description="免责声明")
    probe_details: Optional[Dict[str, Any]] = Field(None, description="探测详情")
    phase_metrics: Dict[str, Any] = Field({}, description="阶段指标")
    total_results: int = Field(0, description="总结果数量")

    model_config = ConfigDict(from_attributes=True)

# 搜索状态查询相关schema
class SearchStatusRequest(BaseModel):
    """搜索状态查询请求"""
    search_id: str = Field(..., description="搜索ID")

class SearchStatusResponse(BaseModel):
    """搜索状态查询响应"""
    search_id: str = Field(..., description="搜索ID")
    current_phase: SearchPhase = Field(..., description="当前阶段")
    overall_status: str = Field(..., description="总体状态")
    phases_completed: List[SearchPhase] = Field(..., description="已完成的阶段")
    estimated_completion_time: Optional[datetime] = Field(None, description="预计完成时间")
    partial_results: Optional[Dict[str, Any]] = Field(None, description="部分结果")
    error_info: Optional[Dict[str, str]] = Field(None, description="错误信息")

    model_config = ConfigDict(from_attributes=True)