"""
管理员数据验证模式
Admin data validation schemas
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

# 基础管理员模式
class AdminBase(BaseModel):
    username: str = Field(..., title="用户名", max_length=50)
    name: Optional[str] = Field(None, title="姓名", max_length=100)
    role: Optional[str] = Field("admin", title="角色", max_length=20)
    is_active: Optional[bool] = Field(True, title="是否激活")

# 创建管理员请求
class AdminCreate(AdminBase):
    password: str = Field(..., title="密码", min_length=6)

# 更新管理员请求
class AdminUpdate(BaseModel):
    name: Optional[str] = Field(None, title="姓名", max_length=100)
    role: Optional[str] = Field(None, title="角色", max_length=20)
    is_active: Optional[bool] = Field(None, title="是否激活")
    password: Optional[str] = Field(None, title="密码", min_length=6)

# 管理员响应
class Admin(AdminBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# 管理员列表响应
class AdminList(BaseModel):
    items: List[Admin]
    total: int

# 令牌数据
class Token(BaseModel):
    access_token: str
    token_type: str
    admin_id: int
    username: str
    name: Optional[str] = None
    role: str

# 令牌数据载荷
class TokenData(BaseModel):
    username: Optional[str] = None

# 系统设置基础模式
class SystemSettingsBase(BaseModel):
    site_name: str = Field(..., title="站点名称", max_length=100)
    maintenance_mode: bool = Field(False, title="维护模式")
    reservation_limit_per_day: int = Field(5, title="每日预定限制", ge=1)
    allow_equipment_conflict: bool = Field(False, title="允许设备冲突")
    advance_reservation_days: int = Field(30, title="提前预定天数", ge=1)

# 系统设置更新请求
class SystemSettingsUpdate(BaseModel):
    site_name: Optional[str] = Field(None, title="站点名称", max_length=100)
    maintenance_mode: Optional[bool] = Field(None, title="维护模式")
    reservation_limit_per_day: Optional[int] = Field(None, title="每日预定限制", ge=1)
    allow_equipment_conflict: Optional[bool] = Field(None, title="允许设备冲突")
    advance_reservation_days: Optional[int] = Field(None, title="提前预定天数", ge=1)

# 系统设置响应
class SystemSettings(SystemSettingsBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
