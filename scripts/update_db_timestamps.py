"""
更新数据库中的时间戳字段
Update timestamp fields in the database
"""
import os
import sys
import sqlite3
from datetime import datetime, timedelta, timezone
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 数据库路径
DB_PATH = os.path.join('equipment_reservation.db')

def convert_to_beijing_time(dt_str):
    """
    将UTC时间字符串转换为北京时间字符串
    Convert UTC time string to Beijing time string
    """
    if not dt_str:
        return dt_str

    try:
        # 解析日期时间字符串
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00').replace(' ', 'T'))

        # 如果没有时区信息，假定它是UTC时间
        if dt.tzinfo is None:
            # 添加8小时得到北京时间
            beijing_dt = dt + timedelta(hours=8)
        else:
            # 已经有时区信息，转换为UTC+8
            beijing_dt = dt.astimezone(timezone(timedelta(hours=8)))

        # 返回格式化的字符串
        return beijing_dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        logger.error(f"转换时间 '{dt_str}' 失败: {str(e)}")
        return dt_str

def get_tables_with_timestamp_columns(conn):
    """
    获取包含时间戳字段的表
    Get tables with timestamp columns
    """
    cursor = conn.cursor()

    # 获取所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    # 查找包含created_at或updated_at字段的表
    tables_with_timestamps = []
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        columns = [row[1] for row in cursor.fetchall()]
        timestamp_columns = []

        if 'created_at' in columns:
            timestamp_columns.append('created_at')
        if 'updated_at' in columns:
            timestamp_columns.append('updated_at')

        if timestamp_columns:
            tables_with_timestamps.append((table, timestamp_columns))

    return tables_with_timestamps

def update_timestamps(conn, table, columns):
    """
    更新表中的时间戳字段
    Update timestamp fields in a table
    """
    cursor = conn.cursor()

    # 获取表中的所有记录
    cursor.execute(f"SELECT * FROM {table};")
    rows = cursor.fetchall()

    # 获取列名
    cursor.execute(f"PRAGMA table_info({table});")
    column_info = cursor.fetchall()
    column_names = [col[1] for col in column_info]

    # 更新每条记录
    updated_count = 0
    for row in rows:
        row_id = row[0]  # 假设第一列是ID

        # 构建更新语句
        updates = []
        for col in columns:
            col_index = column_names.index(col)
            old_value = row[col_index]

            if old_value:
                # 转换为北京时间
                new_value = convert_to_beijing_time(old_value)

                if new_value != old_value:
                    updates.append(f"{col} = '{new_value}'")

        if updates:
            # 执行更新
            update_sql = f"UPDATE {table} SET {', '.join(updates)} WHERE id = {row_id};"
            cursor.execute(update_sql)
            updated_count += 1

    # 提交更改
    conn.commit()

    return updated_count

def main():
    """主函数"""
    logger.info(f"开始更新数据库时间戳...")

    # 检查数据库文件是否存在
    if not os.path.exists(DB_PATH):
        logger.error(f"数据库文件不存在: {DB_PATH}")
        return

    try:
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)

        # 获取包含时间戳字段的表
        tables_with_timestamps = get_tables_with_timestamp_columns(conn)
        logger.info(f"找到 {len(tables_with_timestamps)} 个包含时间戳字段的表")

        # 更新每个表
        for table, columns in tables_with_timestamps:
            logger.info(f"更新表 '{table}' 的时间戳字段: {', '.join(columns)}")
            updated_count = update_timestamps(conn, table, columns)
            logger.info(f"表 '{table}' 中更新了 {updated_count} 条记录")

        # 关闭连接
        conn.close()

        logger.info("数据库时间戳更新完成")
    except Exception as e:
        logger.error(f"更新数据库时间戳时出错: {str(e)}")

if __name__ == '__main__':
    main()
