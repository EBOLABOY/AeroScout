"""
Token 调度器

负责在应用启动时预获取 token（可选）
改为按需获取策略，避免频繁请求
"""

import asyncio
import logging
from typing import Optional
import time

from app.core.config import settings
from app.core.dynamic_fetcher import _get_fresh_kiwi_headers_sync
import app.core.dynamic_fetcher as df  # 导入模块以访问全局变量

logger = logging.getLogger(__name__)

class TokenScheduler:
    """Token 预获取调度器（简化版，无定时刷新）"""
    
    def __init__(self):
        self.is_running = False
    
    async def start(self):
        """启动 token 调度器（仅尝试预获取）"""
        logger.info("启动 Token 调度器（按需获取模式）...")
        self.is_running = True
        
        # 尝试预获取一次 Kiwi token（失败不影响应用启动）
        success = await self._try_fetch_kiwi_token_once()
        
        if success:
            logger.info("Token 调度器启动完成 - 预获取成功")
        else:
            logger.info("Token 调度器启动完成 - 预获取失败，将依赖按需获取")
    
    async def stop(self):
        """停止 token 调度器"""
        logger.info("停止 Token 调度器...")
        self.is_running = False
        logger.info("Token 调度器已停止")
    
    async def _try_fetch_kiwi_token_once(self) -> bool:
        """尝试获取一次 Kiwi token（失败不抛出异常）"""
        logger.info("尝试预获取 Kiwi token...")
        try:
            headers = await _get_fresh_kiwi_headers_sync()
            if headers and 'kw-umbrella-token' in headers:
                # 更新全局变量
                df.KIWI_CURRENT_HEADERS = headers.copy()
                df.KIWI_LAST_FETCH_TIME = time.time()
                
                # 保存到文件缓存
                import json
                try:
                    with open(settings.KIWI_TOKEN_FILE, 'w') as f:
                        json.dump(headers, f, indent=2)
                    logger.info(f"Kiwi token 预获取成功，已保存到缓存: {settings.KIWI_TOKEN_FILE}")
                except Exception as e:
                    logger.warning(f"Kiwi token 获取成功但保存失败: {e}")
                
                return True
            else:
                logger.warning("Kiwi token 预获取失败：未获取到有效 token")
                return False
        except Exception as e:
            logger.warning(f"Kiwi token 预获取异常: {e}")
            return False

# 全局调度器实例
_token_scheduler: Optional[TokenScheduler] = None

async def start_token_scheduler():
    """启动全局 token 调度器"""
    global _token_scheduler
    
    if _token_scheduler is None:
        _token_scheduler = TokenScheduler()
    
    await _token_scheduler.start()

async def stop_token_scheduler():
    """停止全局 token 调度器"""
    global _token_scheduler
    
    if _token_scheduler:
        await _token_scheduler.stop()

def get_token_scheduler() -> Optional[TokenScheduler]:
    """获取全局 token 调度器实例"""
    return _token_scheduler 