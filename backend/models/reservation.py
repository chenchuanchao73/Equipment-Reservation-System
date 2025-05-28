"""
预定模型
Reservation model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from backend.utils.db_utils import BeijingNow

from backend.database import Base

class Reservation(Base):
    """
    预定模型类
    Reservation model class
    """
    __tablename__ = "reservation"

    id = Column(Integer, primary_key=True, index=True)
    reservation_number = Column(String(20), unique=True, nullable=False, index=True, comment="预约序号，唯一标识每个预约")
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False, comment="设备ID")
    reservation_code = Column(String(20), nullable=False, index=True, comment="预定码，用于关联相同循环预约的子预约")
    user_name = Column(String(100), nullable=False, comment="用户姓名")
    user_department = Column(String(100), nullable=False, comment="用户部门")
    user_contact = Column(String(100), nullable=False, comment="联系方式")
    user_email = Column(String(100), comment="用户邮箱")
    start_datetime = Column(DateTime, nullable=False, comment="开始时间")
    end_datetime = Column(DateTime, nullable=False, comment="结束时间")
    purpose = Column(Text, comment="使用目的")
    status = Column(String(20), default="confirmed", comment="状态: confirmed(已确认), in_use(使用中), expired(已过期), cancelled(已取消)")
    created_at = Column(DateTime, default=BeijingNow(), comment="创建时间")

    # 循环预约相关字段
    recurring_reservation_id = Column(Integer, ForeignKey("recurring_reservation.id"), nullable=True, comment="循环预约ID")
    is_exception = Column(Integer, default=0, comment="是否为循环预约的例外，0表示否，1表示是")

    # 时间段关联
    time_slot_id = Column(Integer, ForeignKey("equipment_time_slots.id"), nullable=True, comment="关联的设备时间段ID")

    # 关系
    equipment = relationship("Equipment", back_populates="reservations")
    recurring_reservation = relationship("RecurringReservation", back_populates="reservations")
    time_slot = relationship("EquipmentTimeSlot", back_populates="reservations")
    # 使用字符串引用，避免循环引用问题
    history = relationship("ReservationHistory", back_populates="reservation", cascade="all, delete-orphan", lazy="dynamic")

    def __repr__(self):
        return f"<Reservation {self.reservation_number}>"
