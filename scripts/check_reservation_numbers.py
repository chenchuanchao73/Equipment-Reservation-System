#!/usr/bin/env python
"""
查看数据库中的预约编号
Check reservation numbers in the database
"""
import sqlite3
import os
from pathlib import Path

# 确定项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

def check_reservation_numbers():
    """查看预约编号"""
    # 连接到数据库
    db_path = os.path.join(BASE_DIR, 'equipment_reservation.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询最新的10条预约记录
    cursor.execute("""
        SELECT id, reservation_code, reservation_number, created_at 
        FROM reservation 
        ORDER BY id DESC 
        LIMIT 10
    """)
    reservations = cursor.fetchall()
    
    # 显示结果
    print("ID | 预约码 | 预约编号 | 创建时间")
    print("-" * 80)
    for res in reservations:
        print(f"{res[0]} | {res[1]} | {res[2]} | {res[3]}")
        
    # 显示是否有重复的预约编号
    cursor.execute("""
        SELECT reservation_number, COUNT(*) 
        FROM reservation 
        GROUP BY reservation_number 
        HAVING COUNT(*) > 1
    """)
    duplicates = cursor.fetchall()
    
    if duplicates:
        print("\n发现重复的预约编号:")
        for dup in duplicates:
            print(f"- {dup[0]}: {dup[1]}次")
    else:
        print("\n没有发现重复的预约编号!")
    
    conn.close()

if __name__ == "__main__":
    check_reservation_numbers() 