"""
搜索会话管理器
提供统一的搜索会话管理接口，支持自动切换存储后端
"""

import logging
from typing import Dict, Any, Optional, List
from app.core.config import settings
from app.core.redis_manager import redis_manager
from app.core.search_session_storage import (
    SearchSessionStorage,
    MemorySearchSessionStorage,
    RedisSearchSessionStorage
)

logger = logging.getLogger(__name__)

class SearchSessionManager:
    """搜索会话管理器"""
    
    def __init__(self):
        self._storage: Optional[SearchSessionStorage] = None
        self._use_redis = True  # 默认尝试使用Redis
    
    async def initialize(self) -> None:
        """初始化搜索会话管理器"""
        try:
            if self._use_redis:
                # 尝试使用Redis存储
                redis_client = redis_manager.get_client()
                await redis_client.ping()  # 测试连接
                self._storage = RedisSearchSessionStorage(redis_client)
                logger.info("搜索会话管理器初始化成功 - 使用Redis存储")
            else:
                raise Exception("强制使用内存存储")
                
        except Exception as e:
            # Redis不可用时回退到内存存储
            logger.warning(f"Redis不可用，回退到内存存储: {e}")
            self._storage = MemorySearchSessionStorage()
            self._use_redis = False
            logger.info("搜索会话管理器初始化成功 - 使用内存存储")
    
    def get_storage(self) -> SearchSessionStorage:
        """获取存储实例"""
        if not self._storage:
            raise RuntimeError("搜索会话管理器未初始化")
        return self._storage
    
    def is_using_redis(self) -> bool:
        """是否使用Redis存储"""
        return self._use_redis
    
    async def set_session(self, search_id: str, session_data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """存储搜索会话"""
        return await self.get_storage().set_session(search_id, session_data, ttl)
    
    async def get_session(self, search_id: str) -> Optional[Dict[str, Any]]:
        """获取搜索会话"""
        return await self.get_storage().get_session(search_id)
    
    async def update_session(self, search_id: str, updates: Dict[str, Any]) -> bool:
        """更新搜索会话"""
        return await self.get_storage().update_session(search_id, updates)
    
    async def delete_session(self, search_id: str) -> bool:
        """删除搜索会话"""
        return await self.get_storage().delete_session(search_id)
    
    async def exists(self, search_id: str) -> bool:
        """检查搜索会话是否存在"""
        return await self.get_storage().exists(search_id)
    
    async def list_sessions(self, pattern: str = "*") -> List[str]:
        """列出搜索会话ID"""
        return await self.get_storage().list_sessions(pattern)
    
    async def cleanup_expired(self) -> int:
        """清理过期的搜索会话"""
        return await self.get_storage().cleanup_expired()
    
    async def get_session_info(self, search_id: str) -> Optional[Dict[str, Any]]:
        """获取搜索会话信息（包含元数据）"""
        session = await self.get_session(search_id)
        if not session:
            return None
        
        info = {
            'search_id': search_id,
            'exists': True,
            'storage_type': 'redis' if self._use_redis else 'memory',
            'created_at': session.get('_created_at'),
            'updated_at': session.get('_updated_at'),
            'status': session.get('status', 'unknown'),
            'phase': session.get('phase', 'unknown'),
            'results_count': session.get('results_count', 0)
        }
        
        # 如果使用Redis，添加TTL信息
        if self._use_redis and isinstance(self._storage, RedisSearchSessionStorage):
            ttl = await self._storage.get_session_ttl(search_id)
            info['ttl_seconds'] = ttl if ttl > 0 else None
        
        return info
    
    async def extend_session_ttl(self, search_id: str, additional_seconds: int = 3600) -> bool:
        """延长搜索会话TTL（仅Redis支持）"""
        if self._use_redis and isinstance(self._storage, RedisSearchSessionStorage):
            return await self._storage.extend_session_ttl(search_id, additional_seconds)
        return False
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 测试存储功能
            test_id = "health_check_test"
            test_data = {"test": True, "timestamp": "2024-01-01T00:00:00Z"}
            
            # 测试写入
            write_success = await self.set_session(test_id, test_data, 60)
            
            # 测试读取
            read_data = await self.get_session(test_id) if write_success else None
            read_success = read_data is not None and read_data.get("test") is True
            
            # 测试删除
            delete_success = await self.delete_session(test_id) if read_success else False
            
            return {
                'status': 'healthy' if (write_success and read_success and delete_success) else 'unhealthy',
                'storage_type': 'redis' if self._use_redis else 'memory',
                'write_test': write_success,
                'read_test': read_success,
                'delete_test': delete_success,
                'redis_available': self._use_redis
            }
            
        except Exception as e:
            logger.error(f"搜索会话管理器健康检查失败: {e}")
            return {
                'status': 'unhealthy',
                'storage_type': 'redis' if self._use_redis else 'memory',
                'error': str(e),
                'redis_available': self._use_redis
            }

# 全局搜索会话管理器实例
search_session_manager = SearchSessionManager()

async def get_search_session_manager() -> SearchSessionManager:
    """获取搜索会话管理器的依赖注入函数"""
    return search_session_manager
