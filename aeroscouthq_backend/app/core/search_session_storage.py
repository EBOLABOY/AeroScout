"""
搜索会话存储抽象接口和实现
支持内存存储和Redis存储
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)

class SearchSessionStorage(ABC):
    """搜索会话存储抽象基类"""

    @abstractmethod
    async def set_session(self, search_id: str, session_data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        存储搜索会话数据

        Args:
            search_id: 搜索ID
            session_data: 会话数据
            ttl: 过期时间（秒），None表示使用默认值

        Returns:
            bool: 是否成功存储
        """
        pass

    @abstractmethod
    async def get_session(self, search_id: str) -> Optional[Dict[str, Any]]:
        """
        获取搜索会话数据

        Args:
            search_id: 搜索ID

        Returns:
            Optional[Dict[str, Any]]: 会话数据，不存在时返回None
        """
        pass

    @abstractmethod
    async def update_session(self, search_id: str, updates: Dict[str, Any]) -> bool:
        """
        更新搜索会话数据

        Args:
            search_id: 搜索ID
            updates: 要更新的数据

        Returns:
            bool: 是否成功更新
        """
        pass

    @abstractmethod
    async def delete_session(self, search_id: str) -> bool:
        """
        删除搜索会话

        Args:
            search_id: 搜索ID

        Returns:
            bool: 是否成功删除
        """
        pass

    @abstractmethod
    async def exists(self, search_id: str) -> bool:
        """
        检查搜索会话是否存在

        Args:
            search_id: 搜索ID

        Returns:
            bool: 是否存在
        """
        pass

    @abstractmethod
    async def list_sessions(self, pattern: str = "*") -> List[str]:
        """
        列出搜索会话ID

        Args:
            pattern: 匹配模式

        Returns:
            List[str]: 搜索ID列表
        """
        pass

    @abstractmethod
    async def cleanup_expired(self) -> int:
        """
        清理过期的搜索会话

        Returns:
            int: 清理的会话数量
        """
        pass

