"""
预定历史记录数据验证模式
Reservation history data validation schemas
"""
from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel, Field

# 基础预定历史记录模式
class ReservationHistoryBase(BaseModel):
    reservation_id: int = Field(..., title="预定ID")
    reservation_code: str = Field(..., title="预定码")
    reservation_number: Optional[str] = Field(None, title="预定序号")
    user_type: str = Field(..., title="用户类型")
    user_id: Optional[str] = Field(None, title="用户ID或用户名")
    action: str = Field(..., title="操作类型")
    field_name: Optional[str] = Field(None, title="修改的字段名")
    old_value: Optional[str] = Field(None, title="修改前的值")
    new_value: Optional[str] = Field(None, title="修改后的值")

# 创建预定历史记录请求
class ReservationHistoryCreate(ReservationHistoryBase):
    pass

# 预定历史记录响应
class ReservationHistory(ReservationHistoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# 预定历史记录列表响应
class ReservationHistoryList(BaseModel):
    items: List[ReservationHistory]
    total: int
