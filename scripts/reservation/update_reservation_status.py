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

# 检查命令行参数
if len(sys.argv) < 3:
    print("用法: python update_reservation_status.py <预约ID> <新状态>")
    print("状态选项: confirmed, cancelled, in_use, expired")
    sys.exit(1)

reservation_id = sys.argv[1]
new_status = sys.argv[2]

# 验证状态值
valid_statuses = ['confirmed', 'cancelled', 'in_use', 'expired']
if new_status not in valid_statuses:
    print(f"错误: 无效的状态值 '{new_status}'")
    print(f"有效的状态值: {', '.join(valid_statuses)}")
    sys.exit(1)

# 查询当前状态
try:
    cursor.execute("""
    SELECT id, reservation_number, reservation_code, status
    FROM reservation
    WHERE id = ?;
    """, (reservation_id,))
    
    reservation = cursor.fetchone()
    if not reservation:
        print(f"错误: 未找到ID为 {reservation_id} 的预约")
        sys.exit(1)
    
    res_dict = dict(reservation)
    print(f"当前状态: ID: {res_dict['id']}, 预约序号: {res_dict.get('reservation_number', 'N/A')}, 预约码: {res_dict['reservation_code']}, 状态: {res_dict['status']}")
    
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
    
except sqlite3.OperationalError as e:
    print(f"数据库操作错误: {e}")
except Exception as e:
    print(f"发生错误: {e}")
finally:
    # 关闭连接
    conn.close()
