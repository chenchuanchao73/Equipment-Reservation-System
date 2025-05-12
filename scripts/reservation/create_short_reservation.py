"""
创建一个短时间预约（25分钟）用于测试日历视图
"""
import sqlite3
import os
import random
import string
from datetime import datetime

# 生成随机预约码
def generate_reservation_code(length=8):
    """生成随机预约码"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

# 生成预约序号
def generate_reservation_number():
    """生成预约序号"""
    now = datetime.now()
    random_num = random.randint(1000, 9999)
    return f"RN-{now.strftime('%Y%m%d')}-{random_num}"

# 数据库路径
DB_PATH = "equipment_reservation.db"

# 连接数据库
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 创建短时间预约
reservation_code = generate_reservation_code()
reservation_number = generate_reservation_number()
equipment_id = 1  # 假设ID为1的设备是P1F Mic
equipment_name = "P1F Mic"
user_id = 1  # 假设ID为1的用户是管理员
user_name = "测试用户"
user_department = "测试部门"
start_datetime = "2025-04-30 16:35:00.000000"
end_datetime = "2025-04-30 17:00:00.000000"
status = "in_use"
created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S.000000")

# 插入预约记录
cursor.execute("""
INSERT INTO reservation (
    reservation_code, reservation_number, equipment_id, equipment_name,
    user_id, user_name, user_department, start_datetime, end_datetime,
    status, created_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    reservation_code, reservation_number, equipment_id, equipment_name,
    user_id, user_name, user_department, start_datetime, end_datetime,
    status, created_at
))

# 提交更改
conn.commit()

# 验证插入
cursor.execute("""
SELECT id, reservation_code, reservation_number, equipment_name, user_name,
       start_datetime, end_datetime, status
FROM reservation
WHERE reservation_code = ?
""", (reservation_code,))

reservation = cursor.fetchone()
print("创建的预约:")
print(f"ID: {reservation[0]}")
print(f"预约码: {reservation[1]}")
print(f"预约序号: {reservation[2]}")
print(f"设备: {reservation[3]}")
print(f"用户: {reservation[4]}")
print(f"开始时间: {reservation[5]}")
print(f"结束时间: {reservation[6]}")
print(f"状态: {reservation[7]}")

# 关闭连接
conn.close()

print("\n预约创建成功！请刷新日历视图查看效果。")
