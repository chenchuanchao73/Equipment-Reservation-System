"""
更新数据库表结构
Update Database Schema
"""
import sqlite3
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

# 导入配置
from config import DATABASE_URL

# 解析SQLite数据库文件路径
db_path = DATABASE_URL.replace("sqlite:///", "")

print(f"数据库路径: {db_path}")

# 连接到数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查reservation表是否存在recurring_reservation_id列
print("检查reservation表结构...")
cursor.execute("PRAGMA table_info(reservation)")
columns = cursor.fetchall()
column_names = [column[1] for column in columns]

if "recurring_reservation_id" not in column_names:
    print("添加recurring_reservation_id列到reservation表...")
    cursor.execute("ALTER TABLE reservation ADD COLUMN recurring_reservation_id INTEGER")
else:
    print("recurring_reservation_id列已存在")

if "is_exception" not in column_names:
    print("添加is_exception列到reservation表...")
    cursor.execute("ALTER TABLE reservation ADD COLUMN is_exception INTEGER DEFAULT 0")
else:
    print("is_exception列已存在")
    # 修改is_exception列类型
    print("修改is_exception列类型为INTEGER...")
    cursor.execute("CREATE TABLE reservation_temp AS SELECT * FROM reservation")
    cursor.execute("DROP TABLE reservation")
    cursor.execute("""
    CREATE TABLE reservation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        equipment_id INTEGER NOT NULL,
        reservation_code TEXT NOT NULL,
        user_name TEXT NOT NULL,
        user_department TEXT NOT NULL,
        user_contact TEXT NOT NULL,
        user_email TEXT,
        start_datetime TIMESTAMP NOT NULL,
        end_datetime TIMESTAMP NOT NULL,
        purpose TEXT,
        status TEXT DEFAULT 'confirmed',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        recurring_reservation_id INTEGER,
        is_exception INTEGER DEFAULT 0,
        FOREIGN KEY (equipment_id) REFERENCES equipment (id),
        FOREIGN KEY (recurring_reservation_id) REFERENCES recurring_reservation (id)
    )
    """)
    cursor.execute("INSERT INTO reservation SELECT * FROM reservation_temp")
    cursor.execute("DROP TABLE reservation_temp")

# 创建recurring_reservation表
print("创建recurring_reservation表...")
cursor.execute("""
CREATE TABLE IF NOT EXISTS recurring_reservation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipment_id INTEGER NOT NULL,
    pattern_type TEXT NOT NULL,
    days_of_week TEXT,
    days_of_month TEXT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    user_name TEXT NOT NULL,
    user_department TEXT NOT NULL,
    user_contact TEXT NOT NULL,
    user_email TEXT,
    purpose TEXT,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (equipment_id) REFERENCES equipment (id)
)
""")

# 提交更改
conn.commit()

# 验证表结构
print("\n验证表结构...")
cursor.execute("PRAGMA table_info(reservation)")
columns = cursor.fetchall()
print("reservation表列:")
for column in columns:
    print(f"  {column[1]} ({column[2]})")

cursor.execute("PRAGMA table_info(recurring_reservation)")
columns = cursor.fetchall()
print("\nrecurring_reservation表列:")
for column in columns:
    print(f"  {column[1]} ({column[2]})")

# 关闭连接
conn.close()

print("\n数据库表结构更新完成！")
