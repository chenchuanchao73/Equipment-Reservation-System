"""
更新循环预约表，添加reservation_code字段
Update recurring_reservation table, add reservation_code field
"""
import sqlite3
import os
import sys
from pathlib import Path

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 数据库路径
DB_PATH = os.path.join(BASE_DIR, "equipment_reservation.db")

def update_database():
    """更新数据库"""
    print(f"正在连接数据库: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 检查reservation_code字段是否已存在
        cursor.execute("PRAGMA table_info(recurring_reservation)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]

        if "reservation_code" not in column_names:
            print("正在添加reservation_code字段...")
            # 先添加普通字段
            cursor.execute("""
            ALTER TABLE recurring_reservation
            ADD COLUMN reservation_code TEXT
            """)
            print("字段添加成功")

            # 生成唯一的预定码并更新现有记录
            print("正在为现有循环预约生成预定码...")
            cursor.execute("SELECT id FROM recurring_reservation")
            recurring_ids = cursor.fetchall()

            # 导入生成预定码的函数
            sys.path.append(str(BASE_DIR))
            from backend.utils.code_generator import generate_reservation_code

            for (recurring_id,) in recurring_ids:
                # 生成唯一的预定码
                while True:
                    code = generate_reservation_code()
                    cursor.execute("SELECT 1 FROM recurring_reservation WHERE reservation_code = ?", (code,))
                    if not cursor.fetchone():
                        cursor.execute("SELECT 1 FROM reservation WHERE reservation_code = ?", (code,))
                        if not cursor.fetchone():
                            break

                # 更新记录
                cursor.execute(
                    "UPDATE recurring_reservation SET reservation_code = ? WHERE id = ?",
                    (code, recurring_id)
                )

                # 更新子预约
                cursor.execute(
                    "UPDATE reservation SET reservation_code = ? WHERE recurring_reservation_id = ?",
                    (code, recurring_id)
                )

            print(f"已为{len(recurring_ids)}个循环预约生成预定码")

            # 添加唯一约束
            print("正在添加唯一约束...")
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_recurring_reservation_code ON recurring_reservation(reservation_code)")
            print("唯一约束添加成功")
        else:
            print("reservation_code字段已存在")

        # 提交更改
        conn.commit()
        print("数据库更新成功")
    except Exception as e:
        print(f"更新数据库时出错: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_database()
