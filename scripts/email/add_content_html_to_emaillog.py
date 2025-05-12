import sqlite3
import os

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "equipment_reservation.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE email_logs ADD COLUMN content_html TEXT")
    print("已添加 content_html 字段")
except Exception as e:
    if "duplicate column name" in str(e):
        print("content_html 字段已存在")
    else:
        print(f"添加失败: {e}")
finally:
    conn.commit()
    conn.close() 