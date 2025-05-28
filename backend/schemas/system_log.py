"""
系统日志API模式
System log API schemas
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class SystemLogBase(BaseModel):
    """系统日志基础模型"""
    user_type: str = Field(..., title="用户类型")
    user_id: Optional[str] = Field(None, title="用户ID或用户名")
    user_name: Optional[str] = Field(None, title="用户姓名或联系方式")
    action: str = Field(..., title="操作类型")
    module: str = Field(..., title="操作模块")
    description: str = Field(..., title="操作描述")
    ip_address: Optional[str] = Field(None, title="IP地址")
    status: str = Field("success", title="状态")
    error_message: Optional[str] = Field(None, title="错误信息")
    target_id: Optional[str] = Field(None, title="操作对象ID")
    target_type: Optional[str] = Field(None, title="操作对象类型")
    details: Optional[str] = Field(None, title="操作详细信息，JSON格式")

class SystemLogCreate(SystemLogBase):
    """系统日志创建模型"""
    pass

class SystemLogOut(SystemLogBase):
    """系统日志输出模型"""
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class PaginatedSystemLogs(BaseModel):
    """分页系统日志列表"""
    items: List[SystemLogOut]
    total: int
