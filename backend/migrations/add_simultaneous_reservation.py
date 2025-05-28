"""
添加可同时预定功能相关字段
Add simultaneous reservation fields to equipment table
"""
import logging
from sqlalchemy import Column, Boolean, Integer

def migrate(db_engine):
    """
    执行迁移
    Execute migration
    """
    try:
        # 添加allow_simultaneous字段
        db_engine.execute(
            "ALTER TABLE equipment ADD COLUMN allow_simultaneous BOOLEAN DEFAULT 0"
        )
        logging.info("添加 allow_simultaneous 字段成功")

        # 添加max_simultaneous字段
        db_engine.execute(
            "ALTER TABLE equipment ADD COLUMN max_simultaneous INTEGER DEFAULT 1"
        )
        logging.info("添加 max_simultaneous 字段成功")

        return True
    except Exception as e:
        logging.error(f"迁移失败: {str(e)}")
        return False 