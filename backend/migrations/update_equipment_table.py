"""
更新设备表，确保添加同时预定功能相关字段
Update equipment table to ensure simultaneous reservation fields exist
"""
import logging
import sqlite3
from sqlalchemy import inspect, MetaData, Table, Column, Boolean, Integer

def check_column_exists(conn, table_name, column_name):
    """检查列是否存在"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    column_exists = any(column[1] == column_name for column in columns)
    cursor.close()
    return column_exists

def migrate(db_engine):
    """
    执行迁移
    Execute migration
    """
    try:
        # 获取数据库连接
        conn = db_engine.raw_connection()
        
        # 检查allow_simultaneous字段是否存在
        allow_simultaneous_exists = check_column_exists(conn, "equipment", "allow_simultaneous")
        if not allow_simultaneous_exists:
            logging.info("添加 allow_simultaneous 字段...")
            conn.execute("ALTER TABLE equipment ADD COLUMN allow_simultaneous BOOLEAN DEFAULT 0")
            logging.info("添加 allow_simultaneous 字段成功")
        else:
            logging.info("allow_simultaneous 字段已存在")
        
        # 检查max_simultaneous字段是否存在
        max_simultaneous_exists = check_column_exists(conn, "equipment", "max_simultaneous")
        if not max_simultaneous_exists:
            logging.info("添加 max_simultaneous 字段...")
            conn.execute("ALTER TABLE equipment ADD COLUMN max_simultaneous INTEGER DEFAULT 1")
            logging.info("添加 max_simultaneous 字段成功")
        else:
            logging.info("max_simultaneous 字段已存在")
        
        # 提交事务
        conn.commit()
        conn.close()
        
        return True
    except Exception as e:
        logging.error(f"迁移失败: {str(e)}")
        return False 