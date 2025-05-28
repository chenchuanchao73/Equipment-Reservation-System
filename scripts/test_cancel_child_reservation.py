#!/usr/bin/env python
"""
测试取消循环预约的子预约功能
Test cancellation of child reservations in recurring reservation
"""
import sys
import os
import requests
from pathlib import Path
from pprint import pprint

# 获取项目根目录
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

def test_cancel_child_reservation():
    """测试取消循环预约的子预约"""
    print("开始测试取消循环预约子预约功能...")
    
    # 设置基本URL
    base_url = "http://localhost:8000"  # 根据实际环境修改
    
    # 步骤1: 获取所有循环预约
    response = requests.get(f"{base_url}/api/recurring-reservation/")
    if response.status_code != 200:
        print(f"获取循环预约失败: {response.status_code}, {response.text}")
        return
    
    data = response.json()
    recurring_reservations = data.get("items", [])
    
    if not recurring_reservations:
        print("没有找到任何循环预约")
        return
    
    # 获取第一个循环预约
    recurring_reservation = recurring_reservations[0]
    print(f"找到循环预约: ID={recurring_reservation.get('id')}, 预约码={recurring_reservation.get('reservation_code')}")
    
    # 步骤2: 获取该循环预约的子预约
    response = requests.get(f"{base_url}/api/recurring-reservation/{recurring_reservation.get('id')}/reservations")
    if response.status_code != 200:
        print(f"获取子预约失败: {response.status_code}, {response.text}")
        return
    
    child_reservations = response.json()
    
    if not child_reservations:
        print("没有找到任何子预约")
        return
    
    # 获取第一个子预约
    child_reservation = child_reservations[0]
    print(f"找到子预约: ID={child_reservation.get('id')}, 预约序号={child_reservation.get('reservation_number')}")
    
    # 步骤3: 尝试取消该子预约
    reservation_code = child_reservation.get('reservation_code')
    reservation_number = child_reservation.get('reservation_number')
    
    print(f"尝试取消子预约: 预约码={reservation_code}, 预约序号={reservation_number}")
    
    # 构建取消请求
    cancel_data = {
        "reservation_number": reservation_number,
        "lang": "zh_CN"
    }
    
    response = requests.post(
        f"{base_url}/api/reservation/cancel/code/{reservation_code}",
        json=cancel_data
    )
    
    print(f"取消响应: 状态码={response.status_code}")
    pprint(response.json())
    
    # 步骤4: 验证取消结果
    if response.json().get("success", False):
        print("取消成功")
        
        # 检查预约状态
        response = requests.get(f"{base_url}/api/reservation/number/{reservation_number}")
        if response.status_code == 200:
            reservation_data = response.json()
            if reservation_data.get("success", False):
                status = reservation_data.get("data", {}).get("status")
                print(f"预约当前状态: {status}")
                if status == "cancelled":
                    print("验证成功: 预约状态已变为cancelled")
                else:
                    print(f"验证失败: 预约状态为{status}，而非cancelled")
            else:
                print(f"获取预约详情失败: {reservation_data.get('message')}")
        else:
            print(f"获取预约详情失败: {response.status_code}, {response.text}")
    else:
        print(f"取消失败: {response.json().get('message')}")
    
    print("\n测试完成")

if __name__ == "__main__":
    test_cancel_child_reservation() 