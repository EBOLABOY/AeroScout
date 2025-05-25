from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import select, insert, delete

from app.database.connection import database
from app.database.models import user_searches_table

async def save_user_search(user_id: int, 
                          from_location: str, 
                          to_location: str, 
                          date: Optional[str] = None,
                          passengers: int = 1) -> int:
    """
    保存用户的搜索记录。

    Args:
        user_id: 用户ID
        from_location: 出发地
        to_location: 目的地
        date: 搜索的日期，格式YYYY-MM-DD
        passengers: 乘客数量

    Returns:
        新创建的搜索记录ID
    """
    query = insert(user_searches_table).values(
        user_id=user_id,
        from_location=from_location,
        to_location=to_location,
        date=date,
        passengers=passengers,
        searched_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc)
    )
    
    last_record_id = await database.execute(query)
    return last_record_id

async def get_user_recent_searches(user_id: int, limit: int = 10) -> List[dict]:
    """
    获取用户的最近搜索记录。

    Args:
        user_id: 用户ID
        limit: 返回记录的最大数量，默认10条

    Returns:
        包含搜索记录的字典列表，按搜索时间倒序排列
    """
    query = (
        select(user_searches_table)
        .where(user_searches_table.c.user_id == user_id)
        .order_by(user_searches_table.c.searched_at.desc())
        .limit(limit)
    )
    
    results = await database.fetch_all(query)
    return [dict(result) for result in results]

async def delete_user_search(search_id: int, user_id: int) -> bool:
    """
    删除用户的搜索记录。

    Args:
        search_id: 搜索记录ID
        user_id: 用户ID（用于验证记录所有权）

    Returns:
        True如果删除成功，False如果记录不存在或不属于该用户
    """
    query = (
        delete(user_searches_table)
        .where(
            user_searches_table.c.id == search_id,
            user_searches_table.c.user_id == user_id
        )
    )
    
    result = await database.execute(query)
    return result > 0  # 如果影响的行数大于0，则说明删除成功