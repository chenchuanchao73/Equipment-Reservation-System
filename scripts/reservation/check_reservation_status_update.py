import sqlite3
import os
import sys

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 连接到数据库
db_path = os.path.join(current_dir, 'equipment_reservation.db')
print(f"数据库路径: {db_path}")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row  # 使结果以字典形式返回

# 创建游标
cursor = conn.cursor()

# 获取预约ID
if len(sys.argv) > 1:
    reservation_id = sys.argv[1]
else:
    reservation_id = input("请输入要查询的预约ID: ")

# 查询预约状态
print(f"\n查询预约ID {reservation_id} 的状态:")
try:
    cursor.execute("""
    SELECT id, reservation_number, reservation_code, status, start_datetime, end_datetime
    FROM reservation
    WHERE id = ?;
    """, (reservation_id,))
    
    reservation = cursor.fetchone()
    if reservation:
        res_dict = dict(reservation)
        print(f"ID: {res_dict['id']}, 预约序号: {res_dict.get('reservation_number', 'N/A')}, 预约码: {res_dict['reservation_code']}, 状态: {res_dict['status']}, 开始时间: {res_dict['start_datetime']}, 结束时间: {res_dict['end_datetime']}")
        
        # 询问是否更新状态
        update = input("\n是否要更新此预约的状态? (y/n): ")
        if update.lower() == 'y':
            new_status = input("请输入新状态 (confirmed/cancelled/in_use/expired): ")
            
            # 更新状态
            cursor.execute("""
            UPDATE reservation
            SET status = ?
            WHERE id = ?;
            """, (new_status, reservation_id))
            
            conn.commit()
            print(f"预约ID {reservation_id} 的状态已更新为 {new_status}")
            
            # 验证更新
            cursor.execute("""
            SELECT id, status FROM reservation WHERE id = ?;
            """, (reservation_id,))
            
            updated = cursor.fetchone()
            print(f"验证: ID {updated['id']} 的状态现在是 {updated['status']}")
    else:
        print(f"未找到ID为 {reservation_id} 的预约")
except sqlite3.OperationalError as e:
    print(f"查询错误: {e}")

# 关闭连接
conn.close()
