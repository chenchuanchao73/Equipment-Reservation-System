from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import DateTime as DateTimeType
from datetime import datetime, timedelta
from backend.database import Base
from backend.utils.db_utils import BeijingNow

class BeijingDateTime(DateTimeType):
    """自定义DateTime类型，在存储前自动转换为北京时间"""
    def process_bind_param(self, value, dialect):
        """在数据写入数据库前处理"""
        if value is not None and isinstance(value, datetime):
            # 如果时间没有时区信息，假设是本地时间，直接返回
            if value.tzinfo is None:
                return value
            # 如果时间有时区信息，确保转换成北京时间
            return value.astimezone() + timedelta(hours=8)
        return value

# 注册方言编译器，确保函数now()是使用UTC时间
@compiles(func.now, 'sqlite')
def sqlite_now(element, compiler, **kw):
    return "DATETIME('now', '+8 hours')"  # 直接使用SQLite的时间函数，返回北京时间

class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=BeijingNow(), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False) 