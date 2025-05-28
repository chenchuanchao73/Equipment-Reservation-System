"""
循环预约CRUD操作
Recurring Reservation CRUD operations
"""
import logging
import json
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, date, time, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_

from backend.models.recurring_reservation import RecurringReservation
from backend.models.reservation import Reservation
from backend.models.equipment import Equipment
from backend.schemas.recurring_reservation import RecurringReservationCreate, RecurringReservationUpdate
from backend.utils.code_generator import generate_reservation_code, generate_reservation_number, generate_recurring_reservation_number
from backend.utils.date_utils import combine_date_time, get_weekday, get_next_occurrence_date
from backend.routes.crud.reservation import is_time_available

# 设置日志
logger = logging.getLogger(__name__)

def create_recurring_reservation(db: Session, recurring_reservation: RecurringReservationCreate) -> Tuple[Optional[RecurringReservation], str, List[Reservation]]:
    """
    创建循环预约
    Create recurring reservation
    """
    # 检查设备是否存在
    equipment = db.query(Equipment).filter(Equipment.id == recurring_reservation.equipment_id).first()
    if not equipment:
        return None, "设备不存在", []

    # 检查设备是否可用
    if equipment.status != "available":
        return None, "设备不可用", []

    # 检查日期和时间是否有效
    if recurring_reservation.start_date > recurring_reservation.end_date:
        return None, "开始日期必须早于或等于结束日期", []

    if recurring_reservation.start_time >= recurring_reservation.end_time:
        return None, "开始时间必须早于结束时间", []

    # 根据模式类型验证必要的字段
    if recurring_reservation.pattern_type == "weekly" and (not recurring_reservation.days_of_week or len(recurring_reservation.days_of_week) == 0):
        return None, "每周模式必须指定每周几", []

    if recurring_reservation.pattern_type == "monthly" and (not recurring_reservation.days_of_month or len(recurring_reservation.days_of_month) == 0):
        return None, "每月模式必须指定每月几号", []

    # 生成循环预约码
    reservation_code = generate_reservation_code()
    while db.query(RecurringReservation).filter(RecurringReservation.reservation_code == reservation_code).first() or \
          db.query(Reservation).filter(Reservation.reservation_code == reservation_code).first():
        reservation_code = generate_reservation_code()

    # 创建循环预约记录
    db_recurring_reservation = RecurringReservation(
        equipment_id=recurring_reservation.equipment_id,
        reservation_code=reservation_code,
        pattern_type=recurring_reservation.pattern_type,
        days_of_week=json.dumps(recurring_reservation.days_of_week) if recurring_reservation.days_of_week else None,
        days_of_month=json.dumps(recurring_reservation.days_of_month) if recurring_reservation.days_of_month else None,
        start_date=recurring_reservation.start_date,
        end_date=recurring_reservation.end_date,
        start_time=recurring_reservation.start_time,
        end_time=recurring_reservation.end_time,
        user_name=recurring_reservation.user_name,
        user_department=recurring_reservation.user_department,
        user_contact=recurring_reservation.user_contact,
        user_email=recurring_reservation.user_email,
        purpose=recurring_reservation.purpose,
        status="active"
    )

    db.add(db_recurring_reservation)
    db.commit()
    db.refresh(db_recurring_reservation)

    # 生成所有子预约
    child_reservations = generate_child_reservations(db, db_recurring_reservation)

    # 添加设备信息
    db_recurring_reservation.equipment_name = equipment.name
    db_recurring_reservation.equipment_category = equipment.category
    db_recurring_reservation.equipment_location = equipment.location

    return db_recurring_reservation, "循环预约创建成功", child_reservations

