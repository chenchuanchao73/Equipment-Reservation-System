"""
管理员API模式
Admin API schemas
"""
from typing import List, Optional
from pydantic import BaseModel, Field, validator, EmailStr
from datetime import datetime

# 标准响应基础模式
class ResponseBase(BaseModel):
    success: bool = Field(True, title="是否成功")
    message: str = Field("操作成功", title="响应消息")

# 管理员基础模式
class AdminBase(BaseModel):
    username: str = Field(..., title="用户名")
    name: Optional[str] = Field(None, title="管理员姓名")

# 管理员创建请求
class AdminCreate(AdminBase):
    password: str = Field(..., title="密码")
    role: str = Field("admin", title="角色")
    is_active: bool = Field(True, title="是否激活")

# 管理员更新请求
class AdminUpdate(BaseModel):
    name: Optional[str] = Field(None, title="管理员姓名")
    password: Optional[str] = Field(None, title="密码")
    role: Optional[str] = Field(None, title="角色")
    is_active: Optional[bool] = Field(None, title="是否激活")

# 管理员响应模式
class Admin(AdminBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True

# 管理员列表响应
class AdminList(BaseModel):
    items: List[Admin]
    total: int

# Token相关模式
class Token(BaseModel):
    access_token: str
    token_type: str
    admin_id: int
    username: str
    name: Optional[str] = None
    role: str

class TokenData(BaseModel):
    username: str

# 修改密码请求
class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., title="当前密码")
    new_password: str = Field(..., title="新密码")

    @validator('new_password')
    def validate_new_password(cls, v):
        if len(v) < 6:
            raise ValueError('密码长度不能小于6个字符')
        return v
