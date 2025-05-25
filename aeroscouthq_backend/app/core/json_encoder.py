"""
自定义 JSON 编码器，用于处理 Celery 任务中的特殊数据类型序列化
主要解决 datetime 对象的序列化问题，避免 EncodeError
"""

import json
from datetime import datetime, date, time
from decimal import Decimal
from uuid import UUID
from typing import Any


class CeleryJSONEncoder(json.JSONEncoder):
    """
    自定义 JSON 编码器，用于 Celery 任务结果序列化
    处理 datetime、date、time、Decimal、UUID 等特殊类型
    """
    
    def default(self, obj: Any) -> Any:
        """
        将特殊类型转换为 JSON 可序列化的格式
        
        Args:
            obj: 需要序列化的对象
            
        Returns:
            JSON 可序列化的对象
        """
        if isinstance(obj, datetime):
            # 将 datetime 转换为 ISO 格式字符串
            return obj.isoformat()
        elif isinstance(obj, date):
            # 将 date 转换为 ISO 格式字符串
            return obj.isoformat()
        elif isinstance(obj, time):
            # 将 time 转换为 ISO 格式字符串
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            # 将 Decimal 转换为 float
            return float(obj)
        elif isinstance(obj, UUID):
            # 将 UUID 转换为字符串
            return str(obj)
        elif hasattr(obj, 'model_dump'):
            # 处理 Pydantic 模型，使用 JSON 模式序列化
            return obj.model_dump(mode='json')
        elif hasattr(obj, '__dict__'):
            # 处理其他对象，转换为字典
            return obj.__dict__
        
        # 对于无法处理的类型，调用父类方法（会抛出 TypeError）
        return super().default(obj)


def safe_json_dumps(obj: Any, **kwargs) -> str:
    """
    安全的 JSON 序列化函数，使用自定义编码器
    
    Args:
        obj: 需要序列化的对象
        **kwargs: 传递给 json.dumps 的其他参数
        
    Returns:
        JSON 字符串
    """
    return json.dumps(obj, cls=CeleryJSONEncoder, ensure_ascii=False, **kwargs)


def safe_json_loads(json_str: str, **kwargs) -> Any:
    """
    安全的 JSON 反序列化函数
    
    Args:
        json_str: JSON 字符串
        **kwargs: 传递给 json.loads 的其他参数
        
    Returns:
        反序列化后的对象
    """
    return json.loads(json_str, **kwargs) 