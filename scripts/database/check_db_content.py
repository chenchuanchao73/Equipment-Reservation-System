#!/usr/bin/env python3
"""
查看数据库内容的临时脚本
"""
import sqlite3
import os
import sys
from pathlib import Path

# 获取当前文件所在目录
current_path = Path(__file__).parent.absolute()

# 数据库文件路径
db_path = os.path.join(current_path, "equipment_reservation.db")

def print_separator(title):
    """打印分隔线"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def show_tables():
    """显示所有表"""
    print_separator("数据库表")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("数据库中没有表")
        else:
            print(f"数据库中共有 {len(tables)} 个表:")
            for i, table in enumerate(tables, 1):
                print(f"{i}. {table[0]}")
        
        conn.close()
    except Exception as e:
        print(f"查询表时出错: {str(e)}")

def show_table_schema(table_name):
    """显示表结构"""
    print_separator(f"表结构: {table_name}")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        if not columns:
            print(f"表 {table_name} 不存在或没有列")
        else:
            print(f"表 {table_name} 的结构:")
            print(f"{'序号':<5} {'列名':<20} {'类型':<10} {'非空':<5} {'默认值':<15} {'主键':<5}")
            print("-" * 70)
            for col in columns:
                cid, name, type_, notnull, dflt_value, pk = col
                print(f"{cid:<5} {name:<20} {type_:<10} {notnull:<5} {str(dflt_value):<15} {pk:<5}")
        
        conn.close()
    except Exception as e:
        print(f"查询表结构时出错: {str(e)}")

def show_table_data(table_name, limit=10):
    """显示表数据"""
    print_separator(f"表数据: {table_name} (最多 {limit} 条)")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取表的列名
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # 查询数据
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit};")
        rows = cursor.fetchall()
        
        if not rows:
            print(f"表 {table_name} 中没有数据")
        else:
            # 打印列名
            header = " | ".join(f"{name}" for name in column_names)
            print(header)
            print("-" * len(header))
            
            # 打印数据
            for row in rows:
                formatted_row = []
                for i, val in enumerate(row):
                    # 处理长字符串显示
                    if isinstance(val, str) and len(val) > 20:
                        formatted_row.append(f"{val[:17]}...")
                    else:
                        formatted_row.append(str(val))
                print(" | ".join(formatted_row))
            
            # 查询表中总记录数
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            total_count = cursor.fetchone()[0]
            print(f"\n总记录数: {total_count} 条")
        
        conn.close()
    except Exception as e:
        print(f"查询表数据时出错: {str(e)}")

def show_reservation_details():
    """特别查看预约表中的数据，包括reservation_number字段"""
    print_separator("预约表详细信息")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查预约表是否有reservation_number字段
        cursor.execute("PRAGMA table_info(reservation);")
        columns = cursor.fetchall()
        has_reservation_number = any(col[1] == 'reservation_number' for col in columns)
        
        if has_reservation_number:
            print("预约表包含 reservation_number 字段")
            # 查询包含reservation_number的记录
            cursor.execute("""
                SELECT id, reservation_number, reservation_code, user_name, start_datetime, status
                FROM reservation
                ORDER BY id DESC
                LIMIT 20;
            """)
            records = cursor.fetchall()
            
            if records:
                print("\n最近的预约记录:")
                print(f"{'ID':<5} {'预约序号':<15} {'预约码':<15} {'用户':<15} {'开始时间':<20} {'状态':<10}")
                print("-" * 80)
                for record in records:
                    id_, res_num, res_code, user, start_time, status = record
                    res_num = res_num if res_num else '空'
                    print(f"{id_:<5} {res_num:<15} {res_code:<15} {user:<15} {start_time:<20} {status:<10}")
            else:
                print("预约表中没有记录")
                
            # 检查空值情况
            cursor.execute("SELECT COUNT(*) FROM reservation WHERE reservation_number IS NULL;")
            null_count = cursor.fetchone()[0]
            print(f"\n预约序号为空的记录数: {null_count}")
        else:
            print("预约表没有 reservation_number 字段")
        
        conn.close()
    except Exception as e:
        print(f"查询预约详情时出错: {str(e)}")

if __name__ == "__main__":
    if not os.path.exists(db_path):
        print(f"错误: 数据库文件不存在: {db_path}")
        sys.exit(1)
    
    print(f"数据库文件: {db_path}")
    
    # 显示所有表
    show_tables()
    
    # 显示预约表结构和数据
    show_table_schema("reservation")
    show_reservation_details()
    
    # 显示设备表结构和数据
    show_table_schema("equipment")
    show_table_data("equipment", limit=5)
    
    # 可以根据需要添加更多表的查询
    print("\n使用以下命令查看其他表的数据:")
    print("python check_db_content.py [表名]")
    
    # 如果提供了表名参数，则显示该表的数据
    if len(sys.argv) > 1:
        table_name = sys.argv[1]
        show_table_schema(table_name)
        show_table_data(table_name)