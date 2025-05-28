#!/usr/bin/env python
"""
测试循环预约编号生成逻辑
Test recurring reservation number generation logic
"""
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

# 获取项目根目录
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# 导入相关函数
from backend.utils.code_generator import generate_recurring_reservation_number

def test_recurring_reservation_numbers():
    """测试循环预约编号生成"""
    print("开始测试循环预约编号生成...")

    # 创建一系列日期（模拟一个循环预约在不同日期的子预约）
    start_date = datetime.now().date()
    dates = [start_date + timedelta(days=i*5) for i in range(5)]  # 每隔5天一个预约

    # 测试生成同一系列的预约编号
    base_number = None
    for i, date in enumerate(dates, 1):
        # 注意：在测试环境中，我们不传入数据库会话
        reservation_number, base_number = generate_recurring_reservation_number(date, i, base_number, db=None)
        print(f"子预约 {i} (日期: {date.strftime('%Y-%m-%d')}): {reservation_number}, 基础编号: {base_number}")

    print("\n测试完成，所有子预约应该共享相同的基础编号部分。")
    print("注意：此测试未使用数据库查重功能，实际应用中应传入数据库会话以确保唯一性。")

if __name__ == "__main__":
    test_recurring_reservation_numbers()