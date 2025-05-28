"""
预定历史记录模型
Reservation history model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from backend.database import Base
from backend.utils.date_utils import get_beijing_now

class ReservationHistory(Base):
    """
    预定历史记录模型类
    Reservation history model class
    """
    __tablename__ = "reservation_history"

    id = Column(Integer, primary_key=True, index=True)
    reservation_id = Column(Integer, ForeignKey("reservation.id"), nullable=False, comment="预定ID")
    reservation_code = Column(String(20), nullable=False, index=True, comment="预定码")
    reservation_number = Column(String(20), nullable=True, index=True, comment="预定序号")
    user_type = Column(String(20), nullable=False, comment="用户类型: admin, user")
    user_id = Column(String(50), comment="用户ID或用户名")
    action = Column(String(50), nullable=False, comment="操作类型: update, status_change")
    field_name = Column(String(50), comment="修改的字段名")
    old_value = Column(Text, comment="修改前的值")
    new_value = Column(Text, comment="修改后的值")
    created_at = Column(DateTime, default=get_beijing_now(), comment="创建时间")

    # 关系
    # 使用字符串引用，避免循环引用问题
    reservation = relationship("Reservation", back_populates="history")

    def __repr__(self):
        return f"<ReservationHistory {self.id}: {self.action} {self.field_name}>"
