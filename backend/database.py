"""
数据库连接管理
Database connection management
"""
import os
import sys
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# 导入配置
from config import DATABASE_URL

# 设置日志
logger = logging.getLogger(__name__)

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # 仅适用于SQLite
    pool_size=10,  # 增加连接池大小
    max_overflow=20,  # 增加最大溢出连接数
    pool_timeout=60,  # 增加连接超时时间
    pool_recycle=3600,  # 每小时回收连接
    pool_pre_ping=True  # 在使用连接前先测试连接是否有效
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()

async def init_db():
    """初始化数据库"""
    try:
        # 导入所有模型以确保它们被注册到Base中
        from backend.models.equipment import Equipment
        from backend.models.reservation import Reservation
        from backend.models.recurring_reservation import RecurringReservation
        from backend.models.admin import Admin
        from backend.models.email import EmailSettings, EmailTemplate, EmailLog
        from backend.models.announcement import Announcement
        from backend.models.equipment_time_slot import EquipmentTimeSlot
        from backend.models.equipment_category import EquipmentCategory
        from backend.models.system_log import SystemLog

        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("数据库初始化成功")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
