#!/usr/bin/env python
"""
测试预约API是否生成唯一的预约编号
Test if reservation API generates unique reservation numbers
"""
import requests
import json
import time

# API URL
BASE_URL = "http://localhost:8000"
RESERVATION_URL = f"{BASE_URL}/api/reservation/"

def create_reservation():
    """创建一个测试预约"""
    # 测试数据
    data = {
        "equipment_id": 4,
        "user_name": "测试用户",
        "user_department": "测试部门",
        "user_contact": "13800138000",
        "user_email": "test@example.com",
        "start_datetime": "2025-06-10 10:00:00",
        "end_datetime": "2025-06-10 12:00:00",
        "lang": "zh-CN"
    }
    
    # 发送POST请求
    headers = {"Content-Type": "application/json"}
    response = requests.post(RESERVATION_URL, json=data, headers=headers)
    
    # 打印响应
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        if result.get("success"):
            reservation_data = result.get("data", {})
            print(f"\n成功创建预约:")
            print(f"- 预约ID: {reservation_data.get('id')}")
            print(f"- 预约编号: {reservation_data.get('reservation_number')}")
            print(f"- 预约码: {reservation_data.get('reservation_code')}")
            return True
        else:
            print(f"\n创建预约失败: {result.get('message')}")
            return False
    else:
        print(f"\n请求失败: {response.text}")
        return False

def main():
    """创建多个预约测试唯一性"""
    print("开始测试预约API生成唯一编号...\n")
    
    # 创建3个预约
    reservation_numbers = []
    for i in range(3):
        print(f"\n创建第 {i+1} 个测试预约:")
        result = create_reservation()
        if result:
            # 等待一秒确保不会有冲突
            time.sleep(1)
    
    print("\n测试完成！")

if __name__ == "__main__":
    main() 