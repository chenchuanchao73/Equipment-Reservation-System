import sqlite3

# 连接到数据库
conn = sqlite3.connect('equipment_reservation.db')
cursor = conn.cursor()

# 获取所有设备类别
cursor.execute("SELECT id, name FROM equipment_category")
categories = {row[0]: row[1] for row in cursor.fetchall()}

print("设备类别映射:")
for category_id, category_name in categories.items():
    print(f"ID: {category_id}, 名称: {category_name}")

# 获取所有设备及其当前类别
cursor.execute("SELECT id, name, category FROM equipment")
equipments = cursor.fetchall()

print("\n更新前的设备类别:")
for equipment in equipments:
    equipment_id, equipment_name, current_category = equipment
    print(f"ID: {equipment_id}, 名称: {equipment_name}, 当前类别: {current_category}")

# 更新设备类别
updated_count = 0
for category_id, full_category_name in categories.items():
    # 提取简短类别名称（假设格式为"简称 全称"）
    short_name = full_category_name.split(' ')[0] if ' ' in full_category_name else full_category_name
    
    # 更新所有使用简短类别名称的设备
    cursor.execute(
        "UPDATE equipment SET category = ? WHERE category = ?",
        (full_category_name, short_name)
    )
    updated_count += cursor.rowcount

# 提交更改
conn.commit()

# 验证更新
cursor.execute("SELECT id, name, category FROM equipment")
updated_equipments = cursor.fetchall()

print(f"\n已更新 {updated_count} 个设备的类别")
print("\n更新后的设备类别:")
for equipment in updated_equipments:
    equipment_id, equipment_name, updated_category = equipment
    print(f"ID: {equipment_id}, 名称: {equipment_name}, 更新后类别: {updated_category}")

# 关闭连接
conn.close()

print("\n设备类别更新完成!")