class MemorySearchSessionStorage(SearchSessionStorage):
    """内存搜索会话存储实现"""

    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._max_sessions = 1000  # 最大会话数

    async def set_session(self, search_id: str, session_data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """存储搜索会话数据到内存"""
        try:
            # 添加时间戳
            session_data = session_data.copy()
            session_data['_created_at'] = datetime.now(timezone.utc).isoformat()
            if ttl:
                session_data['_expires_at'] = datetime.now(timezone.utc).timestamp() + ttl

            self._sessions[search_id] = session_data

            # 简单的内存清理策略
            if len(self._sessions) > self._max_sessions:
                await self._cleanup_old_sessions()

            return True
        except Exception as e:
            logger.error(f"内存存储会话失败 {search_id}: {e}")
            return False

    async def get_session(self, search_id: str) -> Optional[Dict[str, Any]]:
        """从内存获取搜索会话数据"""
        session = self._sessions.get(search_id)
        if not session:
            return None

        # 检查是否过期
        if '_expires_at' in session:
            if datetime.now(timezone.utc).timestamp() > session['_expires_at']:
                await self.delete_session(search_id)
                return None

        return session

    async def update_session(self, search_id: str, updates: Dict[str, Any]) -> bool:
        """更新内存中的搜索会话数据"""
        try:
            if search_id not in self._sessions:
                return False

            self._sessions[search_id].update(updates)
            self._sessions[search_id]['_updated_at'] = datetime.now(timezone.utc).isoformat()
            return True
        except Exception as e:
            logger.error(f"内存更新会话失败 {search_id}: {e}")
            return False

    async def delete_session(self, search_id: str) -> bool:
        """从内存删除搜索会话"""
        try:
            if search_id in self._sessions:
                del self._sessions[search_id]
                return True
            return False
        except Exception as e:
            logger.error(f"内存删除会话失败 {search_id}: {e}")
            return False

    async def exists(self, search_id: str) -> bool:
        """检查内存中是否存在搜索会话"""
        return search_id in self._sessions

    async def list_sessions(self, pattern: str = "*") -> List[str]:
        """列出内存中的搜索会话ID"""
        if pattern == "*":
            return list(self._sessions.keys())

        # 简单的模式匹配
        import fnmatch
        return [sid for sid in self._sessions.keys() if fnmatch.fnmatch(sid, pattern)]

    async def cleanup_expired(self) -> int:
        """清理过期的内存会话"""
        current_time = datetime.now(timezone.utc).timestamp()
        expired_sessions = []

        for search_id, session in self._sessions.items():
            if '_expires_at' in session and current_time > session['_expires_at']:
                expired_sessions.append(search_id)

        for search_id in expired_sessions:
            await self.delete_session(search_id)

        return len(expired_sessions)

    async def _cleanup_old_sessions(self):
        """清理旧的会话以释放内存"""
        # 保留最近的500个会话
        sessions_with_time = [
            (sid, session.get('_created_at', ''))
            for sid, session in self._sessions.items()
        ]

        # 按创建时间排序，保留最新的500个
        sessions_with_time.sort(key=lambda x: x[1], reverse=True)
        sessions_to_keep = sessions_with_time[:500]

        # 重建会话字典
        self._sessions = {
            sid: self._sessions[sid]
            for sid, _ in sessions_to_keep
        }

class RedisSearchSessionStorage(SearchSessionStorage):
    """Redis搜索会话存储实现"""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.key_prefix = "search_session:"
        self.default_ttl = settings.REDIS_SESSION_TTL

    def _make_key(self, search_id: str) -> str:
        """生成Redis键名"""
        return f"{self.key_prefix}{search_id}"

    def _serialize_data(self, data: Dict[str, Any]) -> str:
        """序列化数据为JSON字符串"""
        def json_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        return json.dumps(data, default=json_serializer, ensure_ascii=False)

    def _deserialize_data(self, data: str) -> Dict[str, Any]:
        """反序列化JSON字符串为数据"""
        return json.loads(data)

    async def set_session(self, search_id: str, session_data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """存储搜索会话数据到Redis"""
        try:
            key = self._make_key(search_id)

            # 添加元数据
            session_data = session_data.copy()
            session_data['_created_at'] = datetime.now(timezone.utc).isoformat()
            session_data['_search_id'] = search_id

            # 序列化数据
            serialized_data = self._serialize_data(session_data)

            # 设置TTL
            expire_time = ttl or self.default_ttl

            # 存储到Redis
            await self.redis.setex(key, expire_time, serialized_data)

            logger.debug(f"Redis存储会话成功: {search_id}, TTL: {expire_time}s")
            return True

        except Exception as e:
            logger.error(f"Redis存储会话失败 {search_id}: {e}")
            return False

    async def get_session(self, search_id: str) -> Optional[Dict[str, Any]]:
        """从Redis获取搜索会话数据"""
        try:
            key = self._make_key(search_id)
            data = await self.redis.get(key)

            if not data:
                return None

            return self._deserialize_data(data)

        except Exception as e:
            logger.error(f"Redis获取会话失败 {search_id}: {e}")
            return None

    async def update_session(self, search_id: str, updates: Dict[str, Any]) -> bool:
        """更新Redis中的搜索会话数据"""
        try:
            # 获取现有数据
            existing_data = await self.get_session(search_id)
            if not existing_data:
                return False

            # 更新数据
            existing_data.update(updates)
            existing_data['_updated_at'] = datetime.now(timezone.utc).isoformat()

            # 获取剩余TTL
            key = self._make_key(search_id)
            ttl = await self.redis.ttl(key)
            if ttl <= 0:
                ttl = self.default_ttl

            # 重新存储
            return await self.set_session(search_id, existing_data, ttl)

        except Exception as e:
            logger.error(f"Redis更新会话失败 {search_id}: {e}")
            return False

    async def delete_session(self, search_id: str) -> bool:
        """从Redis删除搜索会话"""
        try:
            key = self._make_key(search_id)
            result = await self.redis.delete(key)
            return result > 0

        except Exception as e:
            logger.error(f"Redis删除会话失败 {search_id}: {e}")
            return False

    async def exists(self, search_id: str) -> bool:
        """检查Redis中是否存在搜索会话"""
        try:
            key = self._make_key(search_id)
            return await self.redis.exists(key) > 0

        except Exception as e:
            logger.error(f"Redis检查会话存在失败 {search_id}: {e}")
            return False

    async def list_sessions(self, pattern: str = "*") -> List[str]:
        """列出Redis中的搜索会话ID"""
        try:
            key_pattern = f"{self.key_prefix}{pattern}"
            keys = await self.redis.keys(key_pattern)

            # 提取搜索ID（去掉前缀）
            search_ids = [
                key.replace(self.key_prefix, "")
                for key in keys
            ]

            return search_ids

        except Exception as e:
            logger.error(f"Redis列出会话失败: {e}")
            return []

    async def cleanup_expired(self) -> int:
        """清理过期的Redis会话（Redis自动处理TTL，这里返回0）"""
        # Redis会自动清理过期的键，所以这里不需要手动清理
        return 0

    async def get_session_ttl(self, search_id: str) -> int:
        """获取会话的剩余TTL"""
        try:
            key = self._make_key(search_id)
            return await self.redis.ttl(key)
        except Exception as e:
            logger.error(f"Redis获取TTL失败 {search_id}: {e}")
            return -1

    async def extend_session_ttl(self, search_id: str, additional_seconds: int) -> bool:
        """延长会话TTL"""
        try:
            key = self._make_key(search_id)
            current_ttl = await self.redis.ttl(key)
            if current_ttl > 0:
                new_ttl = current_ttl + additional_seconds
                return await self.redis.expire(key, new_ttl)
            return False
        except Exception as e:
            logger.error(f"Redis延长TTL失败 {search_id}: {e}")
            return False
