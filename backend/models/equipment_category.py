"""
设备类别模型
Equipment Category Model
"""
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.database import Base

class EquipmentCategory(Base):
    """
    设备类别模型
    Equipment Category Model
    """
    __tablename__ = "equipment_category"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # 关联设备
    equipments = relationship("Equipment", back_populates="category_rel")
