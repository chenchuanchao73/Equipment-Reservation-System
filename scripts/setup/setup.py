"""
设备预定系统初始化脚本
Equipment Reservation System initialization script
"""
import os
import sys
import asyncio
import logging
from pathlib import Path
from getpass import getpass
from passlib.context import CryptContext

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

# 导入配置和模块
from config import BASE_DIR, ADMIN_PASSWORD
from backend.database import init_db, get_db
from backend.models.admin import Admin

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 密码哈希工具
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_admin_user(db, username, password, name="管理员"):
    """创建管理员用户"""
    # 检查用户是否已存在
    admin = db.query(Admin).filter(Admin.username == username).first()
    if admin:
        logger.info(f"管理员用户 {username} 已存在")
        return admin
    
    # 创建新管理员用户
    hashed_password = pwd_context.hash(password)
    admin = Admin(
        username=username,
        password_hash=hashed_password,
        name=name,
        role="admin",
        is_active=True
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    logger.info(f"已创建管理员用户 {username}")
    return admin

async def setup():
    """初始化设置"""
    logger.info("开始初始化设备预定系统...")
    
    # 确保目录存在
    os.makedirs(os.path.join(BASE_DIR, "logs"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "backend", "static"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "backend", "templates"), exist_ok=True)
    
    # 初始化数据库
    logger.info("初始化数据库...")
    await init_db()
    
    # 创建管理员用户
    logger.info("创建管理员用户...")
    async for db in get_db():
        # 使用默认管理员密码或从命令行输入
        password = ADMIN_PASSWORD
        if "--interactive" in sys.argv:
            password = getpass("请输入管理员密码: ")
        
        await create_admin_user(db, "admin", password)
        break
    
    logger.info("初始化完成！")

if __name__ == "__main__":
    asyncio.run(setup())
