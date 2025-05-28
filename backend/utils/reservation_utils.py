"""
预约工具函数
Reservation utilities
"""
import os
import logging
import asyncio
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime

# 导入配置
from config import BASE_DIR
from backend.database import get_db
from backend.utils.email_sender import send_reservation_confirmation

# 设置日志
logger = logging.getLogger(__name__)

def update_ics_for_reservation(db: Session, reservation) -> None:
    """
    为预约更新ICS文件
    Update ICS file for reservation
    """
    try:
        # 实现ICS文件生成的逻辑
        # 但由于这是一个模拟功能，所以只记录日志
        logger.info(f"更新ICS文件: 预约ID={reservation.id}")
    except Exception as e:
        logger.error(f"更新ICS文件失败: {str(e)}")

def generate_qrcode_for_reservation(reservation) -> None:
    """
    为预约生成二维码 (空实现)
    Generate QR code for reservation (empty implementation)
    """
    # 此功能已禁用，仅保留函数接口
    logger.info(f"二维码生成功能已禁用: 预约ID={reservation.id}")

def check_reservation_calendar_sync_enabled() -> bool:
    """
    检查是否启用了预约日历同步
    Check if reservation calendar sync is enabled
    """
    # 由于这是一个模拟功能，默认返回False
    return False

def add_reservation_to_calendar(reservation) -> None:
    """
    将预约添加到日历
    Add reservation to calendar
    """
    try:
        # 实现日历同步的逻辑
        # 但由于这是一个模拟功能，所以只记录日志
        logger.info(f"添加预约到日历: 预约ID={reservation.id}")
    except Exception as e:
        logger.error(f"添加预约到日历失败: {str(e)}")

def remove_reservation_from_calendar(reservation) -> None:
    """
    从日历中移除预约
    Remove reservation from calendar
    """
    try:
        # 实现日历同步的逻辑
        # 但由于这是一个模拟功能，所以只记录日志
        logger.info(f"从日历中移除预约: 预约ID={reservation.id}")
    except Exception as e:
        logger.error(f"从日历中移除预约失败: {str(e)}")

def send_reservation_confirmation_email(reservation) -> None:
    """
    发送预约确认邮件
    Send reservation confirmation email
    """
    try:
        # 记录要发送邮件的日志
        logger.info(f"发送预约确认邮件: 预约ID={reservation.id}, 邮箱={reservation.user_email}")
        
        # 如果没有邮箱，就不发送
        if not reservation.user_email:
            logger.warning(f"预约ID={reservation.id}没有提供邮箱，无法发送确认邮件")
            return
        
        # 获取数据库会话
        db = next(get_db())
        
        # 准备邮件数据
        reservation_data = {
            "reservation_code": reservation.reservation_code,
            "reservation_number": reservation.reservation_number,
            "user_name": reservation.user_name,
            "equipment_name": reservation.equipment.name if hasattr(reservation, 'equipment') and reservation.equipment else "",
            "equipment_category": reservation.equipment.category if hasattr(reservation, 'equipment') and reservation.equipment else "",
            "location": reservation.equipment.location if hasattr(reservation, 'equipment') and reservation.equipment else "",
            "start_datetime": reservation.start_datetime.strftime("%Y-%m-%d %H:%M") if reservation.start_datetime else "",
            "end_datetime": reservation.end_datetime.strftime("%Y-%m-%d %H:%M") if reservation.end_datetime else "",
            "purpose": reservation.purpose or "",
            "description": reservation.equipment.description if hasattr(reservation, 'equipment') and reservation.equipment else "",
            "site_url": "http://localhost:8000",  # 应该从配置中获取
            "status": "已确认 / Confirmed"
        }
        
        # 创建异步事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # 调用真正的邮件发送函数
        result = loop.run_until_complete(
            send_reservation_confirmation(
                to_email=reservation.user_email,
                reservation_data=reservation_data,
                lang="zh_CN",  # 默认使用中文，也可以从reservation获取
                db=db
            )
        )
        
        # 关闭事件循环
        loop.close()
        
        if result:
            logger.info(f"预约确认邮件发送成功: 预约ID={reservation.id}, 邮箱={reservation.user_email}")
        else:
            logger.error(f"预约确认邮件发送失败: 预约ID={reservation.id}, 邮箱={reservation.user_email}")
            
    except Exception as e:
        logger.error(f"发送预约确认邮件失败: {str(e)}")

def send_reservation_cancel_email(reservation) -> None:
    """
    发送预约取消邮件
    Send reservation cancellation email
    """
    try:
        # 实现邮件发送的逻辑
        # 但由于这是一个模拟功能，所以只记录日志
        logger.info(f"发送预约取消邮件: 预约ID={reservation.id}, 邮箱={reservation.user_email}")
    except Exception as e:
        logger.error(f"发送预约取消邮件失败: {str(e)}") 