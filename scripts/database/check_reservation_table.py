"""
检查预约表结构
Check Reservation Table Structure
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

# 检查reservation表结构
print("检查reservation表结构...")
cursor.execute("PRAGMA table_info(reservation)")
columns = cursor.fetchall()
print("reservation表列:")
for column in columns:
    print(f"  {column[1]} ({column[2]})")

# 检查recurring_reservation表结构
print("\n检查recurring_reservation表结构...")
cursor.execute("PRAGMA table_info(recurring_reservation)")
columns = cursor.fetchall()
print("recurring_reservation表列:")
for column in columns:
    print(f"  {column[1]} ({column[2]})")

# 关闭连接
conn.close()

print("\n检查完成！")
