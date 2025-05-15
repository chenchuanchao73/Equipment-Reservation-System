"""
管理员CRUD操作
Admin CRUD operations
"""
import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from backend.models.admin import Admin
from backend.schemas.admin import AdminCreate, AdminUpdate
from backend.routes.auth import get_password_hash

# 设置日志
logger = logging.getLogger(__name__)

def get_admin(db: Session, admin_id: int):
    """
    获取管理员
    Get admin
    """
    return db.query(Admin).filter(Admin.id == admin_id).first()

def get_admin_by_username(db: Session, username: str):
    """
    通过用户名获取管理员
    Get admin by username
    """
    return db.query(Admin).filter(Admin.username == username).first()

def get_admins(
    db: Session, 
    skip: int = 0, 
    limit: int = 10,
    search: Optional[str] = None
):
    """
    获取管理员列表
    Get admin list
    """
    query = db.query(Admin)
    
    # 应用过滤条件
    if search:
        query = query.filter(
            or_(
                Admin.username.ilike(f"%{search}%"),
                Admin.name.ilike(f"%{search}%")
            )
        )
    
    # 应用分页
    return query.order_by(Admin.id).offset(skip).limit(limit).all()

def get_admin_count(
    db: Session,
    search: Optional[str] = None
):
    """
    获取管理员数量
    Get admin count
    """
    query = db.query(func.count(Admin.id))
    
    # 应用过滤条件
    if search:
        query = query.filter(
            or_(
                Admin.username.ilike(f"%{search}%"),
                Admin.name.ilike(f"%{search}%")
            )
        )
    
    return query.scalar()

def create_admin(db: Session, admin: AdminCreate):
    """
    创建管理员
    Create admin
    """
    # 检查用户名是否已存在
    db_admin = db.query(Admin).filter(Admin.username == admin.username).first()
    if db_admin:
        raise ValueError(f"用户名 '{admin.username}' 已存在")
    
    # 创建管理员
    hashed_password = get_password_hash(admin.password)
    db_admin = Admin(
        username=admin.username,
        password_hash=hashed_password,
        name=admin.name,
        role=admin.role,
        is_active=admin.is_active
    )
    
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    
    return db_admin

def update_admin(db: Session, admin_id: int, admin: AdminUpdate):
    """
    更新管理员
    Update admin
    """
    db_admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not db_admin:
        return None
    
    # 更新字段
    update_data = admin.dict(exclude_unset=True)
    
    # 如果更新密码，需要哈希处理
    if "password" in update_data:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))
    
    for key, value in update_data.items():
        setattr(db_admin, key, value)
    
    db.commit()
    db.refresh(db_admin)
    
    return db_admin

def delete_admin(db: Session, admin_id: int):
    """
    删除管理员
    Delete admin
    """
    db_admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not db_admin:
        return False
    
    db.delete(db_admin)
    db.commit()
    
    return True
