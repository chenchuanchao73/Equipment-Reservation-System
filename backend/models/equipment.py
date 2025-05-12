"""
设备模型
Equipment model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from backend.utils.db_utils import BeijingNow
from sqlalchemy.orm import relationship

from backend.database import Base

class Equipment(Base):
    """
    设备模型类
    Equipment model class
    """
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="设备名称")
    category = Column(String(50), nullable=False, comment="设备类别")
    model = Column(String(100), comment="设备型号")
    location = Column(String(100), comment="设备位置")
    status = Column(String(20), default="available", comment="设备状态: available, maintenance")
    description = Column(Text, comment="设备描述")
    image_path = Column(String(255), comment="设备图片路径")
    user_guide = Column(Text, comment="设备使用指南")
    video_tutorial = Column(String(255), comment="视频教程链接")
    created_at = Column(DateTime, default=BeijingNow(), comment="创建时间")
    updated_at = Column(DateTime, default=BeijingNow(), onupdate=BeijingNow(), comment="更新时间")

    # 类别关联
    category_id = Column(Integer, ForeignKey("equipment_category.id"), nullable=True)
    category_rel = relationship("EquipmentCategory", back_populates="equipments")

    # 预约关系
    reservations = relationship("Reservation", back_populates="equipment", cascade="all, delete-orphan")
    recurring_reservations = relationship("RecurringReservation", back_populates="equipment", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Equipment {self.name}>"
