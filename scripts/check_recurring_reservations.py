#!/usr/bin/env python
"""
检查循环预约及其子预约的序号格式
Check reservation numbers for recurring reservations
"""
import sqlite3
import os
from pathlib import Path

# 确定项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

def check_recurring_reservation_numbers():
    """查看循环预约的子预约编号格式"""
    # 连接到数据库
    db_path = os.path.join(BASE_DIR, 'equipment_reservation.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 查询循环预约
    cursor.execute("""
        SELECT id, reservation_code, user_name, created_at 
        FROM recurring_reservation 
        ORDER BY id DESC 
        LIMIT 5
    """)
    recurring_reservations = cursor.fetchall()
    
    if not recurring_reservations:
        print("未找到循环预约记录")
        conn.close()
        return
    
    print("\n找到循环预约记录:")
    print("ID | 预约码 | 用户名 | 创建时间")
    print("-" * 80)
    for res in recurring_reservations:
        print(f"{res[0]} | {res[1]} | {res[2]} | {res[3]}")
    
    # 对每个循环预约，查找其子预约
    for recurring_res in recurring_reservations:
        recurring_id = recurring_res[0]
        recurring_code = recurring_res[1]
        
        print(f"\n循环预约 ID={recurring_id}, 预约码={recurring_code} 的子预约:")
        
        # 查询该循环预约的子预约
        cursor.execute("""
            SELECT id, reservation_code, reservation_number, created_at 
            FROM reservation 
            WHERE recurring_reservation_id = ? OR reservation_code = ?
            ORDER BY start_datetime
            LIMIT 10
        """, (recurring_id, recurring_code))
        
        child_reservations = cursor.fetchall()
        
        if not child_reservations:
            print("  未找到子预约")
            continue
        
        print("  ID | 预约码 | 预约编号 | 创建时间")
        print("  " + "-" * 78)
        for child in child_reservations:
            print(f"  {child[0]} | {child[1]} | {child[2]} | {child[3]}")
    
    conn.close()

if __name__ == "__main__":
    check_recurring_reservation_numbers() 