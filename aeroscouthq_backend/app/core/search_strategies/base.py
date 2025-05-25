"""
搜索策略基础类和模型定义
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional, Set
from enum import Enum
import logging

from app.apis.v1.schemas.flights_v2 import (
    FlightSearchBaseRequest,
    EnhancedFlightItinerary,
    SearchPhase
)

logger = logging.getLogger(__name__)

class SearchResultStatus(str, Enum):
    """搜索结果状态"""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILED = "failed"
    CACHED = "cached"

@dataclass
class SearchContext:
    """搜索上下文，包含搜索过程中的共享信息"""
    request: FlightSearchBaseRequest
    search_id: str
    phase: SearchPhase
    started_at: datetime
    cache_enabled: bool = True
    kiwi_headers: Optional[Dict[str, str]] = None
    api_call_count: int = 0
    cache_hits: int = 0
    total_cache_attempts: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def increment_api_calls(self, count: int = 1):
        """增加API调用计数"""
        self.api_call_count += count

    def record_cache_hit(self):
        """记录缓存命中"""
        self.cache_hits += 1
        self.total_cache_attempts += 1

    def record_cache_miss(self):
        """记录缓存未命中"""
        self.total_cache_attempts += 1

    @property
    def cache_hit_rate(self) -> float:
        """计算缓存命中率"""
        if self.total_cache_attempts == 0:
            return 0.0
        return self.cache_hits / self.total_cache_attempts

@dataclass
class SearchResult:
    """搜索结果封装"""
    status: SearchResultStatus
    flights: List[EnhancedFlightItinerary]
    execution_time_ms: int
    error_message: Optional[str] = None
    cache_hit: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    disclaimers: List[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """是否成功"""
        return self.status in [SearchResultStatus.SUCCESS, SearchResultStatus.PARTIAL_SUCCESS, SearchResultStatus.CACHED]

    @property
    def has_results(self) -> bool:
        """是否有结果"""
        return len(self.flights) > 0

    @property
    def metrics(self) -> Dict[str, Any]:
        """
        兼容性属性：提供metrics接口
        将execution_time_ms映射到search_time_ms，并包含其他指标
        """
        return {
            "search_time_ms": self.execution_time_ms,
            "execution_time_ms": self.execution_time_ms,
            "cache_hit": self.cache_hit,
            "results_count": len(self.flights),
            "status": self.status.value,
            **self.metadata  # 包含额外的元数据
        }

class SearchStrategy(ABC):
    """搜索策略抽象基类"""

    def __init__(self, strategy_name: str):
        self.strategy_name = strategy_name
        self.logger = logging.getLogger(f"{__name__}.{strategy_name}")

    @abstractmethod
    async def execute(self, context: SearchContext) -> SearchResult:
        """
        执行搜索策略

        Args:
            context: 搜索上下文

        Returns:
            SearchResult: 搜索结果
        """
        pass

    @abstractmethod
    def can_execute(self, context: SearchContext) -> bool:
        """
        检查是否可以执行此策略

        Args:
            context: 搜索上下文

        Returns:
            bool: 是否可以执行
        """
        pass

    def get_cache_key(self, context: SearchContext) -> str:
        """
        生成缓存键

        Args:
            context: 搜索上下文

        Returns:
            str: 缓存键
        """
        request = context.request
        key_parts = [
            self.strategy_name,
            request.origin_iata,
            request.destination_iata,
            request.departure_date_from,
            request.departure_date_to,
            request.cabin_class,
            str(request.adults),
            request.preferred_currency
        ]

        # 为往返票添加返程日期
        if request.return_date_from:
            key_parts.extend([request.return_date_from, request.return_date_to or ""])

        return f"flight_search:{':'.join(key_parts)}"

    async def _validate_request(self, context: SearchContext) -> bool:
        """
        验证请求参数

        Args:
            context: 搜索上下文

        Returns:
            bool: 验证是否通过
        """
        request = context.request

        # 基础验证
        if not request.origin_iata or not request.destination_iata:
            self.logger.error(f"[{context.search_id}] 缺少起始地或目的地")
            return False

        if request.origin_iata == request.destination_iata:
            self.logger.error(f"[{context.search_id}] 起始地和目的地不能相同")
            return False

        # 日期验证
        try:
            from datetime import datetime
            departure_from = datetime.strptime(request.departure_date_from, "%Y-%m-%d")
            departure_to = datetime.strptime(request.departure_date_to, "%Y-%m-%d")

            if departure_from > departure_to:
                self.logger.error(f"[{context.search_id}] 出发日期范围无效")
                return False

            # 检查往返票日期
            if request.return_date_from:
                return_from = datetime.strptime(request.return_date_from, "%Y-%m-%d")
                if return_from < departure_from:
                    self.logger.error(f"[{context.search_id}] 返程日期不能早于出发日期")
                    return False

        except ValueError as e:
            self.logger.error(f"[{context.search_id}] 日期格式错误: {e}")
            return False

        return True

    def _enhance_flight_with_metadata(
        self,
        flight: EnhancedFlightItinerary,
        context: SearchContext,
        additional_metadata: Optional[Dict[str, Any]] = None
    ) -> EnhancedFlightItinerary:
        """
        为航班添加策略相关的元数据

        Args:
            flight: 航班信息
            context: 搜索上下文
            additional_metadata: 额外的元数据

        Returns:
            EnhancedFlightItinerary: 增强后的航班信息
        """
        # 设置搜索阶段
        flight.search_phase = context.phase

        # 添加策略特定的元数据
        if additional_metadata:
            if not flight.raw_data:
                flight.raw_data = {}
            flight.raw_data.update({
                "strategy_name": self.strategy_name,
                "search_id": context.search_id,
                **additional_metadata
            })

        return flight

    def _calculate_quality_score(self, flight: EnhancedFlightItinerary) -> float:
        """
        计算航班质量评分

        Args:
            flight: 航班信息

        Returns:
            float: 质量评分 (0-100)
        """
        score = 50.0  # 基础分数

        # 价格因素 (30分)
        # 这里需要根据历史数据或市场平均价格来评估
        # 暂时使用简单的逻辑
        if flight.price <= 1000:  # CNY
            score += 30
        elif flight.price <= 3000:
            score += 20
        elif flight.price <= 5000:
            score += 10

        # 时长因素 (20分)
        if hasattr(flight, 'total_duration_minutes'):
            duration_hours = flight.total_duration_minutes / 60
            if duration_hours <= 2:
                score += 20
            elif duration_hours <= 5:
                score += 15
            elif duration_hours <= 10:
                score += 10

        # 直飞加分 (20分)
        if len(flight.segments or []) == 1:
            score += 20

        # 航空公司和舱位因素 (10分)
        if flight.segments:
            # 优质航空公司加分
            preferred_carriers = {'CA', 'MU', 'CZ', 'SQ', 'CX', 'EK', 'QR'}
            if any(seg.carrier_code in preferred_carriers for seg in flight.segments):
                score += 5

            # 商务舱/头等舱加分
            if any(seg.cabin_class in ['BUSINESS', 'FIRST'] for seg in flight.segments):
                score += 5

        # 风险因素扣分 (最多-20分)
        if flight.risk_factors:
            score -= min(len(flight.risk_factors) * 5, 20)

        # 确保分数在0-100范围内
        return max(0.0, min(100.0, score))

    async def _log_execution_start(self, context: SearchContext):
        """记录策略执行开始"""
        self.logger.debug(
            f"[{context.search_id}] 开始执行搜索策略: {self.strategy_name} "
            f"({context.request.origin_iata} -> {context.request.destination_iata})"
        )

    async def _log_execution_end(self, context: SearchContext, result: SearchResult):
        """记录策略执行结束"""
        self.logger.debug(
            f"[{context.search_id}] 搜索策略完成: {self.strategy_name} "
            f"状态: {result.status}, 结果数: {len(result.flights)}, "
            f"用时: {result.execution_time_ms}ms"
        )