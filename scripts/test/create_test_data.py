"""
创建测试数据脚本
Create test data script

此脚本用于向数据库中插入测试数据，包括单次预约和循环预约，
以便测试日历视图功能。
"""
import sqlite3
import json
import os
import random
import string
from datetime import datetime, timedelta, date, time

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 连接到数据库
db_path = os.path.join(current_dir, 'equipment_reservation.db')
print(f"数据库路径: {db_path}")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row  # 使结果以字典形式返回

# 创建游标
cursor = conn.cursor()

# 生成随机预约码
def generate_reservation_code(length=8):
    """生成随机预约码"""
    return ''.join(random.choices(string.ascii_uppercase, k=length))

# 生成预约序号
def generate_reservation_number(start_datetime):
    """生成预约序号，格式：RN-YYYYMMDD-XXXX"""
    date_str = start_datetime.strftime("%Y%m%d")
    random_num = ''.join(random.choices(string.digits, k=4))
    return f"RN-{date_str}-{random_num}"

# 获取设备列表
def get_equipment_list():
    """获取设备列表"""
    cursor.execute("SELECT id, name, category FROM equipment")
    return cursor.fetchall()

# 创建单次预约
def create_single_reservation(equipment_id, equipment_name, equipment_category, start_datetime, end_datetime, status, user_name, user_department, user_contact, user_email, purpose):
    """创建单次预约"""
    reservation_code = generate_reservation_code()
    reservation_number = generate_reservation_number(start_datetime)
    
    cursor.execute("""
    INSERT INTO reservation (
        equipment_id, reservation_code, reservation_number, user_name, user_department, 
        user_contact, user_email, start_datetime, end_datetime, purpose, status, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        equipment_id, reservation_code, reservation_number, user_name, user_department,
        user_contact, user_email, start_datetime.isoformat(), end_datetime.isoformat(), purpose, status,
        datetime.now().isoformat()
    ))
    
    reservation_id = cursor.lastrowid
    print(f"创建单次预约成功: ID={reservation_id}, 设备={equipment_name}, 预约码={reservation_code}, 状态={status}")
    return reservation_id, reservation_code

# 创建循环预约
def create_recurring_reservation(equipment_id, equipment_name, equipment_category, pattern_type, days_of_week, start_date, end_date, start_time, end_time, user_name, user_department, user_contact, user_email, purpose):
    """创建循环预约"""
    reservation_code = generate_reservation_code()
    
    # 插入循环预约记录
    cursor.execute("""
    INSERT INTO recurring_reservation (
        equipment_id, reservation_code, pattern_type, days_of_week, days_of_month,
        start_date, end_date, start_time, end_time, user_name, user_department,
        user_contact, user_email, purpose, status, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        equipment_id, reservation_code, pattern_type, json.dumps(days_of_week), None,
        start_date.isoformat(), end_date.isoformat(), start_time.isoformat(), end_time.isoformat(),
        user_name, user_department, user_contact, user_email, purpose, "active",
        datetime.now().isoformat()
    ))
    
    recurring_id = cursor.lastrowid
    print(f"创建循环预约成功: ID={recurring_id}, 设备={equipment_name}, 预约码={reservation_code}")
    
    # 生成子预约
    child_reservations = []
    current_date = start_date
    while current_date <= end_date:
        # 检查当前日期是否符合重复模式
        weekday = current_date.weekday()  # 0-6, 0表示周一
        if pattern_type == "weekly" and weekday not in days_of_week:
            current_date += timedelta(days=1)
            continue
        
        # 创建子预约的开始和结束时间
        start_datetime = datetime.combine(current_date, start_time)
        end_datetime = datetime.combine(current_date, end_time)
        
        # 确定状态
        now = datetime.now()
        if start_datetime <= now <= end_datetime:
            status = "in_use"
        elif end_datetime < now:
            status = "expired"
        else:
            status = "confirmed"
        
        # 创建子预约
        reservation_number = generate_reservation_number(start_datetime)
        cursor.execute("""
        INSERT INTO reservation (
            equipment_id, reservation_code, reservation_number, user_name, user_department, 
            user_contact, user_email, start_datetime, end_datetime, purpose, status, 
            recurring_reservation_id, is_exception, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            equipment_id, reservation_code, reservation_number, user_name, user_department,
            user_contact, user_email, start_datetime.isoformat(), end_datetime.isoformat(), purpose, status,
            recurring_id, 0, datetime.now().isoformat()
        ))
        
        child_id = cursor.lastrowid
        child_reservations.append(child_id)
        print(f"  创建子预约: ID={child_id}, 日期={current_date.isoformat()}, 状态={status}")
        
        # 移动到下一天
        current_date += timedelta(days=1)
    
    return recurring_id, reservation_code, child_reservations

# 主函数
def main():
    """主函数"""
    # 获取设备列表
    equipment_list = get_equipment_list()
    if not equipment_list:
        print("错误: 没有找到设备，请先创建设备")
        return
    
    # 用户数据
    users = [
        {
            "name": "张三",
            "department": "研发部",
            "contact": "13800138001",
            "email": "zhangsan@example.com"
        },
        {
            "name": "李四",
            "department": "市场部",
            "contact": "13800138002",
            "email": "lisi@example.com"
        },
        {
            "name": "王五",
            "department": "行政部",
            "contact": "13800138003",
            "email": "wangwu@example.com"
        },
        {
            "name": "赵六",
            "department": "财务部",
            "contact": "13800138004",
            "email": "zhaoliu@example.com"
        },
        {
            "name": "陈传超",
            "department": "技术部",
            "contact": "13800138005",
            "email": "chenchuanchao@example.com"
        }
    ]
    
    # 使用目的
    purposes = [
        "项目演示",
        "培训使用",
        "实验研究",
        "会议使用",
        "日常工作"
    ]
    
    # 创建单次预约
    print("\n创建单次预约...")
    now = datetime.now()
    
    # 创建不同状态的单次预约
    for i in range(15):
        # 随机选择设备和用户
        equipment = random.choice(equipment_list)
        user = random.choice(users)
        purpose = random.choice(purposes)
        
        # 随机日期，在当前日期的前后15天内
        day_offset = random.randint(-15, 15)
        reservation_date = (now + timedelta(days=day_offset)).date()
        
        # 随机时间，8:00 - 18:00
        start_hour = random.randint(8, 17)
        start_minute = random.choice([0, 30])
        duration_hours = random.randint(1, 4)  # 1-4小时
        
        start_datetime = datetime.combine(reservation_date, time(start_hour, start_minute))
        end_datetime = start_datetime + timedelta(hours=duration_hours)
        
        # 确定状态
        if start_datetime <= now <= end_datetime:
            status = "in_use"
        elif end_datetime < now:
            status = "expired"
        elif random.random() < 0.1:  # 10%的概率为已取消
            status = "cancelled"
        else:
            status = "confirmed"
        
        # 创建预约
        create_single_reservation(
            equipment["id"], equipment["name"], equipment["category"],
            start_datetime, end_datetime, status,
            user["name"], user["department"], user["contact"], user["email"],
            purpose
        )
    
    # 创建循环预约
    print("\n创建循环预约...")
    for i in range(3):
        # 随机选择设备和用户
        equipment = random.choice(equipment_list)
        user = random.choice(users)
        purpose = random.choice(purposes)
        
        # 循环预约的起始日期，在当前日期的前后15天内
        start_day_offset = random.randint(-15, 0)
        end_day_offset = random.randint(15, 30)
        start_date = (now + timedelta(days=start_day_offset)).date()
        end_date = (now + timedelta(days=end_day_offset)).date()
        
        # 随机时间，8:00 - 18:00
        start_hour = random.randint(8, 16)
        start_minute = random.choice([0, 30])
        duration_hours = random.randint(1, 2)  # 1-2小时
        
        start_time = time(start_hour, start_minute)
        end_time = time(start_hour + duration_hours, start_minute)
        
        # 每周几
        days_of_week = sorted(random.sample(range(7), random.randint(1, 3)))  # 1-3天
        
        # 创建循环预约
        create_recurring_reservation(
            equipment["id"], equipment["name"], equipment["category"],
            "weekly", days_of_week, start_date, end_date, start_time, end_time,
            user["name"], user["department"], user["contact"], user["email"],
            purpose
        )
    
    # 提交事务
    conn.commit()
    print("\n所有测试数据创建成功!")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"错误: {e}")
        conn.rollback()
    finally:
        conn.close()
