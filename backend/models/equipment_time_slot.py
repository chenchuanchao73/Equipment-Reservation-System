from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from backend.database import Base

class EquipmentTimeSlot(Base):
    """设备时间段模型，用于跟踪设备在特定时间段内的同时预约情况"""
    __tablename__ = "equipment_time_slots"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    current_count = Column(Integer, default=1)  # 当前已使用的同时预约数量
    
    # 关联关系
    equipment = relationship("Equipment", back_populates="time_slots")
    reservations = relationship("Reservation", back_populates="time_slot")

    def __repr__(self):
        return f"<EquipmentTimeSlot(id={self.id}, equipment_id={self.equipment_id}, current_count={self.current_count})>" 