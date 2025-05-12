import sqlite3
import os

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 连接到数据库
db_path = os.path.join(current_dir, 'equipment_reservation.db')
print(f"数据库路径: {db_path}")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row  # 使结果以字典形式返回

# 创建游标
cursor = conn.cursor()

# 查询最近的预约记录
print("\n查询最近的预约记录:")
try:
    cursor.execute("""
    SELECT id, reservation_number, reservation_code, status, start_datetime, end_datetime
    FROM reservation
    ORDER BY id DESC
    LIMIT 100;
    """)
    
    reservations = cursor.fetchall()
    print(f"找到 {len(reservations)} 条记录")
    
    for res in reservations:
        res_dict = dict(res)
        print(f"ID: {res_dict['id']}, 预约序号: {res_dict.get('reservation_number', 'N/A')}, 预约码: {res_dict['reservation_code']}, 状态: {res_dict['status']}, 开始时间: {res_dict['start_datetime']}, 结束时间: {res_dict['end_datetime']}")
except sqlite3.OperationalError as e:
    print(f"查询错误: {e}")

# 关闭连接
conn.close()