def generate_child_reservations(db: Session, recurring_reservation: RecurringReservation) -> List[Reservation]:
    """
    为循环预约生成子预约
    Generate child reservations for recurring reservation
    """
    try:
        # 解析必要的数据
        equipment_id = recurring_reservation.equipment_id
        pattern_type = recurring_reservation.pattern_type
        start_date = recurring_reservation.start_date
        end_date = recurring_reservation.end_date
        start_time = recurring_reservation.start_time
        end_time = recurring_reservation.end_time

        # 解析days_of_week和days_of_month
        days_of_week = []
        if recurring_reservation.days_of_week:
            try:
                if isinstance(recurring_reservation.days_of_week, str):
                    days_of_week = json.loads(recurring_reservation.days_of_week)
                else:
                    days_of_week = recurring_reservation.days_of_week
            except (json.JSONDecodeError, TypeError):
                logger.error(f"无法解析days_of_week: {recurring_reservation.days_of_week}")

        days_of_month = []
        if recurring_reservation.days_of_month:
            try:
                if isinstance(recurring_reservation.days_of_month, str):
                    days_of_month = json.loads(recurring_reservation.days_of_month)
                else:
                    days_of_month = recurring_reservation.days_of_month
            except (json.JSONDecodeError, TypeError):
                logger.error(f"无法解析days_of_month: {recurring_reservation.days_of_month}")

        # 准备循环生成子预约
        child_reservations = []
        current_date = start_date

        # 冲突信息收集
        conflicts = []
        total_planned = 0
        created_count = 0

        # 添加一个基础编号变量，用于生成关联的预约号
        base_number = None
        # 添加子预约序号计数
        reservation_index = 1

        while current_date <= end_date:
            should_create = False

            if pattern_type == "daily":
                should_create = True
            elif pattern_type == "weekly":
                # 检查当前日期是否是指定的星期几
                weekday = get_weekday(current_date)  # 0-6, 0表示周日
                should_create = weekday in days_of_week
            elif pattern_type == "monthly":
                # 检查当前日期是否是指定的月份日期
                day = current_date.day
                should_create = day in days_of_month
            elif pattern_type == "custom":
                # 自定义模式的处理逻辑
                pass

            if should_create:
                total_planned += 1  # 计划创建的预约总数

                # 创建预约的开始和结束时间
                try:
                    # 直接使用datetime构造函数创建日期时间对象
                    start_time = recurring_reservation.start_time
                    end_time = recurring_reservation.end_time

                    # 创建开始日期时间
                    start_datetime = datetime(
                        year=current_date.year,
                        month=current_date.month,
                        day=current_date.day,
                        hour=start_time.hour,
                        minute=start_time.minute,
                        second=start_time.second
                    )

                    # 创建结束日期时间
                    end_datetime = datetime(
                        year=current_date.year,
                        month=current_date.month,
                        day=current_date.day,
                        hour=end_time.hour,
                        minute=end_time.minute,
                        second=end_time.second
                    )

                    # 打印调试信息
                    print(f"成功创建日期时间 - 开始: {start_datetime}, 结束: {end_datetime}")

                except Exception as e:
                    print(f"创建日期时间对象失败: {e}")
                    conflicts.append(current_date.strftime('%Y-%m-%d'))  # 记录失败的日期
                    current_date += timedelta(days=1)  # 增加一天
                    continue

                # 检查该时间段是否可用
                reservation_date = current_date.strftime('%Y-%m-%d')
                is_available = is_time_available(db, equipment_id, start_datetime, end_datetime)

                if not is_available:
                    print(f"日期 {reservation_date} 的时间段不可用")
                    conflicts.append(reservation_date)  # 记录冲突的日期
                    current_date += timedelta(days=1)  # 增加一天
                    continue

                # 创建预约 - 使用父循环预约的预约码，而不是生成新的
                reservation_code = recurring_reservation.reservation_code  # 直接使用父循环预约的预约码

                # 生成预约序号 - 使用循环预约专用的序号生成函数
                reservation_number, base_number = generate_recurring_reservation_number(
                    current_date,
                    reservation_index,
                    base_number,
                    db  # 传入数据库会话，用于检查编号唯一性
                )

                # 递增子预约序号
                reservation_index += 1

                # 创建子预约
                child_reservation = Reservation(
                    recurring_reservation_id=recurring_reservation.id,
                    equipment_id=equipment_id,
                    reservation_code=reservation_code,
                    reservation_number=reservation_number,
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    user_name=recurring_reservation.user_name,
                    user_department=recurring_reservation.user_department,
                    user_contact=recurring_reservation.user_contact,
                    user_email=recurring_reservation.user_email,
                    purpose=recurring_reservation.purpose,
                    status='confirmed',
                    is_exception=0
                )

                db.add(child_reservation)
                child_reservations.append(child_reservation)
                created_count += 1  # 实际创建的预约数

            current_date += timedelta(days=1)  # 增加一天

        # 记录冲突信息
        if conflicts:
            recurring_reservation.conflicts = ','.join(conflicts)

        # 更新总计划数和实际创建数
        recurring_reservation.total_planned = total_planned
        recurring_reservation.created_count = created_count

        # 提交更改
        db.commit()

        return child_reservations

    except Exception as e:
        db.rollback()
        logger.error(f"生成子预约失败: {str(e)}")
        raise

