"""
设备类别CRUD操作
Equipment Category CRUD operations
"""
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from backend.models.equipment_category import EquipmentCategory
from backend.schemas.equipment_category import EquipmentCategoryCreate, EquipmentCategoryUpdate

# 设置日志
logger = logging.getLogger(__name__)

def create_category(db: Session, category: EquipmentCategoryCreate):
    """
    创建设备类别
    Create equipment category
    """
    db_category = EquipmentCategory(
        name=category.name,
        description=category.description
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

def get_category(db: Session, category_id: int):
    """
    获取设备类别
    Get equipment category
    """
    return db.query(EquipmentCategory).filter(EquipmentCategory.id == category_id).first()

def get_category_by_name(db: Session, name: str):
    """
    根据名称获取设备类别
    Get equipment category by name
    """
    return db.query(EquipmentCategory).filter(EquipmentCategory.name == name).first()

def get_categories(
    db: Session, 
    skip: int = 0, 
    limit: int = 10,
    search: Optional[str] = None
):
    """
    获取设备类别列表
    Get equipment category list
    """
    query = db.query(EquipmentCategory)
    
    # 应用过滤条件
    if search:
        query = query.filter(
            or_(
                EquipmentCategory.name.ilike(f"%{search}%"),
                EquipmentCategory.description.ilike(f"%{search}%")
            )
        )
    
    # 应用分页
    return query.order_by(EquipmentCategory.id).offset(skip).limit(limit).all()

def get_category_count(
    db: Session,
    search: Optional[str] = None
):
    """
    获取设备类别数量
    Get equipment category count
    """
    query = db.query(func.count(EquipmentCategory.id))
    
    # 应用过滤条件
    if search:
        query = query.filter(
            or_(
                EquipmentCategory.name.ilike(f"%{search}%"),
                EquipmentCategory.description.ilike(f"%{search}%")
            )
        )
    
    return query.scalar()

def get_all_categories(db: Session):
    """
    获取所有设备类别
    Get all equipment categories
    """
    return db.query(EquipmentCategory).order_by(EquipmentCategory.name).all()

def update_category(db: Session, category_id: int, category: EquipmentCategoryUpdate):
    """
    更新设备类别
    Update equipment category
    """
    db_category = db.query(EquipmentCategory).filter(EquipmentCategory.id == category_id).first()
    if not db_category:
        return None
    
    # 更新字段
    update_data = category.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_category, key, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category

def delete_category(db: Session, category_id: int):
    """
    删除设备类别
    Delete equipment category
    """
    db_category = db.query(EquipmentCategory).filter(EquipmentCategory.id == category_id).first()
    if not db_category:
        return False
    
    db.delete(db_category)
    db.commit()
    return True
