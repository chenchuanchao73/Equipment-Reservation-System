#!/usr/bin/env python
"""
为循环预约表添加冲突信息相关字段的迁移脚本
Migration script to add conflict information fields to the recurring_reservation table
"""
import sys
import os
import sqlite3

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "equipment_reservation.db")

def run_migration():
    """执行迁移：为循环预约表添加冲突信息相关字段"""
    try:
        # 连接数据库
        print(f"连接数据库: {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 获取表的当前列
        cursor.execute("PRAGMA table_info(recurring_reservation)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"当前表列: {columns}")
        
        # 需要添加的列
        new_columns = {
            "conflicts": "TEXT",
            "total_planned": "INTEGER",
            "created_count": "INTEGER"
        }
        
        # 添加缺少的列
        for column_name, column_type in new_columns.items():
            if column_name not in columns:
                print(f"添加'{column_name}'字段...")
                try:
                    cursor.execute(f"ALTER TABLE recurring_reservation ADD COLUMN {column_name} {column_type}")
                    print(f"'{column_name}'字段添加成功")
                except Exception as e:
                    print(f"添加'{column_name}'字段时出错: {str(e)}")
                    raise
            else:
                print(f"'{column_name}'字段已存在")
        
        # 提交更改并关闭连接
        conn.commit()
        conn.close()
        
        print("迁移完成！")
        return True
    except Exception as e:
        print(f"迁移失败: {str(e)}")
        return False

if __name__ == "__main__":
    success = run_migration()
    
    if success:
        print("迁移成功完成")
    else:
        print("迁移失败")
        sys.exit(1) 