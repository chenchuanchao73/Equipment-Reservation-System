import sqlite3
import json
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

# 查询设备类别表
print("查询设备类别表:")
try:
    cursor.execute("SELECT * FROM equipment_category;")
    categories = cursor.fetchall()
    for category in categories:
        # 将Row对象转换为字典
        category_dict = dict(category)
        # 将字典转换为JSON字符串并格式化输出
        print(json.dumps(category_dict, indent=2, ensure_ascii=False))
except sqlite3.OperationalError as e:
    print(f"设备类别表查询错误: {e}")

# 查询设备表中的类别字段
print("\n查询设备表中的类别字段:")
try:
    cursor.execute("SELECT id, name, category FROM equipment;")
    equipments = cursor.fetchall()
    for equipment in equipments:
        print(f"ID: {equipment['id']}, 名称: {equipment['name']}, 类别: {equipment['category']}")
except sqlite3.OperationalError as e:
    print(f"设备表查询错误: {e}")

# 查询预约表中的设备信息
print("\n查询预约表中的设备信息:")
try:
    cursor.execute("""
    SELECT r.id, r.reservation_code, r.equipment_id, e.name as equipment_name, e.category as equipment_category
    FROM reservation r
    JOIN equipment e ON r.equipment_id = e.id
    LIMIT 10;
    """)
    reservations = cursor.fetchall()
    for reservation in reservations:
        print(f"预约ID: {reservation['id']}, 预约码: {reservation['reservation_code']}, 设备ID: {reservation['equipment_id']}, 设备名称: {reservation['equipment_name']}, 设备类别: {reservation['equipment_category']}")
except sqlite3.OperationalError as e:
    print(f"预约表查询错误: {e}")

# 关闭连接
conn.close()
