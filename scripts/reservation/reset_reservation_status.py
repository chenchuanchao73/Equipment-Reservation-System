#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
重置预约状态脚本
将预约码为SNPXSUQW的所有预约记录的状态从cancelled改回confirmed
"""

import sqlite3
import os
import sys
from datetime import datetime

# 数据库路径
DB_PATH = "equipment_reservation.db"

def main():
    # 检查数据库文件是否存在
    if not os.path.exists(DB_PATH):
        print(f"错误: 数据库文件 {DB_PATH} 不存在")
        sys.exit(1)
    
    print(f"数据库路径: {os.path.abspath(DB_PATH)}")
    
    try:
        # 连接到数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 查询预约码为SNPXSUQW的所有预约记录
        reservation_code = "SNPXSUQW"
        cursor.execute(
            "SELECT id, reservation_number, reservation_code, status, start_datetime, end_datetime FROM reservation WHERE reservation_code = ?",
            (reservation_code,)
        )
        
        reservations = cursor.fetchall()
        
        if not reservations:
            print(f"未找到预约码为 {reservation_code} 的预约记录")
            conn.close()
            sys.exit(0)
        
        print(f"\n找到 {len(reservations)} 条预约记录:")
        for res in reservations:
            print(f"ID: {res[0]}, 预约序号: {res[1]}, 预约码: {res[2]}, 状态: {res[3]}, 开始时间: {res[4]}, 结束时间: {res[5]}")
        
        # 确认是否继续
        confirm = input("\n是否将这些预约记录的状态从cancelled改回confirmed? (y/n): ")
        if confirm.lower() != 'y':
            print("操作已取消")
            conn.close()
            sys.exit(0)
        
        # 更新预约记录的状态
        cursor.execute(
            "UPDATE reservation SET status = 'confirmed' WHERE reservation_code = ? AND status = 'cancelled'",
            (reservation_code,)
        )
        
        # 提交更改
        conn.commit()
        
        # 查询更新后的预约记录
        cursor.execute(
            "SELECT id, reservation_number, reservation_code, status, start_datetime, end_datetime FROM reservation WHERE reservation_code = ?",
            (reservation_code,)
        )
        
        updated_reservations = cursor.fetchall()
        
        print(f"\n更新后的预约记录:")
        for res in updated_reservations:
            print(f"ID: {res[0]}, 预约序号: {res[1]}, 预约码: {res[2]}, 状态: {res[3]}, 开始时间: {res[4]}, 结束时间: {res[5]}")
        
        print(f"\n成功将 {cursor.rowcount} 条预约记录的状态从cancelled改回confirmed")
        
        # 关闭连接
        conn.close()
        
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
