import sqlite3
import json
import os
from datetime import datetime

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 连接到数据库
db_path = os.path.join(current_dir, 'equipment_reservation.db')
print(f"数据库路径: {db_path}")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row  # 使结果以字典形式返回

# 创建游标
cursor = conn.cursor()

# 检查循环预定表是否存在
print("\n检查循环预定表是否存在:")
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='recurring_reservation';")
    table_exists = cursor.fetchone()
    if table_exists:
        print("循环预定表存在")
    else:
        print("循环预定表不存在")
except sqlite3.OperationalError as e:
    print(f"检查表存在错误: {e}")

# 查询循环预定表
print("\n查询循环预定表:")
try:
    cursor.execute("SELECT * FROM recurring_reservation;")
    recurring_reservations = cursor.fetchall()
    print(f"总共找到 {len(recurring_reservations)} 条循环预定")
    for rr in recurring_reservations:
        # 将Row对象转换为字典
        rr_dict = dict(rr)
        # 将字典转换为JSON字符串并格式化输出
        print(json.dumps(rr_dict, indent=2, ensure_ascii=False))
        
        # 查询该循环预定的预定码
        res_code = rr_dict.get('reservation_code')
        if res_code:
            print(f"\n查询循环预定码 {res_code} 的所有子预定:")
            cursor.execute("SELECT id, reservation_code, status, start_datetime, end_datetime, recurring_reservation_id FROM reservation WHERE reservation_code = ?;", (res_code,))
            child_reservations = cursor.fetchall()
            print(f"找到 {len(child_reservations)} 条子预定")
            for cr in child_reservations:
                cr_dict = dict(cr)
                # 格式化日期时间显示
                if 'start_datetime' in cr_dict and cr_dict['start_datetime']:
                    try:
                        start_dt = datetime.fromisoformat(cr_dict['start_datetime'].replace('Z', '+00:00'))
                        cr_dict['start_datetime'] = start_dt.strftime('%Y-%m-%d %H:%M:%S')
                    except Exception as e:
                        print(f"日期转换错误: {e}")
                if 'end_datetime' in cr_dict and cr_dict['end_datetime']:
                    try:
                        end_dt = datetime.fromisoformat(cr_dict['end_datetime'].replace('Z', '+00:00'))
                        cr_dict['end_datetime'] = end_dt.strftime('%Y-%m-%d %H:%M:%S')
                    except Exception as e:
                        print(f"日期转换错误: {e}")
                print(json.dumps(cr_dict, indent=2, ensure_ascii=False))
except sqlite3.OperationalError as e:
    print(f"循环预定表查询错误: {e}")

# 查询使用特定预约码的所有预约记录，无论是否关联到循环预约
print("\n查询使用特定预约码的所有预约记录:")
try:
    # 假设我们已有一个预约码 SNPXSUQW - 如果这不是您系统中的正确预约码，请替换它
    search_code = "SNPXSUQW"
    print(f"搜索预约码: {search_code}")
    
    cursor.execute("""
    SELECT r.id, r.reservation_code, r.status, r.start_datetime, r.end_datetime, 
           r.recurring_reservation_id, r.user_name, r.equipment_id, e.name as equipment_name
    FROM reservation r
    LEFT JOIN equipment e ON r.equipment_id = e.id
    WHERE r.reservation_code = ?;
    """, (search_code,))
    reservations = cursor.fetchall()
    print(f"找到 {len(reservations)} 条记录")
    
    for res in reservations:
        res_dict = dict(res)
        # 格式化日期时间
        if 'start_datetime' in res_dict and res_dict['start_datetime']:
            try:
                start_dt = datetime.fromisoformat(res_dict['start_datetime'].replace('Z', '+00:00'))
                res_dict['start_datetime'] = start_dt.strftime('%Y-%m-%d %H:%M:%S')
            except Exception as e:
                print(f"日期转换错误: {e}")
        if 'end_datetime' in res_dict and res_dict['end_datetime']:
            try:
                end_dt = datetime.fromisoformat(res_dict['end_datetime'].replace('Z', '+00:00'))
                res_dict['end_datetime'] = end_dt.strftime('%Y-%m-%d %H:%M:%S')
            except Exception as e:
                print(f"日期转换错误: {e}")
        print(json.dumps(res_dict, indent=2, ensure_ascii=False))
except sqlite3.OperationalError as e:
    print(f"预约查询错误: {e}")

# 查询不同日期范围内使用相同预约码的预约
print("\n检查相同预约码在不同日期的预约:")
try:
    cursor.execute("""
    SELECT reservation_code, COUNT(*) as count, 
           GROUP_CONCAT(DISTINCT date(start_datetime)) as dates,
           GROUP_CONCAT(DISTINCT status) as statuses
    FROM reservation 
    GROUP BY reservation_code
    HAVING count > 1;
    """)
    results = cursor.fetchall()
    print(f"找到 {len(results)} 个有多条记录的预约码")
    
    for result in results:
        result_dict = dict(result)
        # 打印详细信息
        print(f"\n预约码: {result_dict['reservation_code']}, 记录数: {result_dict['count']}")
        print(f"日期: {result_dict['dates']}")
        print(f"状态: {result_dict['statuses']}")
        
        # 查询该预约码的所有记录
        cursor.execute("""
        SELECT id, reservation_code, status, date(start_datetime) as date, 
               start_datetime, end_datetime, recurring_reservation_id
        FROM reservation 
        WHERE reservation_code = ?
        ORDER BY start_datetime;
        """, (result_dict['reservation_code'],))
        
        code_records = cursor.fetchall()
        for rec in code_records:
            rec_dict = dict(rec)
            print(f"  ID: {rec_dict['id']}, 日期: {rec_dict['date']}, 状态: {rec_dict['status']}, 循环预约ID: {rec_dict['recurring_reservation_id']}")
except sqlite3.OperationalError as e:
    print(f"预约日期查询错误: {e}")

# 检查是否有预约记录不存在于数据库中的问题（特别针对SNPXSUQW预约码）
print("\n检查前端可能显示但数据库中不存在的日期预约:")
test_code = "SNPXSUQW"
test_dates = [
    "2025-04-28",  # 测试日期1
    "2025-04-29",  # 测试日期2
    "2025-04-30",  # 测试日期3
    "2025-05-26",  # 测试日期4 - 这是您遇到问题的日期
    "2025-05-27",  # 测试日期5
]

for test_date in test_dates:
    try:
        cursor.execute("""
        SELECT id, reservation_code, status, date(start_datetime) as date, 
               start_datetime, end_datetime
        FROM reservation 
        WHERE reservation_code = ? AND date(start_datetime) = ?;
        """, (test_code, test_date))
        
        records = cursor.fetchall()
        if records:
            for rec in records:
                rec_dict = dict(rec)
                print(f"日期 {test_date} 的预约记录存在: ID={rec_dict['id']}, 状态={rec_dict['status']}")
        else:
            print(f"警告: 日期 {test_date} 的预约记录不存在于数据库中")
    except sqlite3.OperationalError as e:
        print(f"检查日期 {test_date} 时出错: {e}")

# 关闭连接
conn.close()