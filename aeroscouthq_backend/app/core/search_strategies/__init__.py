"""
搜索策略模块

提供可扩展的航班搜索策略框架，支持不同的搜索算法和策略组合。
"""

from .base import SearchStrategy, SearchContext, SearchResult
from .direct_flight import DirectFlightStrategy
from .hidden_city import HiddenCityStrategy
from .hub_probe import HubProbeStrategy

__all__ = [
    "SearchStrategy",
    "SearchContext", 
    "SearchResult",
    "DirectFlightStrategy",
    "HiddenCityStrategy",
    "HubProbeStrategy"
] 