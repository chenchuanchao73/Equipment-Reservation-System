"""
查询数据库内容的脚本
"""
import sqlite3
import os
from pathlib import Path

# 获取数据库路径
db_path = os.path.join(Path(__file__).resolve().parent, "database.db")
print(f"数据库路径: {db_path}")

# 连接数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 获取所有表名
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("\n所有表:")
for table in tables:
    print(f"- {table[0]}")

# 查询admin表
print("\n管理员表(admin)内容:")
try:
    cursor.execute("SELECT * FROM admin")
    admins = cursor.fetchall()
    
    # 获取列名
    cursor.execute("PRAGMA table_info(admin)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    # 打印列名
    print(" | ".join(column_names))
    print("-" * 80)
    
    # 打印数据
    for admin in admins:
        print(" | ".join(str(field) for field in admin))
except sqlite3.OperationalError as e:
    print(f"查询admin表出错: {e}")

# 关闭连接
conn.close()
