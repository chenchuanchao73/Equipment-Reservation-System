"""
循环预约模型
Recurring Reservation model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func, Date, Time, JSON, Boolean
from backend.utils.db_utils import BeijingNow
from sqlalchemy.orm import relationship

from backend.database import Base

class RecurringReservation(Base):
    """
    循环预约模型类
    Recurring Reservation model class
    """
    __tablename__ = "recurring_reservation"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False, comment="设备ID")
    reservation_code = Column(String(20), unique=True, nullable=True, index=True, comment="循环预约码")
    pattern_type = Column(String(20), nullable=False, comment="重复模式: daily, weekly, monthly, custom")
    days_of_week = Column(JSON, comment="每周几 (0-6, 0表示周日)")
    days_of_month = Column(JSON, comment="每月几号")
    start_date = Column(Date, nullable=False, comment="系列预约开始日期")
    end_date = Column(Date, nullable=False, comment="系列预约结束日期")
    start_time = Column(Time, nullable=False, comment="每次预约的开始时间")
    end_time = Column(Time, nullable=False, comment="每次预约的结束时间")
    user_name = Column(String(100), nullable=False, comment="用户姓名")
    user_department = Column(String(100), nullable=False, comment="用户部门")
    user_contact = Column(String(100), nullable=False, comment="联系方式")
    user_email = Column(String(100), comment="用户邮箱")
    purpose = Column(Text, comment="使用目的")
    status = Column(String(20), default="active", comment="状态: active, cancelled")
    created_at = Column(DateTime, default=BeijingNow(), comment="创建时间")

    # 关系
    equipment = relationship("Equipment", back_populates="recurring_reservations")
    reservations = relationship("Reservation", back_populates="recurring_reservation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<RecurringReservation {self.id}>"
