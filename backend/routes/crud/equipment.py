"""
设备CRUD操作
Equipment CRUD operations
"""
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from backend.models.equipment import Equipment
from backend.schemas.equipment import EquipmentCreate, EquipmentUpdate

# 设置日志
logger = logging.getLogger(__name__)

def create_equipment(db: Session, equipment: EquipmentCreate):
    """
    创建设备
    Create equipment
    """
    db_equipment = Equipment(
        name=equipment.name,
        category=equipment.category,
        model=equipment.model,
        location=equipment.location,
        status=equipment.status,
        description=equipment.description,
        image_path=equipment.image_path
    )
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    return db_equipment

def get_equipment(db: Session, equipment_id: int):
    """
    获取设备
    Get equipment
    """
    return db.query(Equipment).filter(Equipment.id == equipment_id).first()

def get_equipments(
    db: Session, 
    skip: int = 0, 
    limit: int = 10,
    category: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None
):
    """
    获取设备列表
    Get equipment list
    """
    query = db.query(Equipment)
    
    # 应用过滤条件
    if category:
        query = query.filter(Equipment.category == category)
    if status:
        query = query.filter(Equipment.status == status)
    if search:
        query = query.filter(
            or_(
                Equipment.name.ilike(f"%{search}%"),
                Equipment.model.ilike(f"%{search}%"),
                Equipment.location.ilike(f"%{search}%"),
                Equipment.description.ilike(f"%{search}%")
            )
        )
    
    # 应用分页
    return query.order_by(Equipment.id).offset(skip).limit(limit).all()

def get_equipment_count(
    db: Session,
    category: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None
):
    """
    获取设备数量
    Get equipment count
    """
    query = db.query(func.count(Equipment.id))
    
    # 应用过滤条件
    if category:
        query = query.filter(Equipment.category == category)
    if status:
        query = query.filter(Equipment.status == status)
    if search:
        query = query.filter(
            or_(
                Equipment.name.ilike(f"%{search}%"),
                Equipment.model.ilike(f"%{search}%"),
                Equipment.location.ilike(f"%{search}%"),
                Equipment.description.ilike(f"%{search}%")
            )
        )
    
    return query.scalar()

def get_equipment_categories(db: Session):
    """
    获取设备类别列表
    Get equipment categories
    """
    return db.query(Equipment.category).distinct().all()

def update_equipment(db: Session, equipment_id: int, equipment: EquipmentUpdate):
    """
    更新设备
    Update equipment
    """
    db_equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not db_equipment:
        return None
    
    # 更新字段
    update_data = equipment.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_equipment, key, value)
    
    db.commit()
    db.refresh(db_equipment)
    return db_equipment

def delete_equipment(db: Session, equipment_id: int):
    """
    删除设备
    Delete equipment
    """
    db_equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not db_equipment:
        return False
    
    db.delete(db_equipment)
    db.commit()
    return True
