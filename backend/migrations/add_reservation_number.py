"""
添加预约序号字段的迁移脚本
Script to add reservation number field
"""
import sqlite3
import sys
import os
import logging
from datetime import datetime
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 确定项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 导入工具函数
sys.path.insert(0, str(BASE_DIR))
from backend.utils.code_generator import generate_reservation_number

def add_reservation_number():
    """
    添加预约序号字段并为现有记录生成唯一序号
    Add reservation number field and generate unique numbers for existing records
    """
    # 连接到数据库
    db_path = os.path.join(BASE_DIR, 'equipment_reservation.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    logger.info("检查reservation表是否存在reservation_number列")
    
    # 检查reservation表是否存在reservation_number列
    cursor.execute("PRAGMA table_info(reservation)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    added = False
    
    # 如果不存在reservation_number列，添加它
    if "reservation_number" not in column_names:
        logger.info("添加reservation_number列到reservation表...")
        cursor.execute("ALTER TABLE reservation ADD COLUMN reservation_number VARCHAR(20)")
        added = True
    else:
        logger.info("reservation_number列已存在")
    
    # 为所有没有预约序号的记录生成唯一序号
    cursor.execute("SELECT id FROM reservation WHERE reservation_number IS NULL OR reservation_number = ''")
    reservations = cursor.fetchall()
    
    if reservations:
        logger.info(f"为 {len(reservations)} 条预约记录生成唯一序号")
        
        for res_id in reservations:
            # 生成唯一预约序号
            reservation_number = generate_reservation_number()
            
            # 确保唯一性
            while True:
                cursor.execute("SELECT COUNT(*) FROM reservation WHERE reservation_number = ?", (reservation_number,))
                count = cursor.fetchone()[0]
                if count == 0:
                    break
                reservation_number = generate_reservation_number()
            
            # 更新数据库
            cursor.execute(
                "UPDATE reservation SET reservation_number = ? WHERE id = ?", 
                (reservation_number, res_id[0])
            )
            
            logger.info(f"为预约ID: {res_id[0]} 设置唯一序号: {reservation_number}")
    
    # 提交更改
    conn.commit()
    
    # 创建索引
    logger.info("为reservation_number创建索引")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reservation_number ON reservation(reservation_number)")
    
    conn.commit()
    conn.close()
    
    return added

if __name__ == "__main__":
    try:
        added = add_reservation_number()
        if added:
            logger.info("成功添加预约序号字段并为现有记录生成唯一序号")
        else:
            logger.info("预约序号字段已存在，已为所有必要记录更新唯一序号")
    except Exception as e:
        logger.error(f"添加预约序号字段时出错: {e}")
        sys.exit(1)