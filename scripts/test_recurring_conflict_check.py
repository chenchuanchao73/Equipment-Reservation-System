#!/usr/bin/env python
"""
测试循环预约冲突检查功能
Test the conflict checking feature for recurring reservations
"""
import sys
import os
from pathlib import Path
from datetime import datetime, date, time, timedelta
import json

# 获取项目根目录
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy.orm import Session
from backend.database import engine, get_db, SessionLocal
from backend.models.recurring_reservation import RecurringReservation
from backend.models.reservation import Reservation
from backend.models.equipment import Equipment
from backend.routes.crud.recurring_reservation import create_recurring_reservation, generate_child_reservations
from backend.schemas.recurring_reservation import RecurringReservationCreate

def create_test_single_reservation(db: Session, equipment_id: int, start_datetime: datetime, end_datetime: datetime):
    """创建测试用的单次预约"""
    from backend.routes.crud.reservation import create_reservation
    from backend.schemas.reservation import ReservationCreate
    
    reservation_data = ReservationCreate(
        equipment_id=equipment_id,
        user_name="测试用户",
        user_department="测试部门",
        user_contact="12345678901",
        user_email="test@example.com",
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        purpose="测试预约",
        skip_email=True  # 跳过发送邮件
    )
    
    db_reservation, message = create_reservation(db, reservation_data)
    
    if db_reservation:
        print(f"创建测试预约成功: ID={db_reservation.id}, 预约编号={db_reservation.reservation_number}")
        return db_reservation
    else:
        print(f"创建测试预约失败: {message}")
        return None

def create_test_recurring_reservation(db: Session, equipment_id: int, has_conflict: bool = True):
    """创建测试用的循环预约"""
    # 首先获取一个设备
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    
    if not equipment:
        print(f"设备ID={equipment_id}不存在")
        return None
    
    print(f"使用设备: ID={equipment.id}, 名称={equipment.name}, 允许同时预约={equipment.allow_simultaneous}")
    
    # 当前日期
    today = date.today()
    
    # 如果要测试冲突，先创建一个单次预约
    if has_conflict:
        # 创建明天10:00-12:00的预约
        tomorrow = today + timedelta(days=1)
        start_dt = datetime.combine(tomorrow, time(10, 0))
        end_dt = datetime.combine(tomorrow, time(12, 0))
        
        print(f"创建单次预约用于测试冲突: {start_dt} - {end_dt}")
        create_test_single_reservation(db, equipment_id, start_dt, end_dt)
    
    # 创建循环预约数据
    recurring_data = RecurringReservationCreate(
        equipment_id=equipment_id,
        pattern_type="daily",  # 每天
        days_of_week=[],  # 不需要指定
        days_of_month=[],  # 不需要指定
        start_date=today,  # 从今天开始
        end_date=today + timedelta(days=5),  # 持续5天
        start_time=time(10, 0),  # 每天10:00开始
        end_time=time(12, 0),  # 每天12:00结束
        user_name="循环测试用户",
        user_department="测试部门",
        user_contact="12345678901",
        user_email="",  # 空邮箱，跳过发送邮件
        purpose="测试循环预约冲突检查",
        lang="zh_CN"
    )
    
    # 创建循环预约
    print("创建循环预约...")
    db_recurring, message, child_reservations = create_recurring_reservation(db, recurring_data)
    
    if db_recurring:
        print(f"创建循环预约成功: ID={db_recurring.id}, 预约码={db_recurring.reservation_code}")
        print(f"子预约数量: {len(child_reservations)}")
        
        # 检查冲突信息
        if hasattr(db_recurring, 'total_planned') and db_recurring.total_planned:
            print(f"计划创建的预约数: {db_recurring.total_planned}")
            print(f"成功创建的预约数: {len(child_reservations)}")
            skipped = db_recurring.total_planned - len(child_reservations)
            print(f"跳过的冲突预约数: {skipped}")
            
            if hasattr(db_recurring, 'conflicts') and db_recurring.conflicts:
                print(f"冲突日期: {db_recurring.conflicts}")
        
        # 显示所有子预约的日期和时间
        print("\n创建的子预约:")
        for i, res in enumerate(child_reservations, 1):
            print(f"{i}. ID={res.id}, 预约号={res.reservation_number}, 时间={res.start_datetime} - {res.end_datetime}")
            
        return db_recurring
    else:
        print(f"创建循环预约失败: {message}")
        return None

def test_conflict_checking():
    """测试循环预约冲突检查功能"""
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 获取一个可用的设备
        equipment = db.query(Equipment).filter(Equipment.status == "available").first()
        
        if not equipment:
            print("找不到可用的设备")
            return
        
        print("===== 测试1: 创建有冲突的循环预约 =====")
        recurring1 = create_test_recurring_reservation(db, equipment.id, has_conflict=True)
        
        print("\n===== 测试2: 创建另一个循环预约（与第一个冲突） =====")
        recurring2 = create_test_recurring_reservation(db, equipment.id, has_conflict=False)
        
        print("\n测试完成！")
        
    finally:
        db.close()

if __name__ == "__main__":
    # 执行测试
    test_conflict_checking() 