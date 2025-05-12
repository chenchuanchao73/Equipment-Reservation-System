"""
循环预约API测试脚本
Recurring Reservation API Test Script
"""
import requests
import json
from datetime import date, datetime, timedelta
import time

# API基础URL
BASE_URL = "http://localhost:8000/api"

# 管理员账户信息
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# 存储访问令牌
access_token = None

def print_response(response):
    """打印响应"""
    print(f"状态码: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(response.text)
    print("-" * 50)

def login_admin():
    """管理员登录获取令牌"""
    global access_token
    print("\n管理员登录...")

    # 准备登录数据
    data = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }

    # 发送请求
    response = requests.post(f"{BASE_URL}/admin/login", data=data)
    print_response(response)

    if response.status_code == 200:
        access_token = response.json().get("access_token")
        print(f"登录成功，获取到令牌")
        return True

    print("登录失败")
    return False

def get_auth_headers():
    """获取带有认证令牌的请求头"""
    if not access_token:
        raise ValueError("未登录，无法获取认证令牌")

    return {
        "Authorization": f"Bearer {access_token}"
    }

def test_create_recurring_reservation():
    """测试创建循环预约"""
    print("\n测试创建循环预约...")

    # 使用ID为1的设备（SpeakerA）
    equipment_id = 1  # SpeakerA

    # 准备循环预约数据
    today = date.today()
    start_date = today + timedelta(days=1)  # 明天开始
    end_date = today + timedelta(days=30)   # 30天后结束

    data = {
        "equipment_id": equipment_id,
        "pattern_type": "weekly",
        "days_of_week": [1, 3, 5],  # 周一、周三、周五
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "start_time": "09:00:00",
        "end_time": "11:00:00",
        "user_name": "测试用户",
        "user_department": "测试部门",
        "user_contact": "13800138000",
        "purpose": "测试循环预约",
        "user_email": "test@example.com"
    }

    # 打印请求数据
    print(f"请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")

    # 发送请求
    response = requests.post(f"{BASE_URL}/recurring-reservation/", json=data)
    print_response(response)

    # 如果失败，打印更多信息
    if response.status_code != 200 or not response.json().get("success"):
        print(f"请求URL: {BASE_URL}/recurring-reservation/")
        print(f"请求方法: POST")
        print(f"请求头: {response.request.headers}")
        print(f"响应头: {response.headers}")

    if response.status_code == 200 and response.json().get("success"):
        return response.json().get("data", {}).get("id")

    return None

def test_get_recurring_reservations():
    """测试获取循环预约列表"""
    print("\n测试获取循环预约列表...")
    response = requests.get(f"{BASE_URL}/recurring-reservation/")
    print_response(response)

def test_get_recurring_reservation(recurring_reservation_id):
    """测试获取循环预约详情"""
    print(f"\n测试获取循环预约详情 (ID: {recurring_reservation_id})...")
    response = requests.get(f"{BASE_URL}/recurring-reservation/{recurring_reservation_id}")
    print_response(response)

def test_update_recurring_reservation(recurring_reservation_id):
    """测试更新循环预约"""
    print(f"\n测试更新循环预约 (ID: {recurring_reservation_id})...")

    data = {
        "purpose": "更新的测试目的",
        "end_date": (date.today() + timedelta(days=45)).isoformat()  # 延长结束日期
    }

    # 使用整数参数
    params = {
        "update_future_only": 1
    }

    response = requests.put(f"{BASE_URL}/recurring-reservation/{recurring_reservation_id}", json=data, params=params)
    print_response(response)

def test_get_child_reservations(recurring_reservation_id):
    """测试获取循环预约的子预约"""
    print(f"\n测试获取循环预约的子预约 (ID: {recurring_reservation_id})...")

    # 使用整数参数
    params = {
        "include_past": 0
    }

    response = requests.get(f"{BASE_URL}/recurring-reservation/{recurring_reservation_id}/reservations", params=params)
    print_response(response)

def test_cancel_recurring_reservation(recurring_reservation_id):
    """测试取消循环预约"""
    print(f"\n测试取消循环预约 (ID: {recurring_reservation_id})...")

    # 使用整数参数
    params = {
        "cancel_future_only": 1
    }

    response = requests.post(f"{BASE_URL}/recurring-reservation/cancel/{recurring_reservation_id}", params=params)
    print_response(response)

def main():
    """主函数"""
    print("开始测试循环预约API...")

    # 管理员登录
    if not login_admin():
        print("管理员登录失败，无法继续测试")
        return

    # 创建循环预约
    recurring_reservation_id = test_create_recurring_reservation()
    if not recurring_reservation_id:
        print("创建循环预约失败，无法继续测试")
        return

    # 等待一秒，确保数据已保存
    time.sleep(1)

    # 获取循环预约列表
    test_get_recurring_reservations()

    # 获取循环预约详情
    test_get_recurring_reservation(recurring_reservation_id)

    # 获取循环预约的子预约
    test_get_child_reservations(recurring_reservation_id)

    # 更新循环预约
    test_update_recurring_reservation(recurring_reservation_id)

    # 再次获取循环预约详情，查看更新结果
    test_get_recurring_reservation(recurring_reservation_id)

    # 再次获取循环预约的子预约，查看更新结果
    test_get_child_reservations(recurring_reservation_id)

    # 取消循环预约
    test_cancel_recurring_reservation(recurring_reservation_id)

    # 再次获取循环预约详情，查看取消结果
    test_get_recurring_reservation(recurring_reservation_id)

    print("\n测试完成！")

if __name__ == "__main__":
    main()
