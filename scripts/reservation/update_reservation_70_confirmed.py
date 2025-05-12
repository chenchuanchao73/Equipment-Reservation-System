"""
临时脚本：更新ID为70的预约状态为confirmed（已确认）
"""
import sqlite3
import os

# 数据库路径
DB_PATH = "equipment_reservation.db"

# 连接数据库
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 查询当前预约信息
cursor.execute(
    "SELECT id, reservation_number, reservation_code, status, start_datetime, end_datetime FROM reservation WHERE id = ?",
    (70,)
)

reservation = cursor.fetchone()

if reservation:
    print(f"当前预约状态: ID={reservation[0]}, 预约序号={reservation[1]}, "
          f"预约码={reservation[2]}, 状态={reservation[3]}, "
          f"开始时间={reservation[4]}, 结束时间={reservation[5]}")
    
    # 更新状态为"已确认"
    cursor.execute(
        "UPDATE reservation SET status = ? WHERE id = ?",
        ("confirmed", 70)
    )
    
    conn.commit()
    print(f"更新完成，受影响行数: {cursor.rowcount}")
    
    # 验证更新
    cursor.execute(
        "SELECT id, reservation_number, reservation_code, status FROM reservation WHERE id = ?",
        (70,)
    )
    
    updated = cursor.fetchone()
    print(f"预约状态已更新: ID={updated[0]}, 预约序号={updated[1]}, 预约码={updated[2]}, 状态={updated[3]}")
else:
    print(f"未找到ID为70的预约")

# 关闭连接
conn.close()
