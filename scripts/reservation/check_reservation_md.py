"""
检查预约表内容并导出为MD格式
Check reservation table and export to markdown format
"""
import sqlite3
from contextlib import contextmanager
import datetime
import os
from pathlib import Path

# 数据库路径
DB_PATH = Path(__file__).parent / "equipment_reservation.db"

@contextmanager
def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def get_status_name(status):
    """获取状态名称"""
    status_map = {
        "confirmed": "已确认",
        "in_use": "使用中",
        "expired": "已过期",
        "cancelled": "已取消"
    }
    return status_map.get(status, status)

def export_reservations_to_md():
    """导出预约表内容为MD格式"""
    md_content = "# 预约管理系统 - 预约记录\n\n"
    md_content += f"导出时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    with get_db_connection() as conn:
        # 获取设备映射
        equipment_map = {}
        equipment_cursor = conn.execute("SELECT id, name FROM equipment")
        for row in equipment_cursor:
            equipment_map[row['id']] = row['name']
        
        # 获取预约记录
        cursor = conn.execute("""
            SELECT id, reservation_number, equipment_id, reservation_code, user_name, 
                   user_department, user_contact, user_email, start_datetime, end_datetime,
                   purpose, status, created_at
            FROM reservation
            ORDER BY created_at DESC
        """)
        
        md_content += "## 预约记录列表\n\n"
        md_content += "| 预约编号 | 设备名称 | 预约者 | 部门 | 联系方式 | 开始时间 | 结束时间 | 状态 | 创建时间 |\n"
        md_content += "|---------|--------|--------|-----|---------|--------|--------|------|--------|\n"
        
        for row in cursor:
            equipment_name = equipment_map.get(row['equipment_id'], f"未知设备(ID:{row['equipment_id']})")
            start_time = datetime.datetime.fromisoformat(row['start_datetime'])
            end_time = datetime.datetime.fromisoformat(row['end_datetime'])
            created_at = datetime.datetime.fromisoformat(row['created_at'])
            
            md_content += f"| {row['reservation_number']} | {equipment_name} | {row['user_name']} | {row['user_department']} | "
            md_content += f"{row['user_contact']} | {start_time.strftime('%Y-%m-%d %H:%M')} | {end_time.strftime('%Y-%m-%d %H:%M')} | "
            md_content += f"{get_status_name(row['status'])} | {created_at.strftime('%Y-%m-%d %H:%M')} |\n"
        
        # 添加状态统计
        cursor = conn.execute("""
            SELECT status, COUNT(*) as count 
            FROM reservation 
            GROUP BY status
        """)
        
        md_content += "\n## 预约状态统计\n\n"
        md_content += "| 状态 | 数量 |\n"
        md_content += "|------|------|\n"
        
        for row in cursor:
            md_content += f"| {get_status_name(row['status'])} | {row['count']} |\n"
            
    # 保存到文件
    output_file = Path(__file__).parent / "reservation_records.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    print(f"预约记录已导出到: {output_file}")
    return output_file

if __name__ == "__main__":
    output_file = export_reservations_to_md()
    print(f"预约记录已成功导出到: {output_file}")