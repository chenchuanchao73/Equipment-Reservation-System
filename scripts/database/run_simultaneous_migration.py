#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
执行设备同时预定字段迁移的脚本
Script to execute the simultaneous reservation field migration
"""
import os
import sys
import logging

# 添加项目根目录到路径，确保能导入项目模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import create_engine
from config import DATABASE_URL
from backend.migrations.update_equipment_table import migrate

def main():
    """主函数，执行迁移"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )
    
    # 创建数据库引擎
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}  # 适用于SQLite
    )
    
    # 执行迁移
    logging.info("开始执行设备同时预定字段迁移...")
    
    success = migrate(engine)
    
    if success:
        logging.info("迁移成功完成！")
    else:
        logging.error("迁移失败！")
        sys.exit(1)
    
    logging.info("迁移操作完成")

if __name__ == "__main__":
    main() 