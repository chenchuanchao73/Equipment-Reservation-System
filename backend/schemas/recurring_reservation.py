"""
循环预约数据验证模式
Recurring Reservation data validation schemas
"""
from typing import Optional, List, Any
from datetime import date, time, datetime
from pydantic import BaseModel, Field, validator
import json

# 基础循环预约模式
class RecurringReservationBase(BaseModel):
    equipment_id: int = Field(..., title="设备ID", gt=0)
    pattern_type: str = Field(..., title="重复模式", description="daily, weekly, monthly, custom")
    start_date: date = Field(..., title="开始日期")
    end_date: date = Field(..., title="结束日期")
    start_time: time = Field(..., title="开始时间")
    end_time: time = Field(..., title="结束时间")
    user_name: str = Field(..., title="用户姓名", max_length=100)
    user_department: str = Field(..., title="用户部门", max_length=100)
    user_contact: str = Field(..., title="联系方式", max_length=100)
    purpose: Optional[str] = Field(None, title="使用目的")

    @validator('pattern_type')
    def validate_pattern_type(cls, v):
        allowed_types = ['daily', 'weekly', 'monthly', 'custom']
        if v not in allowed_types:
            raise ValueError(f'模式类型必须是以下之一: {", ".join(allowed_types)}')
        return v

    @validator('end_date')
    def validate_end_date(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('结束日期必须晚于或等于开始日期')
        return v

    @validator('end_time')
    def validate_end_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('结束时间必须晚于开始时间')
        return v

# 创建循环预约请求
class RecurringReservationCreate(RecurringReservationBase):
    days_of_week: Optional[List[int]] = Field(None, title="每周几", description="0-6, 0表示周日")
    days_of_month: Optional[List[int]] = Field(None, title="每月几号", description="1-31")
    user_email: str = Field(..., title="用户邮箱", max_length=100)
    lang: Optional[str] = Field("zh_CN", title="语言")

    @validator('days_of_week')
    def validate_days_of_week(cls, v, values):
        if values.get('pattern_type') == 'weekly' and (not v or len(v) == 0):
            raise ValueError('每周模式必须指定每周几')
        if v:
            for day in v:
                if day < 0 or day > 6:
                    raise ValueError('每周几必须在0-6之间，0表示周日')
        return v

    @validator('days_of_month')
    def validate_days_of_month(cls, v, values):
        if values.get('pattern_type') == 'monthly' and (not v or len(v) == 0):
            raise ValueError('每月模式必须指定每月几号')
        if v:
            for day in v:
                if day < 1 or day > 31:
                    raise ValueError('每月几号必须在1-31之间')
        return v

# 更新循环预约请求
class RecurringReservationUpdate(BaseModel):
    pattern_type: Optional[str] = Field(None, title="重复模式", description="daily, weekly, monthly, custom")
    days_of_week: Optional[List[int]] = Field(None, title="每周几", description="0-6, 0表示周日")
    days_of_month: Optional[List[int]] = Field(None, title="每月几号", description="1-31")
    start_date: Optional[date] = Field(None, title="开始日期")
    end_date: Optional[date] = Field(None, title="结束日期")
    start_time: Optional[time] = Field(None, title="开始时间")
    end_time: Optional[time] = Field(None, title="结束时间")
    purpose: Optional[str] = Field(None, title="使用目的")
    user_email: Optional[str] = Field(None, title="用户邮箱", max_length=100)
    status: Optional[str] = Field(None, title="状态", description="active, cancelled")
    lang: Optional[str] = Field("zh_CN", title="语言")

    @validator('pattern_type')
    def validate_pattern_type(cls, v):
        if v:
            allowed_types = ['daily', 'weekly', 'monthly', 'custom']
            if v not in allowed_types:
                raise ValueError(f'模式类型必须是以下之一: {", ".join(allowed_types)}')
        return v

# 循环预约响应
class RecurringReservation(RecurringReservationBase):
    id: int
    reservation_code: Optional[str] = None
    days_of_week: Optional[List[int]] = None
    days_of_month: Optional[List[int]] = None
    user_email: Optional[str] = None
    status: str
    created_at: datetime
    equipment_name: Optional[str] = None
    equipment_category: Optional[str] = None
    equipment_location: Optional[str] = None
    # 添加以下字段
    conflicts: Optional[str] = None
    total_planned: Optional[int] = None
    created_count: Optional[int] = None
    conflict_dates: Optional[List[str]] = None

    class Config:
        from_attributes = True

    @validator('days_of_week', 'days_of_month', pre=True)
    def parse_json_list(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                return []
        return v

# 循环预约列表响应
class RecurringReservationList(BaseModel):
    items: List[RecurringReservation]
    total: int

# 通用响应
class RecurringReservationResponse(BaseModel):
    success: bool
    message: str
    data: Optional[RecurringReservation] = None
