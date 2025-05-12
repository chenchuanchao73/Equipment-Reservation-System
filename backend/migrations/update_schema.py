"""
更新数据库表结构
Update database schema
"""
import os
import sys
import asyncio
import logging

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

import sqlite3
from backend.database import init_db
from config import DATABASE_URL

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def update_schema():
    """
    更新数据库表结构
    Update database schema
    """
    # 初始化数据库
    await init_db()

    # 从 DATABASE_URL 中提取数据库路径
    # 默认格式为 sqlite:///path/to/database.db
    db_path = DATABASE_URL.replace('sqlite:///', '')
    logger.info(f"数据库路径: {db_path}")

    try:
        # 连接到SQLite数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 检查equipment表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='equipment'")
        if cursor.fetchone():
            # 检查category_id列是否存在
            cursor.execute("PRAGMA table_info(equipment)")
            columns = cursor.fetchall()
            column_names = [column[1] for column in columns]

            if 'category_id' not in column_names:
                # 添加category_id列
                logger.info("添加category_id列到equipment表")
                cursor.execute("ALTER TABLE equipment ADD COLUMN category_id INTEGER REFERENCES equipment_category(id)")
                conn.commit()
                logger.info("category_id列添加成功")
            else:
                logger.info("category_id列已存在")
        else:
            logger.error("equipment表不存在")

        # 关闭连接
        conn.close()
    except Exception as e:
        logger.error(f"更新数据库表结构出错: {str(e)}")

if __name__ == "__main__":
    asyncio.run(update_schema())
