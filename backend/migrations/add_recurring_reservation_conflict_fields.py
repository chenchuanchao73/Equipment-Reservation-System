#!/usr/bin/env python
"""
为循环预约表添加冲突信息相关字段的迁移脚本
Migration script to add conflict information fields to the recurring_reservation table
"""
import sys
import os
from pathlib import Path
import sqlalchemy

# 获取项目根目录
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from backend.database import engine

def run_migration():
    """执行迁移：为循环预约表添加冲突信息相关字段"""
    try:
        # 检查字段是否已存在
        inspector = sqlalchemy.inspect(engine)
        columns = [c['name'] for c in inspector.get_columns('recurring_reservation')]
        
        with engine.begin() as conn:
            # 如果字段不存在，则添加
            if 'conflicts' not in columns:
                print("添加'conflicts'字段...")
                conn.execute(text('ALTER TABLE recurring_reservation ADD COLUMN conflicts TEXT'))
                print("'conflicts'字段添加成功")
            else:
                print("'conflicts'字段已存在")
                
            if 'total_planned' not in columns:
                print("添加'total_planned'字段...")
                conn.execute(text('ALTER TABLE recurring_reservation ADD COLUMN total_planned INTEGER'))
                print("'total_planned'字段添加成功")
            else:
                print("'total_planned'字段已存在")
                
            if 'created_count' not in columns:
                print("添加'created_count'字段...")
                conn.execute(text('ALTER TABLE recurring_reservation ADD COLUMN created_count INTEGER'))
                print("'created_count'字段添加成功")
            else:
                print("'created_count'字段已存在")
            
        print("迁移完成！")
        return True
    except SQLAlchemyError as e:
        print(f"SQLAlchemy错误: {str(e)}")
        return False
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