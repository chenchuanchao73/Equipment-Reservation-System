"""
添加视频教程字段的数据库迁移脚本
Database migration script to add video_tutorial field to equipment table
"""
import os
import sys
import logging
from sqlalchemy import create_engine, text

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

# 导入配置
from config import DATABASE_URL

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migration():
    """
    运行迁移
    Run migration
    """
    try:
        # 创建数据库引擎
        engine = create_engine(DATABASE_URL)
        
        # 连接数据库
        with engine.connect() as conn:
            # 对于SQLite，我们使用PRAGMA table_info来检查字段是否存在
            result = conn.execute(text("PRAGMA table_info(equipment)"))
            columns = result.fetchall()
            
            # 检查video_tutorial字段是否存在
            video_tutorial_exists = any(column[1] == 'video_tutorial' for column in columns)
            
            # 如果字段不存在，添加字段
            if not video_tutorial_exists:
                conn.execute(text("""
                    ALTER TABLE equipment 
                    ADD COLUMN video_tutorial TEXT
                """))
                conn.commit()
                logger.info("成功添加video_tutorial字段到equipment表")
            else:
                logger.info("video_tutorial字段已存在，无需添加")
        
        return True
    except Exception as e:
        logger.error(f"迁移失败: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("开始迁移...")
    success = run_migration()
    if success:
        logger.info("迁移成功完成")
    else:
        logger.error("迁移失败")
        sys.exit(1)
