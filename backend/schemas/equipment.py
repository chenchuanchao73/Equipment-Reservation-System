"""
设备数据验证模式
Equipment data validation schemas
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

# 基础设备模式
class EquipmentBase(BaseModel):
    name: str = Field(..., title="设备名称", max_length=100)
    category: str = Field(..., title="设备类别", max_length=50)
    model: Optional[str] = Field(None, title="设备型号", max_length=100)
    location: Optional[str] = Field(None, title="设备位置", max_length=100)
    status: Optional[str] = Field("available", title="设备状态", max_length=20)
    description: Optional[str] = Field(None, title="设备描述")
    image_path: Optional[str] = Field(None, title="设备图片路径", max_length=255)
    user_guide: Optional[str] = Field(None, title="设备使用指南")
    video_tutorial: Optional[str] = Field(None, title="视频教程链接", max_length=255)
    allow_simultaneous: Optional[bool] = Field(False, title="是否允许同时预定")
    max_simultaneous: Optional[int] = Field(1, title="最大同时预定数量")

# 创建设备请求
class EquipmentCreate(EquipmentBase):
    pass

# 更新设备请求
class EquipmentUpdate(BaseModel):
    name: Optional[str] = Field(None, title="设备名称", max_length=100)
    category: Optional[str] = Field(None, title="设备类别", max_length=50)
    model: Optional[str] = Field(None, title="设备型号", max_length=100)
    location: Optional[str] = Field(None, title="设备位置", max_length=100)
    status: Optional[str] = Field(None, title="设备状态", max_length=20)
    description: Optional[str] = Field(None, title="设备描述")
    image_path: Optional[str] = Field(None, title="设备图片路径", max_length=255)
    user_guide: Optional[str] = Field(None, title="设备使用指南")
    video_tutorial: Optional[str] = Field(None, title="视频教程链接", max_length=255)
    allow_simultaneous: Optional[bool] = Field(None, title="是否允许同时预定")
    max_simultaneous: Optional[int] = Field(None, title="最大同时预定数量")

# 设备响应
class Equipment(EquipmentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    currently_reserved: Optional[bool] = False

    class Config:
        from_attributes = True

# 设备列表响应
class EquipmentList(BaseModel):
    items: List[Equipment]
    total: int

# 设备可用性请求
class EquipmentAvailabilityRequest(BaseModel):
    start_date: datetime
    end_date: datetime

# 设备可用性响应
class EquipmentAvailability(BaseModel):
    equipment_id: int
    dates: List[datetime]
    available: List[bool]
    allow_simultaneous: Optional[bool] = False
    max_simultaneous: Optional[int] = 1
    reservation_counts: Optional[List[int]] = None
