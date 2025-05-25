from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

class LegalTextBase(BaseModel):
    """法律文本基础模型"""
    type: str = Field(..., description="文本类型，如disclaimer, risk_confirmation, privacy_policy, terms_of_service")
    subtype: Optional[str] = Field(None, description="子类型，如a-b, a-b-x")
    language: str = Field("zh-CN", description="语言代码")
    version: str = Field(..., description="版本号")

class LegalTextCreate(LegalTextBase):
    """创建法律文本请求模型"""
    content: str = Field(..., description="文本内容（HTML格式）")
    is_active: bool = Field(True, description="是否激活")
    content_path: Optional[str] = Field(None, description="文件系统中的文件路径（可选）")

class LegalTextUpdate(BaseModel):
    """更新法律文本请求模型"""
    content: Optional[str] = Field(None, description="文本内容（HTML格式）")
    is_active: Optional[bool] = Field(None, description="是否激活")
    content_path: Optional[str] = Field(None, description="文件系统中的文件路径（可选）")

class LegalTextResponse(LegalTextBase):
    """法律文本响应模型"""
    id: int
    content: Optional[str] = None
    is_active: bool
    content_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class LegalTextQuery(BaseModel):
    """法律文本查询参数模型"""
    type: str = Field(..., description="文本类型")
    subtype: Optional[str] = Field(None, description="子类型（可选）")
    version: Optional[str] = Field(None, description="版本号（可选，默认为最新版本）")
    language: str = Field("zh-CN", description="语言代码")