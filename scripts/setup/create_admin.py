"""
创建默认管理员账户
Create default admin account
"""
import os
import sys
import logging
from sqlalchemy.orm import Session

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

# 导入所需模块
from backend.database import SessionLocal, Base, engine
from backend.models.admin import Admin
from backend.routes.auth import get_password_hash
from config import ADMIN_PASSWORD

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_default_admin():
    """创建默认管理员账户"""
    # 初始化数据库
    # 导入所有模型以确保它们被注册到Base中
    from backend.models.equipment import Equipment
    from backend.models.reservation import Reservation
    from backend.models.admin import Admin

    # 创建所有表
    Base.metadata.create_all(bind=engine)
    logger.info("数据库初始化成功")

    # 创建数据库会话
    db = SessionLocal()
    try:
        # 检查是否已存在管理员账户
        admin = db.query(Admin).filter(Admin.username == "admin").first()
        if admin:
            logger.info("默认管理员账户已存在")
            return

        # 创建默认管理员账户
        hashed_password = get_password_hash(ADMIN_PASSWORD)
        admin = Admin(
            username="admin",
            password_hash=hashed_password,
            name="管理员",
            role="superadmin",
            is_active=True
        )

        db.add(admin)
        db.commit()
        logger.info("默认管理员账户创建成功")
    except Exception as e:
        logger.error(f"创建默认管理员账户失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_default_admin()
    print("用户名: admin")
    print(f"密码: {ADMIN_PASSWORD}")
