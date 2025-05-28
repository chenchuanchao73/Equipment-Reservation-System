"""
预约序号重复检查工具
Reservation number duplicate checker utility
"""
import logging
import sqlite3
import os
import time
import random
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.models.reservation import Reservation

# 设置日志
logger = logging.getLogger(__name__)

def generate_unique_reservation_number(db, reservation_date):
    """
    生成唯一的预约编号
    Generate unique reservation number
    
    Args:
        db: 数据库会话
        reservation_date: 预约日期
    """
    date_str = reservation_date.strftime("%Y%m%d")
    prefix = f"RN-{date_str}-"
    
    # 查找今天已存在的最大编号
    last_reservation = db.query(Reservation).filter(
        Reservation.reservation_number.like(f"{prefix}%")
    ).order_by(Reservation.reservation_number.desc()).first()
    
    if last_reservation:
        try:
            last_number = int(last_reservation.reservation_number.split('-')[-1])
            new_number = last_number + 1
        except (ValueError, IndexError):
            # 使用时间戳和随机数
            timestamp = int(time.time() * 1000) % 10000
            random_part = random.randint(1, 999)
            new_number = timestamp + random_part
    else:
        # 从1000开始
        new_number = 1000
    
    # 确保至少4位数
    if new_number < 1000:
        new_number += 1000
        
    return f"{prefix}{new_number}"

def check_and_fix_duplicate_numbers(db: Session):
    """
    检查并修复重复的预约序号
    Check and fix duplicate reservation numbers
    
    Args:
        db: 数据库会话
    """
    try:
        logger.info("开始检查重复的预约序号...")
        
        # 查找所有重复的预约序号
        duplicate_numbers_query = text("""
            SELECT reservation_number, COUNT(*) as count
            FROM reservation
            GROUP BY reservation_number
            HAVING COUNT(*) > 1
        """)
        
        result = db.execute(duplicate_numbers_query)
        duplicate_numbers = [(row[0], row[1]) for row in result]
        
        if not duplicate_numbers:
            logger.info("没有发现重复的预约序号")
            return 0
        
        logger.info(f"发现 {len(duplicate_numbers)} 个重复的预约序号:")
        for number, count in duplicate_numbers:
            logger.info(f"预约序号 {number} 重复 {count} 次")
        
        # 修复重复的预约序号
        fixed_count = 0
        for duplicate_number, _ in duplicate_numbers:
            # 查找使用该序号的所有预约，按ID排序
            reservations = db.query(Reservation).filter(
                Reservation.reservation_number == duplicate_number
            ).order_by(Reservation.id).all()
            
            # 保留第一个预约的序号，为其他预约生成新序号
            for i, reservation in enumerate(reservations):
                if i == 0:
                    logger.info(f"保留预约ID: {reservation.id} 的序号: {duplicate_number}")
                    continue
                
                # 为其他预约生成新序号
                created_at = reservation.created_at or datetime.now()
                new_number = generate_unique_reservation_number(db, created_at)
                
                # 确保新序号不重复
                while db.query(Reservation).filter(Reservation.reservation_number == new_number).first():
                    # 添加随机后缀确保唯一性
                    timestamp = int(time.time() * 1000) % 10000
                    random_part = random.randint(1000, 9999)
                    new_number = f"RN-{created_at.strftime('%Y%m%d')}-{timestamp}-{random_part}"
                
                # 更新预约序号
                old_number = reservation.reservation_number
                reservation.reservation_number = new_number
                logger.info(f"修复预约ID: {reservation.id}, 旧序号: {old_number} -> 新序号: {new_number}")
                fixed_count += 1
        
        # 提交更改
        if fixed_count > 0:
            db.commit()
            logger.info(f"修复完成，共修复 {fixed_count} 个重复的预约序号")
        
        return fixed_count
    
    except Exception as e:
        logger.error(f"检查和修复重复预约序号时出错: {str(e)}")
        db.rollback()
        return 0
