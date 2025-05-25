from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.apis.v1.schemas.legal_schemas import (
    LegalTextCreate,
    LegalTextUpdate,
    LegalTextResponse,
    LegalTextQuery
)
from app.database.crud import legal_crud
from app.core.dependencies import get_current_active_user, get_current_admin_user
from app.apis.v1.schemas import UserResponse

router = APIRouter()

@router.get("/content", response_model=LegalTextResponse)
async def get_legal_text(
    type: str = Query(..., description="文本类型"),
    subtype: Optional[str] = Query(None, description="子类型（可选）"),
    version: Optional[str] = Query(None, description="版本号（可选，默认为最新版本）"),
    language: str = Query("zh-CN", description="语言代码")
):
    """
    获取法律文本
    
    - **type**: 文本类型，如disclaimer, risk_confirmation, privacy_policy, terms_of_service
    - **subtype**: 子类型，如a-b, a-b-x（可选）
    - **version**: 版本号（可选，默认为最新版本）
    - **language**: 语言代码（默认为zh-CN）
    """
    legal_text = await legal_crud.get_legal_text(
        text_type=type,
        subtype=subtype,
        version=version,
        language=language,
        active_only=True
    )
    
    if not legal_text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到指定的法律文本: {type}"
        )
    
    return legal_text

@router.get("/admin/content", response_model=List[LegalTextResponse])
async def get_all_legal_texts(
    type: Optional[str] = Query(None, description="文本类型（可选）"),
    subtype: Optional[str] = Query(None, description="子类型（可选）"),
    language: Optional[str] = Query(None, description="语言代码（可选）"),
    active_only: bool = Query(True, description="是否只获取激活的文本"),
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """
    获取所有法律文本（管理员）
    
    - **type**: 文本类型（可选）
    - **subtype**: 子类型（可选）
    - **language**: 语言代码（可选）
    - **active_only**: 是否只获取激活的文本（默认为True）
    """
    legal_texts = await legal_crud.get_all_legal_texts(
        text_type=type,
        subtype=subtype,
        language=language,
        active_only=active_only
    )
    
    return legal_texts

@router.post("/admin/content", response_model=LegalTextResponse, status_code=status.HTTP_201_CREATED)
async def create_legal_text(
    legal_text: LegalTextCreate,
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """
    创建法律文本（管理员）
    """
    created_text = await legal_crud.create_legal_text(
        text_type=legal_text.type,
        content=legal_text.content,
        version=legal_text.version,
        subtype=legal_text.subtype,
        language=legal_text.language,
        is_active=legal_text.is_active,
        content_path=legal_text.content_path
    )
    
    return created_text

@router.put("/admin/content/{text_id}", response_model=LegalTextResponse)
async def update_legal_text(
    text_id: int = Path(..., description="法律文本ID"),
    legal_text: LegalTextUpdate = None,
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """
    更新法律文本（管理员）
    """
    # 检查文本是否存在
    existing_text = await legal_crud.get_legal_text_by_id(text_id)
    if not existing_text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到ID为{text_id}的法律文本"
        )
    
    # 更新文本
    updated_text = await legal_crud.update_legal_text(
        id=text_id,
        content=legal_text.content if legal_text else None,
        is_active=legal_text.is_active if legal_text else None,
        content_path=legal_text.content_path if legal_text else None
    )
    
    return updated_text

@router.delete("/admin/content/{text_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_legal_text(
    text_id: int = Path(..., description="法律文本ID"),
    current_user: UserResponse = Depends(get_current_admin_user)
):
    """
    删除法律文本（管理员）
    """
    # 检查文本是否存在
    existing_text = await legal_crud.get_legal_text_by_id(text_id)
    if not existing_text:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"未找到ID为{text_id}的法律文本"
        )
    
    # 删除文本
    success = await legal_crud.delete_legal_text(text_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除法律文本失败"
        )