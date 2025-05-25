"""
任务状态管理器

用于跟踪和管理 Playwright 任务的执行状态，解决异步任务与主任务之间的同步问题。
主要功能：
- 跟踪任务运行状态（running/completed/failed）
- 防止重复启动相同类型的任务
- 提供智能等待机制
- 自动清理过期状态
"""

import json
import time
import logging
import threading
from pathlib import Path
from typing import Dict, Any, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class TaskStatusManager:
    """
    任务状态管理器
    
    使用文件系统存储任务状态，支持多进程/多线程安全访问
    """
    
    def __init__(self, status_file_path: str, expiry_seconds: int = 300):
        """
        初始化任务状态管理器
        
        Args:
            status_file_path: 状态文件路径
            expiry_seconds: 状态过期时间（秒）
        """
        self.status_file_path = Path(status_file_path)
        self.expiry_seconds = expiry_seconds
        self._lock = threading.Lock()
        
        # 确保状态文件目录存在
        self.status_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 初始化时清理过期状态
        self.cleanup_expired_status()
    
    @contextmanager
    def _file_lock(self):
        """文件锁上下文管理器"""
        with self._lock:
            yield
    
    def _read_status_file(self) -> Dict[str, Any]:
        """
        读取状态文件
        
        Returns:
            状态字典，如果文件不存在或格式错误则返回空字典
        """
        try:
            if self.status_file_path.exists():
                with open(self.status_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
                    else:
                        logger.warning(f"状态文件格式错误: {self.status_file_path}")
                        return {}
            else:
                return {}
        except Exception as e:
            logger.error(f"读取状态文件失败 {self.status_file_path}: {e}")
            return {}
    
    def _write_status_file(self, data: Dict[str, Any]) -> bool:
        """
        写入状态文件
        
        Args:
            data: 要写入的状态数据
            
        Returns:
            是否写入成功
        """
        try:
            with open(self.status_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"写入状态文件失败 {self.status_file_path}: {e}")
            return False
    
    def set_task_running(self, task_type: str, task_id: str) -> bool:
        """
        设置任务为运行状态
        
        Args:
            task_type: 任务类型（如 "kiwi", "trip"）
            task_id: 任务ID
            
        Returns:
            是否设置成功（如果已有运行中的任务则返回 False）
        """
        with self._file_lock():
            status_data = self._read_status_file()
            
            # 检查是否已有运行中的任务
            if task_type in status_data:
                existing_status = status_data[task_type]
                if existing_status.get("status") == "running":
                    # 检查任务是否过期
                    start_time = existing_status.get("start_time", 0)
                    if time.time() - start_time < self.expiry_seconds:
                        logger.info(f"任务类型 {task_type} 已有运行中的任务: {existing_status.get('task_id')}")
                        return False
                    else:
                        logger.warning(f"任务类型 {task_type} 的运行中任务已过期，将被替换")
            
            # 设置新的运行状态
            status_data[task_type] = {
                "status": "running",
                "task_id": task_id,
                "start_time": time.time(),
                "end_time": None,
                "result": None,
                "error": None
            }
            
            success = self._write_status_file(status_data)
            if success:
                logger.info(f"设置任务 {task_type}:{task_id} 为运行状态")
            return success
    
    def set_task_completed(self, task_type: str, task_id: str, result: Optional[Dict[str, Any]] = None) -> None:
        """
        设置任务为完成状态
        
        Args:
            task_type: 任务类型
            task_id: 任务ID
            result: 任务结果
        """
        with self._file_lock():
            status_data = self._read_status_file()
            
            if task_type in status_data and status_data[task_type].get("task_id") == task_id:
                status_data[task_type].update({
                    "status": "completed",
                    "end_time": time.time(),
                    "result": result,
                    "error": None
                })
                
                if self._write_status_file(status_data):
                    logger.info(f"设置任务 {task_type}:{task_id} 为完成状态")
                else:
                    logger.error(f"写入任务完成状态失败: {task_type}:{task_id}")
            else:
                logger.warning(f"尝试设置不存在或ID不匹配的任务为完成状态: {task_type}:{task_id}")
    
    def set_task_failed(self, task_type: str, task_id: str, error: str) -> None:
        """
        设置任务为失败状态
        
        Args:
            task_type: 任务类型
            task_id: 任务ID
            error: 错误信息
        """
        with self._file_lock():
            status_data = self._read_status_file()
            
            if task_type in status_data and status_data[task_type].get("task_id") == task_id:
                status_data[task_type].update({
                    "status": "failed",
                    "end_time": time.time(),
                    "result": None,
                    "error": error
                })
                
                if self._write_status_file(status_data):
                    logger.info(f"设置任务 {task_type}:{task_id} 为失败状态: {error}")
                else:
                    logger.error(f"写入任务失败状态失败: {task_type}:{task_id}")
            else:
                logger.warning(f"尝试设置不存在或ID不匹配的任务为失败状态: {task_type}:{task_id}")
    
    def get_task_status(self, task_type: str) -> Optional[Dict[str, Any]]:
        """
        获取任务状态
        
        Args:
            task_type: 任务类型
            
        Returns:
            任务状态字典，如果不存在则返回 None
        """
        with self._file_lock():
            status_data = self._read_status_file()
            return status_data.get(task_type)
    
    def is_task_running(self, task_type: str) -> bool:
        """
        检查任务是否正在运行
        
        Args:
            task_type: 任务类型
            
        Returns:
            是否正在运行
        """
        status = self.get_task_status(task_type)
        if not status:
            return False
        
        if status.get("status") != "running":
            return False
        
        # 检查是否过期
        start_time = status.get("start_time", 0)
        if time.time() - start_time >= self.expiry_seconds:
            logger.warning(f"任务 {task_type} 运行时间过长，视为已过期")
            return False
        
        return True
    
    def cleanup_expired_status(self) -> int:
        """
        清理过期的任务状态
        
        Returns:
            清理的任务数量
        """
        with self._file_lock():
            status_data = self._read_status_file()
            current_time = time.time()
            cleaned_count = 0
            
            tasks_to_remove = []
            for task_type, task_info in status_data.items():
                # 检查任务是否过期
                start_time = task_info.get("start_time", 0)
                end_time = task_info.get("end_time")
                
                # 对于已完成/失败的任务，使用 end_time；对于运行中的任务，使用 start_time
                check_time = end_time if end_time else start_time
                
                if current_time - check_time >= self.expiry_seconds:
                    tasks_to_remove.append(task_type)
                    cleaned_count += 1
            
            # 移除过期任务
            for task_type in tasks_to_remove:
                del status_data[task_type]
                logger.info(f"清理过期任务状态: {task_type}")
            
            if cleaned_count > 0:
                self._write_status_file(status_data)
                logger.info(f"清理了 {cleaned_count} 个过期任务状态")
            
            return cleaned_count
    
    def get_all_status(self) -> Dict[str, Any]:
        """
        获取所有任务状态
        
        Returns:
            所有任务状态字典
        """
        return self._read_status_file()


# 全局实例（延迟初始化）
_task_status_manager: Optional[TaskStatusManager] = None

def get_task_status_manager() -> TaskStatusManager:
    """
    获取全局任务状态管理器实例
    
    Returns:
        TaskStatusManager 实例
    """
    global _task_status_manager
    
    if _task_status_manager is None:
        # 延迟导入配置，避免循环导入
        try:
            from app.core.config import settings
            status_file = getattr(settings, 'KIWI_TASK_STATUS_FILE', 'cache/.kiwi_task_status.json')
            expiry_seconds = getattr(settings, 'KIWI_TASK_STATUS_EXPIRY', 300)
        except ImportError:
            # 如果无法导入配置，使用默认值
            status_file = 'cache/.kiwi_task_status.json'
            expiry_seconds = 300
            logger.warning("无法导入配置，使用默认的任务状态管理器设置")
        
        _task_status_manager = TaskStatusManager(status_file, expiry_seconds)
    
    return _task_status_manager 