def get_recurring_reservation(db: Session, recurring_reservation_id: int) -> Optional[RecurringReservation]:
    """
    获取循环预约
    Get recurring reservation
    """
    return db.query(RecurringReservation).filter(RecurringReservation.id == recurring_reservation_id).first()

def get_recurring_reservations(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    equipment_id: Optional[int] = None,
    user_name: Optional[str] = None,
    user_contact: Optional[str] = None,
    status: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None
) -> List[RecurringReservation]:
    """
    获取循环预约列表
    Get recurring reservations
    """
    query = db.query(RecurringReservation)

    # 应用筛选条件
    if equipment_id:
        query = query.filter(RecurringReservation.equipment_id == equipment_id)
    if user_name:
        query = query.filter(RecurringReservation.user_name.like(f"%{user_name}%"))
    if user_contact:
        query = query.filter(RecurringReservation.user_contact == user_contact)
    if status:
        query = query.filter(RecurringReservation.status == status)
    if from_date:
        query = query.filter(RecurringReservation.end_date >= from_date)
    if to_date:
        query = query.filter(RecurringReservation.start_date <= to_date)

    # 分页
    return query.order_by(RecurringReservation.created_at.desc()).offset(skip).limit(limit).all()

def get_recurring_reservation_count(
    db: Session,
    equipment_id: Optional[int] = None,
    user_name: Optional[str] = None,
    user_contact: Optional[str] = None,
    status: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None
) -> int:
    """
    获取循环预约数量
    Get recurring reservation count
    """
    query = db.query(func.count(RecurringReservation.id))

    # 应用筛选条件
    if equipment_id:
        query = query.filter(RecurringReservation.equipment_id == equipment_id)
    if user_name:
        query = query.filter(RecurringReservation.user_name.like(f"%{user_name}%"))
    if user_contact:
        query = query.filter(RecurringReservation.user_contact == user_contact)
    if status:
        query = query.filter(RecurringReservation.status == status)
    if from_date:
        query = query.filter(RecurringReservation.end_date >= from_date)
    if to_date:
        query = query.filter(RecurringReservation.start_date <= to_date)

    return query.scalar()

