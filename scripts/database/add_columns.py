#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
直接向设备表添加同时预定功能相关字段
Directly add simultaneous reservation fields to equipment table
"""
import os
import sys
import logging
import sqlite3

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

def add_columns():
    """添加字段到设备表"""
    try:
        # 连接到数据库
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                              'equipment_reservation.db')
        logging.info(f"连接数据库: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查equipment表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='equipment'")
        if not cursor.fetchone():
            logging.error("设备表不存在！")
            return False
        
        # 获取equipment表的所有列信息
        cursor.execute("PRAGMA table_info(equipment)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        logging.info(f"设备表当前列: {column_names}")
        
        # 检查并添加allow_simultaneous字段
        if "allow_simultaneous" not in column_names:
            logging.info("添加 allow_simultaneous 字段...")
            cursor.execute("ALTER TABLE equipment ADD COLUMN allow_simultaneous BOOLEAN DEFAULT 0")
            logging.info("添加 allow_simultaneous 字段成功")
        else:
            logging.info("allow_simultaneous 字段已存在")
        
        # 检查并添加max_simultaneous字段
        if "max_simultaneous" not in column_names:
            logging.info("添加 max_simultaneous 字段...")
            cursor.execute("ALTER TABLE equipment ADD COLUMN max_simultaneous INTEGER DEFAULT 1")
            logging.info("添加 max_simultaneous 字段成功")
        else:
            logging.info("max_simultaneous 字段已存在")
        
        # 提交更改
        conn.commit()
        
        # 验证字段是否已添加
        cursor.execute("PRAGMA table_info(equipment)")
        columns_after = cursor.fetchall()
        column_names_after = [column[1] for column in columns_after]
        logging.info(f"设备表更新后的列: {column_names_after}")
        
        # 检查字段是否添加成功
        if "allow_simultaneous" in column_names_after and "max_simultaneous" in column_names_after:
            logging.info("✅ 字段添加成功")
        else:
            logging.error("❌ 字段添加失败")
            return False
        
        # 关闭连接
        conn.close()
        
        return True
    except Exception as e:
        logging.error(f"添加字段失败: {str(e)}")
        return False

if __name__ == "__main__":
    if add_columns():
        logging.info("操作完成：成功添加字段")
        sys.exit(0)
    else:
        logging.error("操作失败：未能添加字段")
        sys.exit(1) 