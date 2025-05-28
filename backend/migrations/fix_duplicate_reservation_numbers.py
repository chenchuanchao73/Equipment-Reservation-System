"""
修复重复的预约编号
Script to fix duplicate reservation numbers
"""
import sqlite3
import sys
import os
import logging
import time
import random
from datetime import datetime
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 确定项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent

def generate_unique_reservation_number(cursor, reservation_date):
    """生成唯一的预约编号"""
    date_str = reservation_date.strftime("%Y%m%d")
    prefix = f"RN-{date_str}-"
    
    # 获取已存在的最大编号
    cursor.execute(
        "SELECT reservation_number FROM reservation WHERE reservation_number LIKE ? ORDER BY id DESC LIMIT 1", 
        (f"{prefix}%",)
    )
    result = cursor.fetchone()
    
    if result and result[0]:
        try:
            last_number = int(result[0].split('-')[-1])
            new_number = last_number + 1
        except (ValueError, IndexError):
            # 使用时间戳和随机数
            timestamp = int(time.time() * 1000) % 10000
            random_part = random.randint(1, 999)
            new_number = timestamp + random_part
    else:
        # 从1000开始
        new_number = 1000
    
    # 确保至少4位数
    if new_number < 1000:
        new_number += 1000
        
    return f"{prefix}{new_number}"

def fix_duplicate_reservation_numbers():
    """修复重复的预约编号"""
    # 连接到数据库
    db_path = os.path.join(BASE_DIR, 'equipment_reservation.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    logger.info("开始检查重复的预约编号...")
    
    # 查找所有预约
    cursor.execute("SELECT id, reservation_number, created_at FROM reservation ORDER BY id")
    reservations = cursor.fetchall()
    
    # 用于存储已经处理过的编号
    processed_numbers = set()
    fixed_count = 0
    
    for res_id, res_number, created_at in reservations:
        # 如果预约编号已经存在或为空，则生成新的编号
        if res_number in processed_numbers or not res_number:
            # 如果有创建时间，使用创建时间；否则使用当前时间
            if created_at:
                try:
                    res_date = datetime.fromisoformat(created_at.replace(' ', 'T'))
                except (ValueError, TypeError):
                    res_date = datetime.now()
            else:
                res_date = datetime.now()
                
            # 生成新编号
            new_number = generate_unique_reservation_number(cursor, res_date)
            
            # 确保新编号不重复
            while new_number in processed_numbers:
                # 添加随机后缀确保唯一性
                random_suffix = random.randint(1000, 9999)
                new_number = f"{new_number.rsplit('-', 1)[0]}-{random_suffix}"
            
            # 更新数据库
            cursor.execute(
                "UPDATE reservation SET reservation_number = ? WHERE id = ?", 
                (new_number, res_id)
            )
            
            logger.info(f"修复预约ID: {res_id}, 旧编号: {res_number} -> 新编号: {new_number}")
            processed_numbers.add(new_number)
            fixed_count += 1
        else:
            processed_numbers.add(res_number)
    
    # 提交更改
    conn.commit()
    conn.close()
    
    logger.info(f"修复完成，共修复 {fixed_count} 个重复的预约编号")
    return fixed_count

if __name__ == "__main__":
    fix_duplicate_reservation_numbers() 