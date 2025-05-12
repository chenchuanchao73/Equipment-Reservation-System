"""
设备类别数据迁移脚本
Equipment Category Data Migration Script
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

async def migrate_categories():
    """
    将设备表中的类别数据迁移到设备类别表中
    Migrate category data from equipment table to equipment_category table
    """
    # 初始化数据库
    await init_db()

    # 从 DATABASE_URL 中提取数据库路径
    db_path = DATABASE_URL.replace('sqlite:///', '')
    logger.info(f"数据库路径: {db_path}")

    try:
        # 连接到SQLite数据库
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # 使结果以字典形式返回
        cursor = conn.cursor()

        # 获取所有不同的设备类别
        cursor.execute("SELECT DISTINCT category FROM equipment WHERE category IS NOT NULL AND category != ''")
        categories = cursor.fetchall()
        logger.info(f"找到 {len(categories)} 个不同的设备类别")

        # 创建设备类别记录
        for category in categories:
            category_name = category['category']

            # 检查类别是否已存在
            cursor.execute("SELECT id FROM equipment_category WHERE name = ?", (category_name,))
            existing_category = cursor.fetchone()

            if existing_category:
                logger.info(f"类别 '{category_name}' 已存在，跳过")
                continue

            # 创建新类别
            cursor.execute("INSERT INTO equipment_category (name) VALUES (?)", (category_name,))
            logger.info(f"创建新类别: '{category_name}'")

        # 提交事务
        conn.commit()
        logger.info("类别数据迁移完成")

        # 更新设备记录，设置category_id
        cursor.execute("SELECT id, name FROM equipment_category")
        categories = cursor.fetchall()

        for category in categories:
            category_id = category['id']
            category_name = category['name']

            # 更新设备的类别ID
            cursor.execute("UPDATE equipment SET category_id = ? WHERE category = ?", (category_id, category_name))
            affected_rows = cursor.rowcount
            logger.info(f"更新了 {affected_rows} 个设备的类别ID为 '{category_name}' (ID: {category_id})")

        # 提交事务
        conn.commit()
        logger.info("设备类别关联更新完成")

        # 关闭连接
        conn.close()

    except Exception as e:
        logger.error(f"迁移过程中出错: {str(e)}")

if __name__ == "__main__":
    asyncio.run(migrate_categories())