def update_recurring_reservation(
    db: Session,
    recurring_reservation_id: int,
    recurring_reservation_update: RecurringReservationUpdate,
    update_future_only: int = 1
) -> Tuple[Optional[RecurringReservation], str]:
    """
    更新循环预约
    Update recurring reservation
    """
    # 获取原循环预约信息
    db_recurring_reservation = db.query(RecurringReservation).filter(RecurringReservation.id == recurring_reservation_id).first()
    if not db_recurring_reservation:
        return None, "循环预约不存在"

    # 检查循环预约是否已取消
    if db_recurring_reservation.status == "cancelled":
        return None, "循环预约已取消，无法修改"

    # 准备更新数据
    update_data = recurring_reservation_update.dict(exclude_unset=True)

    # 如果更新了模式类型，检查必要的字段
    if "pattern_type" in update_data:
        pattern_type = update_data["pattern_type"]
        days_of_week = update_data.get("days_of_week", json.loads(db_recurring_reservation.days_of_week) if db_recurring_reservation.days_of_week else [])
        days_of_month = update_data.get("days_of_month", json.loads(db_recurring_reservation.days_of_month) if db_recurring_reservation.days_of_month else [])

        if pattern_type == "weekly" and (not days_of_week or len(days_of_week) == 0):
            return None, "每周模式必须指定每周几"

        if pattern_type == "monthly" and (not days_of_month or len(days_of_month) == 0):
            return None, "每月模式必须指定每月几号"

    # 如果更新了日期或时间，检查是否有效
    start_date = update_data.get("start_date", db_recurring_reservation.start_date)
    end_date = update_data.get("end_date", db_recurring_reservation.end_date)
    start_time = update_data.get("start_time", db_recurring_reservation.start_time)
    end_time = update_data.get("end_time", db_recurring_reservation.end_time)

    if start_date > end_date:
        return None, "开始日期必须早于或等于结束日期"

    if start_time >= end_time:
        return None, "开始时间必须早于结束时间"

    # 处理JSON字段
    if "days_of_week" in update_data:
        update_data["days_of_week"] = json.dumps(update_data["days_of_week"]) if update_data["days_of_week"] else None

    if "days_of_month" in update_data:
        update_data["days_of_month"] = json.dumps(update_data["days_of_month"]) if update_data["days_of_month"] else None

    # 更新循环预约
    for key, value in update_data.items():
        setattr(db_recurring_reservation, key, value)

    # 处理子预约
    today = datetime.now().date()

    # 获取所有子预约
    child_reservations = db.query(Reservation).filter(
        Reservation.recurring_reservation_id == recurring_reservation_id,
        Reservation.status == "confirmed"
    )

    if update_future_only == 1:
        # 只更新今天及以后的预约
        child_reservations = child_reservations.filter(func.date(Reservation.start_datetime) >= today)

    # 删除现有子预约
    for reservation in child_reservations.all():
        db.delete(reservation)

    db.commit()
    db.refresh(db_recurring_reservation)

    # 重新生成子预约
    generate_child_reservations(db, db_recurring_reservation)

    return db_recurring_reservation, "循环预约已更新"

def cancel_recurring_reservation(
    db: Session,
    recurring_reservation_id: int,
    cancel_future_only: int = 0
) -> Tuple[bool, str]:
    """
    取消循环预约
    Cancel recurring reservation

    Args:
        db: 数据库会话
        recurring_reservation_id: 循环预约ID
        cancel_future_only: 是否只取消未来预约，默认为0（取消所有已确认状态的预约）
    """
    # 获取循环预约
    db_recurring_reservation = db.query(RecurringReservation).filter(RecurringReservation.id == recurring_reservation_id).first()
    if not db_recurring_reservation:
        return False, "循环预约不存在"

    # 检查循环预约是否已取消
    if db_recurring_reservation.status == "cancelled":
        return False, "循环预约已取消"

    # 更新循环预约状态
    db_recurring_reservation.status = "cancelled"

    # 获取所有状态为"已确认"的子预约
    child_reservations = db.query(Reservation).filter(
        Reservation.recurring_reservation_id == recurring_reservation_id,
        Reservation.status == "confirmed"
    )

    # 取消子预约
    for reservation in child_reservations.all():
        reservation.status = "cancelled"

    db.commit()

    return True, "循环预约已取消"

def get_child_reservations(
    db: Session,
    recurring_reservation_id: int,
    include_past: int = 0
) -> List[Reservation]:
    """
    获取循环预约的子预约
    Get child reservations of recurring reservation

    Args:
        include_past: 0表示不包含过去的预约，1表示包含
    """
    query = db.query(Reservation).filter(Reservation.recurring_reservation_id == recurring_reservation_id)

    if include_past == 0:
        # 只获取今天及以后的预约
        today = datetime.now().date()
        query = query.filter(func.date(Reservation.start_datetime) >= today)

    return query.order_by(Reservation.start_datetime).all()
