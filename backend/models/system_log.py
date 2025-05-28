"""
系统日志模型
System log model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime

from backend.database import Base
from backend.utils.date_utils import get_beijing_now

class SystemLog(Base):
    """
    系统操作日志模型类
    System operation log model class
    """
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_type = Column(String(20), nullable=False, comment="用户类型: admin, user")
    user_id = Column(String(50), comment="用户ID或用户名")
    user_name = Column(String(100), comment="用户姓名或联系方式")
    action = Column(String(50), nullable=False, comment="操作类型: login, logout, create, update, delete, etc.")
    module = Column(String(50), nullable=False, comment="操作模块: equipment, reservation, admin, etc.")
    description = Column(Text, comment="操作描述")
    ip_address = Column(String(50), comment="IP地址")
    status = Column(String(20), default="success", comment="状态: success, failed")
    error_message = Column(Text, comment="错误信息")
    target_id = Column(String(50), comment="操作对象ID")
    target_type = Column(String(50), comment="操作对象类型")
    created_at = Column(DateTime, default=get_beijing_now, comment="创建时间")
    details = Column(Text, comment="操作详细信息，JSON格式")

    def __repr__(self):
        return f"<SystemLog {self.id}: {self.user_type} {self.action} {self.module}>"
