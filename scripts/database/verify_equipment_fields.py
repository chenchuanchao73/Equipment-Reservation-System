#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证设备表中是否包含同时预定功能的字段
Verify that equipment table contains simultaneous reservation fields
"""
import os
import sys
import logging
import sqlite3

# 添加项目根目录到路径，确保能导入项目模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import DATABASE_URL, BASE_DIR

def main():
    """主函数，验证字段"""
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    
    # 从DATABASE_URL提取SQLite数据库文件路径
    db_path = str(BASE_DIR / 'equipment_reservation.db')
    
    logging.info(f"检查数据库: {db_path}")
    
    try:
        # 连接到SQLite数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取equipment表的所有列信息
        cursor.execute("PRAGMA table_info(equipment)")
        columns = cursor.fetchall()
        
        # 检查列是否存在
        column_names = [column[1] for column in columns]
        logging.info(f"设备表列: {column_names}")
        
        # 检查allow_simultaneous字段
        if "allow_simultaneous" in column_names:
            logging.info("✅ allow_simultaneous 字段存在")
        else:
            logging.error("❌ allow_simultaneous 字段不存在")
        
        # 检查max_simultaneous字段
        if "max_simultaneous" in column_names:
            logging.info("✅ max_simultaneous 字段存在")
        else:
            logging.error("❌ max_simultaneous 字段不存在")
        
        # 关闭连接
        conn.close()
        
    except Exception as e:
        logging.error(f"验证失败: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    main() 