"""
添加设备时间段表和相关字段的迁移脚本
"""
import sqlite3
import os
from datetime import datetime

def migrate():
    """
    执行迁移操作
    """
    # 数据库文件路径
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'equipment_reservation.db')
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 开始事务
        cursor.execute('BEGIN TRANSACTION')
        
        # 1. 创建设备时间段表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS equipment_time_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipment_id INTEGER NOT NULL,
            start_datetime TIMESTAMP NOT NULL,
            end_datetime TIMESTAMP NOT NULL,
            current_count INTEGER DEFAULT 1,
            FOREIGN KEY (equipment_id) REFERENCES equipment (id)
        )
        ''')
        
        # 2. 为设备时间段表创建索引
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_equipment_time_slots_equipment_id ON equipment_time_slots (equipment_id)
        ''')
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_equipment_time_slots_datetime ON equipment_time_slots (start_datetime, end_datetime)
        ''')
        
        # 3. 在预约表中添加time_slot_id字段
        cursor.execute('''
        ALTER TABLE reservation ADD COLUMN time_slot_id INTEGER;
        ''')
        
        # 4. 添加外键约束
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_reservation_time_slot_id ON reservation (time_slot_id)
        ''')
        
        # 提交事务
        cursor.execute('COMMIT')
        print("迁移成功: 已添加设备时间段表和相关字段")
        
    except Exception as e:
        # 回滚事务
        cursor.execute('ROLLBACK')
        print(f"迁移失败: {str(e)}")
        raise
    finally:
        # 关闭数据库连接
        conn.close()

if __name__ == "__main__":
    migrate() 