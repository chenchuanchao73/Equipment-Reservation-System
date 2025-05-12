"""
统一数据库中的日期时间格式

这个脚本会:
1. 查找所有预约记录
2. 检查日期时间格式
3. 将所有日期时间格式统一为 'YYYY-MM-DD HH:MM:SS.000000' 格式
4. 不改变实际的时间值
"""
import sqlite3
import os
from datetime import datetime

# 设置日志
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 数据库路径
DB_PATH = "equipment_reservation.db"

def normalize_datetime(dt_str):
    """
    将各种格式的日期时间字符串统一为 'YYYY-MM-DD HH:MM:SS.000000' 格式
    不改变实际的时间值
    """
    if not dt_str:
        return dt_str
    
    # 处理带有'T'的ISO格式
    if 'T' in dt_str:
        try:
            # 解析ISO格式的日期时间
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            # 转换为标准格式
            return dt.strftime('%Y-%m-%d %H:%M:%S.000000')
        except Exception as e:
            logger.error(f"解析日期时间 '{dt_str}' 时出错: {str(e)}")
            return dt_str
    
    # 处理已经是标准格式但没有微秒部分的日期时间
    if '.' not in dt_str:
        try:
            # 解析没有微秒部分的日期时间
            dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
            # 转换为带微秒的标准格式
            return dt.strftime('%Y-%m-%d %H:%M:%S.000000')
        except Exception as e:
            logger.error(f"解析日期时间 '{dt_str}' 时出错: {str(e)}")
            return dt_str
    
    # 已经是标准格式的日期时间
    return dt_str

def main():
    """主函数"""
    try:
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 查询所有预约记录
        cursor.execute("SELECT id, reservation_number, start_datetime, end_datetime FROM reservation")
        reservations = cursor.fetchall()
        
        logger.info(f"找到 {len(reservations)} 条预约记录")
        
        # 统计需要更新的记录数
        updated_count = 0
        
        # 遍历所有预约记录
        for res in reservations:
            res_id, res_number, start_dt, end_dt = res
            
            # 检查并标准化开始时间和结束时间
            new_start_dt = normalize_datetime(start_dt)
            new_end_dt = normalize_datetime(end_dt)
            
            # 如果格式已经改变，则更新数据库
            if new_start_dt != start_dt or new_end_dt != end_dt:
                logger.info(f"更新预约 ID={res_id}, 预约序号={res_number}:")
                logger.info(f"  开始时间: '{start_dt}' -> '{new_start_dt}'")
                logger.info(f"  结束时间: '{end_dt}' -> '{new_end_dt}'")
                
                cursor.execute(
                    "UPDATE reservation SET start_datetime = ?, end_datetime = ? WHERE id = ?",
                    (new_start_dt, new_end_dt, res_id)
                )
                
                updated_count += 1
        
        # 提交更改
        conn.commit()
        
        logger.info(f"已更新 {updated_count} 条预约记录的日期时间格式")
        
        # 验证更新
        cursor.execute("SELECT id, reservation_number, start_datetime, end_datetime FROM reservation LIMIT 10")
        sample_reservations = cursor.fetchall()
        
        logger.info("更新后的样本记录:")
        for res in sample_reservations:
            logger.info(f"ID={res[0]}, 预约序号={res[1]}, 开始时间='{res[2]}', 结束时间='{res[3]}'")
        
        # 关闭连接
        conn.close()
        
        logger.info("日期时间格式统一完成")
        
    except Exception as e:
        logger.error(f"统一日期时间格式时出错: {str(e)}")
        logger.exception("详细错误信息:")

if __name__ == "__main__":
    main()
