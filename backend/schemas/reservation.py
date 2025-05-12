"""
预定数据验证模式
Reservation data validation schemas
"""
from typing import Optional, List, Generic, TypeVar, Any
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

# 基础预定模式
class ReservationBase(BaseModel):
    equipment_id: int = Field(..., title="设备ID", gt=0)
    user_name: str = Field(..., title="用户姓名", max_length=100)
    user_department: str = Field(..., title="用户部门", max_length=100)
    user_contact: str = Field(..., title="联系方式", max_length=100)
    start_datetime: datetime = Field(..., title="开始时间")
    end_datetime: datetime = Field(..., title="结束时间")
    purpose: Optional[str] = Field(None, title="使用目的")

# 创建预定请求
class ReservationCreate(ReservationBase):
    user_email: Optional[str] = Field(None, title="用户邮箱", max_length=100)
    lang: Optional[str] = Field("zh_CN", title="语言")

# 更新预定请求
class ReservationUpdate(BaseModel):
    start_datetime: Optional[datetime] = Field(None, title="开始时间")
    end_datetime: Optional[datetime] = Field(None, title="结束时间")
    purpose: Optional[str] = Field(None, title="使用目的")
    user_email: Optional[str] = Field(None, title="用户邮箱", max_length=100)
    lang: Optional[str] = Field("zh_CN", title="语言")

# 预定响应
class Reservation(ReservationBase):
    id: int
    reservation_number: str
    reservation_code: str
    status: str
    created_at: datetime
    equipment_name: Optional[str] = None
    equipment_category: Optional[str] = None
    equipment_location: Optional[str] = None
    user_email: Optional[str] = None
    qrcode_url: Optional[str] = None

    class Config:
        from_attributes = True

# 预定列表响应
class ReservationList(BaseModel):
    items: List[Reservation]
    total: int

# 通用响应
class ReservationResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

# 预定查询请求
class ReservationQuery(BaseModel):
    reservation_code: str = Field(..., title="预定码")
    user_contact: Optional[str] = Field(None, title="联系方式", max_length=100)

# 预定取消请求
class ReservationCancel(BaseModel):
    reservation_code: Optional[str] = Field(None, title="预定码")
    user_contact: Optional[str] = Field(None, title="联系方式", max_length=100)
    reason: Optional[str] = Field(None, title="取消原因")
    lang: Optional[str] = Field("zh_CN", title="语言")
    reservation_number: Optional[str] = Field(None, title="预约序号")
    user_email: Optional[str] = Field(None, title="用户邮箱", max_length=100)
    early_return: Optional[bool] = Field(False, title="是否提前归还")
