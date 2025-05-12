"""
管理员模型
Admin model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from backend.utils.db_utils import BeijingNow
from sqlalchemy.orm import relationship

from backend.database import Base

class Admin(Base):
    """
    管理员模型类
    Admin model class
    """
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, comment="用户名")
    password_hash = Column(String(100), nullable=False, comment="密码哈希")
    name = Column(String(100), comment="姓名")
    role = Column(String(20), default="admin", comment="角色: admin, superadmin")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, default=BeijingNow(), comment="创建时间")

    def __repr__(self):
        return f"<Admin {self.username}>"

class SystemSettings(Base):
    """
    系统设置模型类
    System settings model class
    """
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    site_name = Column(String(100), nullable=False, default="设备预定系统", comment="站点名称")
    maintenance_mode = Column(Boolean, default=False, comment="维护模式")
    reservation_limit_per_day = Column(Integer, default=5, comment="每日预定限制")
    allow_equipment_conflict = Column(Boolean, default=False, comment="允许设备冲突")
    advance_reservation_days = Column(Integer, default=30, comment="提前预定天数")
    created_at = Column(DateTime, default=BeijingNow(), comment="创建时间")
    updated_at = Column(DateTime, default=BeijingNow(), onupdate=BeijingNow(), comment="更新时间")

    def __repr__(self):
        return f"<SystemSettings {self.site_name}>"
