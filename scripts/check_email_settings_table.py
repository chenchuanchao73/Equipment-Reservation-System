#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
检查邮件设置表结构
Check email settings table structure
"""

import os
import sys
import sqlite3

# 添加项目根目录到Python路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# 导入数据库配置
from config import DATABASE_URL

# 解析SQLite数据库文件路径
db_path = DATABASE_URL.replace("sqlite:///", "")
print(f"数据库路径: {db_path}")

# 连接到数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查email_settings表结构
print("检查email_settings表结构...")
cursor.execute("PRAGMA table_info(email_settings)")
columns = cursor.fetchall()
print("email_settings表列:")
for column in columns:
    print(f"  {column[1]} ({column[2]})")

# 关闭连接
conn.close()
