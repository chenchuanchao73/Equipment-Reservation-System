"""
设备类别Schema
Equipment Category Schema
"""
from typing import List, Optional
from pydantic import BaseModel

class EquipmentCategoryBase(BaseModel):
    """
    设备类别基础Schema
    Equipment Category Base Schema
    """
    name: str
    description: Optional[str] = None

class EquipmentCategoryCreate(EquipmentCategoryBase):
    """
    创建设备类别Schema
    Create Equipment Category Schema
    """
    pass

class EquipmentCategoryUpdate(BaseModel):
    """
    更新设备类别Schema
    Update Equipment Category Schema
    """
    name: Optional[str] = None
    description: Optional[str] = None

class EquipmentCategory(EquipmentCategoryBase):
    """
    设备类别Schema
    Equipment Category Schema
    """
    id: int

    class Config:
        orm_mode = True

class EquipmentCategoryList(BaseModel):
    """
    设备类别列表Schema
    Equipment Category List Schema
    """
    items: List[EquipmentCategory]
    total: int

    class Config:
        orm_mode = True
