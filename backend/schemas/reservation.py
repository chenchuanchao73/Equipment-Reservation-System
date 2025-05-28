"""
预定数据验证模式
Reservation data validation schemas
"""
from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field

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
    skip_email: Optional[bool] = Field(False, title="跳过发送邮件")

# 更新预定请求
class ReservationUpdate(BaseModel):
    start_datetime: Optional[datetime] = Field(None, title="开始时间")
    end_datetime: Optional[datetime] = Field(None, title="结束时间")
    purpose: Optional[str] = Field(None, title="使用目的")
    user_email: Optional[str] = Field(None, title="用户邮箱", max_length=100)
    status: Optional[str] = Field(None, title="预定状态", description="仅管理员可修改")
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

# 预定导出请求
class ReservationExportRequest(BaseModel):
    export_format: str = Field("excel", title="导出格式", description="excel 或 csv")
    export_scope: str = Field("current", title="导出范围", description="current(当前页面) 或 all(全部筛选结果)")
    selected_fields: Optional[List[str]] = Field(None, title="选择的字段")
    # 当前页面数据（用于当前页面导出时）
    current_data: Optional[List[dict]] = Field(None, title="当前页面数据")
    # 筛选条件（用于全部导出时）
    reservation_code: Optional[str] = Field(None, title="预约码")
    user_name: Optional[str] = Field(None, title="用户名")
    status: Optional[str] = Field(None, title="状态")
    from_date: Optional[datetime] = Field(None, title="开始日期")
    to_date: Optional[datetime] = Field(None, title="结束日期")
    equipment_id: Optional[int] = Field(None, title="设备ID")
    category: Optional[str] = Field(None, title="设备类别")

# 预定取消请求
class ReservationCancel(BaseModel):
    reservation_code: Optional[str] = Field(None, title="预定码")
    user_contact: Optional[str] = Field(None, title="联系方式", max_length=100)
    reason: Optional[str] = Field(None, title="取消原因")
    lang: Optional[str] = Field("zh_CN", title="语言")
    reservation_number: Optional[str] = Field(None, title="预约序号")
    user_email: Optional[str] = Field(None, title="用户邮箱", max_length=100)
    early_return: Optional[bool] = Field(False, title="是否提前归还")
