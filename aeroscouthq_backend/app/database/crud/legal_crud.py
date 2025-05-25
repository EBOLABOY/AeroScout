from typing import Dict, List, Optional, Any
from datetime import datetime

from app.database.connection import database
from app.database.models import legal_texts_table

async def get_legal_text(
    text_type: str, 
    subtype: Optional[str] = None,
    version: Optional[str] = None,
    language: str = "zh-CN",
    active_only: bool = True
) -> Optional[Dict[str, Any]]:
    """
    获取法律文本
    
    Args:
        text_type: 文本类型
        subtype: 子类型(可选)
        version: 版本号(可选，默认为最新版本)
        language: 语言代码
        active_only: 是否只获取激活的文本
    
    Returns:
        Dict: 包含法律文本信息的字典，如果未找到则返回None
    """
    query = legal_texts_table.select()
    query = query.where(legal_texts_table.c.type == text_type)
    query = query.where(legal_texts_table.c.language == language)
    
    if subtype:
        query = query.where(legal_texts_table.c.subtype == subtype)
    
    if active_only:
        query = query.where(legal_texts_table.c.is_active == True)
    
    if version:
        query = query.where(legal_texts_table.c.version == version)
        result = await database.fetch_one(query)
    else:
        # 获取最新版本
        query = query.order_by(legal_texts_table.c.version.desc())
        result = await database.fetch_one(query)
    
    if result:
        return dict(result)
    return None

async def get_all_legal_texts(
    text_type: Optional[str] = None,
    subtype: Optional[str] = None,
    language: Optional[str] = None,
    active_only: bool = True
) -> List[Dict[str, Any]]:
    """
    获取所有符合条件的法律文本
    
    Args:
        text_type: 文本类型(可选)
        subtype: 子类型(可选)
        language: 语言代码(可选)
        active_only: 是否只获取激活的文本
    
    Returns:
        List[Dict]: 包含法律文本信息的字典列表
    """
    query = legal_texts_table.select()
    
    if text_type:
        query = query.where(legal_texts_table.c.type == text_type)
    
    if subtype:
        query = query.where(legal_texts_table.c.subtype == subtype)
    
    if language:
        query = query.where(legal_texts_table.c.language == language)
    
    if active_only:
        query = query.where(legal_texts_table.c.is_active == True)
    
    query = query.order_by(
        legal_texts_table.c.type,
        legal_texts_table.c.subtype,
        legal_texts_table.c.version.desc()
    )
    
    result = await database.fetch_all(query)
    return [dict(row) for row in result]

async def create_legal_text(
    text_type: str,
    content: str,
    version: str,
    subtype: Optional[str] = None,
    language: str = "zh-CN",
    is_active: bool = True,
    content_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    创建新的法律文本
    
    Args:
        text_type: 文本类型
        content: 文本内容
        version: 版本号
        subtype: 子类型(可选)
        language: 语言代码
        is_active: 是否激活
        content_path: 文件路径(可选)
    
    Returns:
        Dict: 包含新创建的法律文本信息的字典
    """
    now = datetime.now()
    
    if is_active and subtype:
        # 如果新文本设置为激活，则将同类型、同子类型和同语言的其他文本设置为非激活
        await deactivate_similar_texts(text_type, subtype, language)
    
    query = legal_texts_table.insert().values(
        type=text_type,
        subtype=subtype,
        content=content,
        version=version,
        language=language,
        is_active=is_active,
        content_path=content_path,
        created_at=now,
        updated_at=now
    )
    
    last_id = await database.execute(query)
    
    # 获取并返回新创建的文本
    return await get_legal_text_by_id(last_id)

async def update_legal_text(
    id: int,
    content: Optional[str] = None,
    is_active: Optional[bool] = None,
    content_path: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    更新法律文本
    
    Args:
        id: 法律文本ID
        content: 新的文本内容(可选)
        is_active: 是否激活(可选)
        content_path: 新的文件路径(可选)
    
    Returns:
        Dict: 更新后的法律文本信息字典，如果未找到则返回None
    """
    # 首先获取当前文本信息
    current_text = await get_legal_text_by_id(id)
    if not current_text:
        return None
    
    # 准备更新数据
    data = {"updated_at": datetime.now()}
    if content is not None:
        data["content"] = content
    if content_path is not None:
        data["content_path"] = content_path
    if is_active is not None:
        data["is_active"] = is_active
        if is_active and current_text.get("subtype"):
            # 如果设置为激活，则将同类型、同子类型和同语言的其他文本设置为非激活
            await deactivate_similar_texts(
                current_text["type"], 
                current_text["subtype"], 
                current_text["language"],
                exclude_id=id
            )
    
    # 执行更新
    query = legal_texts_table.update().where(
        legal_texts_table.c.id == id
    ).values(**data)
    await database.execute(query)
    
    # 返回更新后的文本
    return await get_legal_text_by_id(id)

async def get_legal_text_by_id(id: int) -> Optional[Dict[str, Any]]:
    """
    通过ID获取法律文本
    
    Args:
        id: 法律文本ID
    
    Returns:
        Dict: 包含法律文本信息的字典，如果未找到则返回None
    """
    query = legal_texts_table.select().where(legal_texts_table.c.id == id)
    result = await database.fetch_one(query)
    if result:
        return dict(result)
    return None

async def deactivate_similar_texts(
    text_type: str,
    subtype: str,
    language: str,
    exclude_id: Optional[int] = None
) -> None:
    """
    将同类型、同子类型和同语言的文本设置为非激活状态
    
    Args:
        text_type: 文本类型
        subtype: 子类型
        language: 语言代码
        exclude_id: 排除的文本ID(可选)
    """
    query = legal_texts_table.update().where(
        legal_texts_table.c.type == text_type,
        legal_texts_table.c.subtype == subtype,
        legal_texts_table.c.language == language,
        legal_texts_table.c.is_active == True
    ).values(
        is_active=False,
        updated_at=datetime.now()
    )
    
    if exclude_id:
        query = query.where(legal_texts_table.c.id != exclude_id)
    
    await database.execute(query)

async def delete_legal_text(id: int) -> bool:
    """
    删除法律文本
    
    Args:
        id: 法律文本ID
    
    Returns:
        bool: 是否成功删除
    """
    query = legal_texts_table.delete().where(legal_texts_table.c.id == id)
    result = await database.execute(query)
    return result > 0