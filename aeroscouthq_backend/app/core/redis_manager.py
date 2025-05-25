"""
Redis连接管理器
负责管理Redis连接池和提供Redis客户端实例
"""

import logging
import redis.asyncio as redis
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisManager:
    """Redis连接管理器"""
    
    def __init__(self):
        self._pool: Optional[redis.ConnectionPool] = None
        self._client: Optional[redis.Redis] = None
    
    async def initialize(self) -> None:
        """初始化Redis连接池"""
        try:
            # 创建连接池
            self._pool = redis.ConnectionPool.from_url(
                settings.REDIS_URL,
                decode_responses=True,  # 自动解码响应为字符串
                max_connections=20,     # 最大连接数
                retry_on_timeout=True,  # 超时重试
                socket_connect_timeout=5,  # 连接超时
                socket_timeout=5,       # 读写超时
                health_check_interval=30  # 健康检查间隔
            )
            
            # 创建Redis客户端
            self._client = redis.Redis(connection_pool=self._pool)
            
            # 测试连接
            await self._client.ping()
            logger.info("Redis连接初始化成功")
            
        except Exception as e:
            logger.error(f"Redis连接初始化失败: {e}")
            raise
    
    async def close(self) -> None:
        """关闭Redis连接"""
        try:
            if self._client:
                await self._client.close()
                logger.info("Redis连接已关闭")
        except Exception as e:
            logger.error(f"关闭Redis连接时出错: {e}")
    
    def get_client(self) -> redis.Redis:
        """获取Redis客户端实例"""
        if not self._client:
            raise RuntimeError("Redis客户端未初始化，请先调用initialize()")
        return self._client
    
    async def health_check(self) -> bool:
        """Redis健康检查"""
        try:
            if not self._client:
                return False
            
            await self._client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis健康检查失败: {e}")
            return False

# 全局Redis管理器实例
redis_manager = RedisManager()

async def get_redis_client() -> redis.Redis:
    """获取Redis客户端的依赖注入函数"""
    return redis_manager.get_client()
