"""
预定CRUD操作
Reservation CRUD operations
"""
import logging
import traceback
from typing import List, Optional, Tuple, Dict, Any, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_

from backend.models.equipment import Equipment
from backend.models.equipment_time_slot import EquipmentTimeSlot
from backend.models.reservation import Reservation
from backend.models.reservation_history import ReservationHistory
from backend.schemas.reservation import ReservationCreate, ReservationUpdate
from backend.schemas.reservation_history import ReservationHistoryCreate
from backend.utils.code_generator import generate_reservation_code, generate_reservation_number
from backend.utils.date_utils import parse_datetime, format_datetime
from backend.routes.crud.time_slot import decrement_time_slot_count
from backend.utils.reservation_utils import (
    update_ics_for_reservation,
    generate_qrcode_for_reservation,
    check_reservation_calendar_sync_enabled,
    add_reservation_to_calendar,
    send_reservation_confirmation_email,
    send_reservation_cancel_email
)

# 设置日志
logger = logging.getLogger(__name__)

def create_reservation(db: Session, reservation: ReservationCreate) -> Tuple[Optional[Reservation], str]:
    """
    创建预定
    Create reservation
    """
    # 检查设备是否存在
    equipment = db.query(Equipment).filter(Equipment.id == reservation.equipment_id).first()
    if not equipment:
        return None, "设备不存在"

    # 检查设备是否可用
    if equipment.status != "available":
        return None, "设备不可用"

    # 检查时间是否有效
    if reservation.start_datetime >= reservation.end_datetime:
        return None, "开始时间必须早于结束时间"

    # 添加调试日志 - 显示设备是否允许同时预约
    print(f"[调试信息] 设备ID: {equipment.id}, 名称: {equipment.name}, 允许同时预约: {equipment.allow_simultaneous}, 最大同时预约数: {equipment.max_simultaneous}")

    try:
        # 使用悲观锁锁定设备记录，防止并发问题
        # 使用with_for_update锁定equipment表中的记录，直到事务结束
        locked_equipment = db.query(Equipment).filter(
            Equipment.id == reservation.equipment_id
        ).with_for_update().first()

        if not locked_equipment:
            return None, "设备不存在或已被锁定"

        # 使用时间段管理功能检查可用性
        from backend.routes.crud.time_slot import check_time_slot_availability, create_time_slot, increment_time_slot_count

        is_available, error_message, containing_slot = check_time_slot_availability(
            db,
            reservation.equipment_id,
            reservation.start_datetime,
            reservation.end_datetime
        )

        if not is_available:
            return None, error_message

        # 生成预约码
        reservation_code = generate_reservation_code()

        # 生成预约编号
        reservation_number = generate_reservation_number(db)

        # 创建预约记录
        db_reservation = Reservation(
            reservation_number=reservation_number,
            equipment_id=reservation.equipment_id,
            reservation_code=reservation_code,
            user_name=reservation.user_name,
            user_department=reservation.user_department,
            user_contact=reservation.user_contact,
            user_email=reservation.user_email,
            start_datetime=reservation.start_datetime,
            end_datetime=reservation.end_datetime,
            purpose=reservation.purpose,
            status="confirmed"
        )

        # 处理时间段关联
        if locked_equipment.allow_simultaneous:
            if containing_slot:
                # 如果找到包含的时间段，增加其计数并关联
                current_count_before = containing_slot.current_count
                db_reservation.time_slot_id = containing_slot.id
                increment_time_slot_count(db, containing_slot.id)
                # 获取更新后的时间段信息
                updated_slot = db.query(EquipmentTimeSlot).filter(EquipmentTimeSlot.id == containing_slot.id).first()
                print(f"[调试信息] 使用现有时间段 - 设备ID: {equipment.id}, 时间段ID: {containing_slot.id}")
                print(f"[调试信息] 同时预约计数: {current_count_before} -> {updated_slot.current_count}/{equipment.max_simultaneous}")
                print(f"[调试信息] 这是该时间段内的第 {updated_slot.current_count} 个预约 (最大允许: {equipment.max_simultaneous})")
            else:
                # 如果没有找到包含的时间段，创建新的时间段并关联
                new_slot = create_time_slot(
                    db,
                    reservation.equipment_id,
                    reservation.start_datetime,
                    reservation.end_datetime
                )
                db_reservation.time_slot_id = new_slot.id
                print(f"[调试信息] 创建新时间段 - 设备ID: {equipment.id}, 时间段ID: {new_slot.id}")
                print(f"[调试信息] 同时预约计数: 1/{equipment.max_simultaneous}")
                print(f"[调试信息] 这是该时间段内的第 1 个预约 (最大允许: {equipment.max_simultaneous})")

        db.add(db_reservation)
        db.commit()
        db.refresh(db_reservation)

        # 更新ics文件
        update_ics_for_reservation(db, db_reservation)

        # 生成二维码
        generate_qrcode_for_reservation(db_reservation)

        # 同步谷歌日历（如果启用）
        if check_reservation_calendar_sync_enabled():
            add_reservation_to_calendar(db_reservation)

        # 发送确认邮件
        if not reservation.skip_email:
            send_reservation_confirmation_email(db_reservation)

        return db_reservation, ""
    except Exception as e:
        db.rollback()
        print(f"创建预约失败: {str(e)}")
        return None, f"创建预约失败: {str(e)}"

def get_reservation_by_id(db: Session, reservation_id: int) -> Optional[Reservation]:
    """
    通过ID获取预定
    Get reservation by ID
    """
    return db.query(Reservation).filter(Reservation.id == reservation_id).first()

def get_reservation_by_code(db: Session, reservation_code: str, reservation_number: Optional[str] = None) -> Optional[Reservation]:
    """
    通过预定码或预约序号获取预定
    Get reservation by code or reservation number

    Args:
        db: 数据库会话
        reservation_code: 预约码
        reservation_number: 预约序号，如果提供，则只获取指定预约序号的预约

    Returns:
        Reservation对象，如果找到预约
        None，如果未找到预约

    Note:
        如果预约码属于循环预约，会在Reservation对象上添加is_recurring=True和recurring_id属性
    """
    try:
        # 记录查询参数
        logger.info(f"[数据库查询] 获取预约: 预约码={reservation_code}, 预约序号={reservation_number}")

        # 首先检查这个预约码是否属于循环预约
        # 导入RecurringReservation模型
        from backend.models.recurring_reservation import RecurringReservation

        # 查询循环预约表
        recurring_reservation = db.query(RecurringReservation).filter(
            RecurringReservation.reservation_code == reservation_code
        ).first()

        if recurring_reservation:
            logger.info(f"[数据库查询] 预约码 {reservation_code} 属于循环预约，ID={recurring_reservation.id}")

            # 如果提供了预约序号，则查询特定的子预约
            if reservation_number:
                logger.info(f"[数据库查询] 提供了预约序号 {reservation_number}，查询特定子预约")
                reservation = db.query(Reservation).filter(
                    Reservation.reservation_code == reservation_code,
                    Reservation.reservation_number == reservation_number
                ).first()

                if reservation:
                    # 标记这是循环预约的子预约
                    reservation.is_recurring = True
                    reservation.recurring_id = recurring_reservation.id

                    # 添加设备信息
                    equipment = db.query(Equipment).filter(Equipment.id == reservation.equipment_id).first()
                    if equipment:
                        reservation.equipment_name = equipment.name
                        reservation.equipment_category = equipment.category
                        reservation.equipment_location = equipment.location

                    return reservation

            # 创建一个特殊的Reservation对象，标记这是循环预约
            # 这将告诉前端这是一个循环预约，应该跳转到循环预约详情页面
            dummy_reservation = Reservation()
            dummy_reservation.is_recurring = True
            dummy_reservation.recurring_id = recurring_reservation.id
            dummy_reservation.reservation_code = reservation_code

            logger.info(f"[数据库查询] 返回标记为循环预约的对象，循环预约ID={recurring_reservation.id}")
            return dummy_reservation

        # 首先检查reservation_code是否是预约序号格式（以RN-开头）
        if reservation_code.startswith("RN-"):
            logger.info(f"[数据库查询] 检测到预约序号格式: {reservation_code}")
            # 直接通过预约序号查询
            reservation = db.query(Reservation).filter(
                Reservation.reservation_number == reservation_code
            ).first()

            if reservation:
                logger.info(f"[数据库查询] 通过预约序号直接找到预约: ID={reservation.id}, 状态={reservation.status}")
                # 添加设备信息
                equipment = db.query(Equipment).filter(Equipment.id == reservation.equipment_id).first()
                if equipment:
                    reservation.equipment_name = equipment.name
                    reservation.equipment_category = equipment.category
                    reservation.equipment_location = equipment.location
                return reservation
            else:
                logger.warning(f"[数据库查询] 通过预约序号直接查询未找到预约: {reservation_code}")

        # 如果提供了预约序号，则优先使用预约序号查询
        if reservation_number:
            logger.info(f"[数据库查询] 使用预约序号查询: {reservation_number}")
            reservation = db.query(Reservation).filter(
                Reservation.reservation_code == reservation_code,
                Reservation.reservation_number == reservation_number
            ).first()

            if reservation:
                logger.info(f"[数据库查询] 通过预约序号找到预约: ID={reservation.id}, 状态={reservation.status}")
                # 添加设备信息
                equipment = db.query(Equipment).filter(Equipment.id == reservation.equipment_id).first()
                if equipment:
                    reservation.equipment_name = equipment.name
                    reservation.equipment_category = equipment.category
                    reservation.equipment_location = equipment.location
                return reservation
            else:
                logger.warning(f"[数据库查询] 通过预约序号未找到预约: 预约码={reservation_code}, 预约序号={reservation_number}")

        # 如果没有提供预约序号或通过预约序号未找到，则尝试通过预约码查询
        logger.info(f"[数据库查询] 使用预约码查询: {reservation_code}")

        # 先尝试通过预约序号查询
        reservation = db.query(Reservation).filter(Reservation.reservation_number == reservation_code).first()
        if reservation:
            logger.info(f"[数据库查询] 通过预约序号直接找到预约: ID={reservation.id}, 状态={reservation.status}, 预约序号={reservation.reservation_number}")
            return reservation

        # 如果通过预约序号未找到，再尝试通过预约码查询
        # 查询具有相同预约码的所有预约，按开始时间排序
        reservations = db.query(Reservation).filter(
            Reservation.reservation_code == reservation_code
        ).order_by(Reservation.start_datetime).all()

        if reservations:
            logger.info(f"[数据库查询] 找到具有相同预约码的预约数量: {len(reservations)}")

            # 记录所有找到的预约，帮助调试
            for r in reservations:
                logger.debug(f"[数据库查询] 预约详情: ID={r.id}, 状态={r.status}, 预约序号={r.reservation_number}, 开始时间={r.start_datetime}")

            # 查找状态为confirmed的预约
            confirmed_reservations = [r for r in reservations if r.status == "confirmed"]
            if confirmed_reservations:
                logger.info(f"[数据库查询] 找到已确认的预约: ID={confirmed_reservations[0].id}, 预约序号={confirmed_reservations[0].reservation_number}")
                reservation = confirmed_reservations[0]
            else:
                # 如果没有confirmed状态的预约，则返回第一个预约
                logger.info(f"[数据库查询] 未找到已确认的预约，返回第一个预约: ID={reservations[0].id}, 预约序号={reservations[0].reservation_number}")
                reservation = reservations[0]

        # 记录查询结果
        if reservation:
            logger.info(f"[数据库查询] 找到预约: 预约码/序号={reservation_code}, 状态={reservation.status}, ID={reservation.id}")
        else:
            logger.warning(f"[数据库查询] 未找到预约: 预约码/序号={reservation_code}")

            # 尝试查询是否有相同预约码但不同时间段的预约（循环预约的子预约）
            similar_reservations = db.query(Reservation).filter(
                or_(
                    Reservation.reservation_code == reservation_code,
                    Reservation.reservation_number == reservation_code
                )
            ).all()

            if similar_reservations:
                logger.info(f"[数据库查询] 找到相似预约数量: {len(similar_reservations)}")
                for r in similar_reservations:
                    logger.info(f"[数据库查询] 相似预约: ID={r.id}, 状态={r.status}, 开始时间={r.start_datetime}, 结束时间={r.end_datetime}")

            # 如果URL中包含时间参数，尝试使用预约码和时间段查询
            # 这种情况通常出现在循环预约的子预约中
            return None

        # 添加设备信息
        if reservation:
            equipment = db.query(Equipment).filter(Equipment.id == reservation.equipment_id).first()
            if equipment:
                reservation.equipment_name = equipment.name
                reservation.equipment_category = equipment.category
                reservation.equipment_location = equipment.location

        return reservation
    except Exception as e:
        logger.error(f"[数据库错误] 获取预约出错: 预约码/序号={reservation_code}, 错误={str(e)}")
        logger.error(f"[数据库错误] 错误详情: {traceback.format_exc()}")
        return None

def get_reservations(
    db: Session,
    equipment_id: Optional[int] = None,
    user_name: Optional[str] = None,
    user_contact: Optional[str] = None,
    status: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    category: Optional[str] = None,
    reservation_code: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = None
) -> List[Reservation]:
    """
    获取预定列表
    Get reservation list

    Args:
        db: 数据库会话
        equipment_id: 设备ID
        user_name: 用户姓名
        user_contact: 联系方式
        status: 状态
        from_date: 开始日期
        to_date: 结束日期
        category: 设备类别
        reservation_code: 预约码
        skip: 跳过记录数
        limit: 返回记录数
        sort_by: 排序字段，如'id', 'start_datetime', 'created_at'等
        sort_order: 排序方式，'asc'升序，'desc'降序
    """
    query = db.query(Reservation)

    # 应用过滤条件
    if equipment_id:
        query = query.filter(Reservation.equipment_id == equipment_id)
    if user_name:
        query = query.filter(Reservation.user_name.ilike(f"%{user_name}%"))
    if user_contact:
        query = query.filter(Reservation.user_contact == user_contact)
    if status:
        query = query.filter(Reservation.status == status)
    if from_date:
        query = query.filter(Reservation.start_datetime >= from_date)
    if to_date:
        query = query.filter(Reservation.end_datetime <= to_date)
    if reservation_code:
        query = query.filter(Reservation.reservation_code == reservation_code)

    # 如果指定了类别，需要联表查询
    if category:
        query = query.join(Equipment, Reservation.equipment_id == Equipment.id)
        query = query.filter(Equipment.category == category)

    # 应用排序
    if sort_by and hasattr(Reservation, sort_by):
        # 获取排序字段
        sort_field = getattr(Reservation, sort_by)

        # 应用排序方向
        if sort_order and sort_order.lower() == 'asc':
            query = query.order_by(sort_field.asc())
        else:
            query = query.order_by(sort_field.desc())
    else:
        # 默认排序
        query = query.order_by(Reservation.start_datetime.desc())

    # 应用分页
    reservations = query.offset(skip).limit(limit).all()

    # 添加设备信息
    for reservation in reservations:
        equipment = db.query(Equipment).filter(Equipment.id == reservation.equipment_id).first()
        if equipment:
            reservation.equipment_name = equipment.name
            reservation.equipment_category = equipment.category
            reservation.equipment_location = equipment.location

        # 确保预约序号字段存在
        # 如果数据库中没有预约序号（旧数据），则生成一个临时序号
        if not hasattr(reservation, 'reservation_number') or not reservation.reservation_number:
            logger.warning(f"预约 ID={reservation.id} 缺少预约序号，生成临时序号")
            from backend.utils.code_generator import generate_reservation_number
            temp_number = generate_reservation_number()
            reservation.reservation_number = temp_number
            # 保存到数据库
            try:
                db.commit()
            except Exception as e:
                logger.error(f"更新预约序号失败: {str(e)}")
                db.rollback()
        else:
            logger.debug(f"预约 ID={reservation.id} 的预约序号: {reservation.reservation_number}")

    return reservations

def get_reservation_count(
    db: Session,
    equipment_id: Optional[int] = None,
    user_name: Optional[str] = None,
    user_contact: Optional[str] = None,
    status: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    category: Optional[str] = None,
    reservation_code: Optional[str] = None
) -> int:
    """
    获取预定数量
    Get reservation count
    """
    query = db.query(func.count(Reservation.id))

    # 应用过滤条件
    if equipment_id:
        query = query.filter(Reservation.equipment_id == equipment_id)
    if user_name:
        query = query.filter(Reservation.user_name.ilike(f"%{user_name}%"))
    if user_contact:
        query = query.filter(Reservation.user_contact == user_contact)
    if status:
        query = query.filter(Reservation.status == status)
    if from_date:
        query = query.filter(Reservation.start_datetime >= from_date)
    if to_date:
        query = query.filter(Reservation.end_datetime <= to_date)
    if reservation_code:
        query = query.filter(Reservation.reservation_code == reservation_code)

    # 如果指定了类别，需要联表查询
    if category:
        query = query.join(Equipment, Reservation.equipment_id == Equipment.id)
        query = query.filter(Equipment.category == category)

    return query.scalar()

def get_equipment_reservations(
    db: Session,
    equipment_id: int,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    status: Union[str, List[str]] = "confirmed"
) -> List[Reservation]:
    """
    获取设备预定列表
    Get equipment reservations
    """
    query = db.query(Reservation).filter(
        Reservation.equipment_id == equipment_id
    )

    # 处理状态参数，可以是单个字符串或字符串列表
    if isinstance(status, list):
        query = query.filter(Reservation.status.in_(status))
    else:
        query = query.filter(Reservation.status == status)

    if from_date:
        query = query.filter(Reservation.end_datetime >= from_date)
    if to_date:
        query = query.filter(Reservation.start_datetime <= to_date)

    return query.order_by(Reservation.start_datetime).all()

def get_conflicting_reservations(
    db: Session,
    equipment_id: int,
    start_datetime: datetime,
    end_datetime: datetime,
    exclude_reservation_id: Optional[int] = None
) -> List[Dict]:
    """
    获取与指定时间段冲突的预定信息
    Get reservations that conflict with the specified time range
    """
    # 获取设备信息
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        return []

    # 构建查询条件
    query = db.query(Reservation).filter(
        Reservation.equipment_id == equipment_id,
        Reservation.status.in_(["confirmed", "in_use"]),
        # 时间重叠条件
        or_(
            # 情况1：已有预约的结束时间在新预约的开始时间之后（部分重叠）
            and_(
                Reservation.start_datetime <= start_datetime,
                Reservation.end_datetime > start_datetime
            ),
            # 情况2：已有预约的开始时间在新预约的结束时间之前（部分重叠）
            and_(
                Reservation.start_datetime < end_datetime,
                Reservation.end_datetime >= end_datetime
            ),
            # 情况3：已有预约完全包含在新预约内（完全重叠）
            and_(
                Reservation.start_datetime >= start_datetime,
                Reservation.end_datetime <= end_datetime
            ),
            # 情况4：新预约完全包含在已有预约内（完全重叠）
            and_(
                Reservation.start_datetime <= start_datetime,
                Reservation.end_datetime >= end_datetime
            )
        )
    )

    # 排除指定的预约ID（用于修改预约时排除自己）
    if exclude_reservation_id:
        query = query.filter(Reservation.id != exclude_reservation_id)

    # 获取冲突的预约
    conflicting_reservations = query.all()

    # 转换为字典格式
    conflicts = []
    for reservation in conflicting_reservations:
        conflicts.append({
            "id": reservation.id,
            "start_datetime": reservation.start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "end_datetime": reservation.end_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "user_name": reservation.user_name,
            "user_department": reservation.user_department,
            "user_email": reservation.user_email,
            "user_phone": getattr(reservation, 'user_phone', None),
            "purpose": reservation.purpose,
            "status": reservation.status
        })

    return conflicts

def is_time_available(
    db: Session,
    equipment_id: int,
    start_datetime: datetime,
    end_datetime: datetime,
    exclude_reservation_id: Optional[int] = None
) -> bool:
    """
    检查时间段是否可用
    Check if time slot is available
    """
    # 获取设备信息，检查是否允许同时预定
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        return False

    print(f"[调试信息] 检查时间是否可用 - 设备ID: {equipment.id}, 名称: {equipment.name}")
    print(f"[调试信息] 检查时间段: {start_datetime} 至 {end_datetime}")
    print(f"[调试信息] 排除预定ID: {exclude_reservation_id}")
    print(f"[调试信息] 允许同时预约: {equipment.allow_simultaneous}, 最大同时预约数: {equipment.max_simultaneous}")

    # 如果设备允许同时预定
    if equipment.allow_simultaneous:
        # 构建查询来计算时间段内的预约数量
        query = db.query(func.count(Reservation.id)).filter(
            Reservation.equipment_id == equipment_id,
            Reservation.status.in_(["confirmed", "in_use"]),  # 同时检查confirmed和in_use状态
            # 时间重叠条件 - 包含所有四种可能的重叠情况
            or_(
                # 情况1：已有预约的结束时间在新预约的开始时间之后（部分重叠）
                and_(
                    Reservation.start_datetime <= start_datetime,
                    Reservation.end_datetime > start_datetime
                ),
                # 情况2：已有预约的开始时间在新预约的结束时间之前（部分重叠）
                and_(
                    Reservation.start_datetime < end_datetime,
                    Reservation.end_datetime >= end_datetime
                ),
                # 情况3：已有预约完全包含在新预约内（完全重叠）
                and_(
                    Reservation.start_datetime >= start_datetime,
                    Reservation.end_datetime <= end_datetime
                ),
                # 情况4：新预约完全包含在已有预约内（完全重叠）
                and_(
                    Reservation.start_datetime <= start_datetime,
                    Reservation.end_datetime >= end_datetime
                )
            )
        )

        # 排除当前预定（用于更新预定时）
        if exclude_reservation_id:
            query = query.filter(Reservation.id != exclude_reservation_id)

        # 获取重叠的预约数量
        overlap_count = query.scalar()
        print(f"[调试信息] 找到 {overlap_count} 个重叠的预约，最大允许 {equipment.max_simultaneous} 个")

        # 如果数量小于最大同时预定数量，则时间段可用
        is_available = overlap_count < equipment.max_simultaneous
        print(f"[调试信息] 时间段可用: {is_available}")
        return is_available

    # 不允许同时预定，使用原有逻辑
    else:
        # 构建基本查询
        query = db.query(Reservation).filter(
            Reservation.equipment_id == equipment_id,
            Reservation.status.in_(["confirmed", "in_use"])  # 同时检查confirmed和in_use状态
        )

        # 排除当前预定（用于更新预定时）
        if exclude_reservation_id:
            print(f"[调试信息] 排除预定ID: {exclude_reservation_id}")
            query = query.filter(Reservation.id != exclude_reservation_id)

        # 添加时间冲突条件 - 包含所有四种可能的重叠情况
        query = query.filter(
            or_(
                # 情况1：已有预约的结束时间在新预约的开始时间之后（部分重叠）
                and_(
                    Reservation.start_datetime <= start_datetime,
                    Reservation.end_datetime > start_datetime
                ),
                # 情况2：已有预约的开始时间在新预约的结束时间之前（部分重叠）
                and_(
                    Reservation.start_datetime < end_datetime,
                    Reservation.end_datetime >= end_datetime
                ),
                # 情况3：已有预约完全包含在新预约内（完全重叠）
                and_(
                    Reservation.start_datetime >= start_datetime,
                    Reservation.end_datetime <= end_datetime
                ),
                # 情况4：新预约完全包含在已有预约内（完全重叠）
                and_(
                    Reservation.start_datetime <= start_datetime,
                    Reservation.end_datetime >= end_datetime
                )
            )
        )

        # 获取所有重叠的预约并打印详细信息
        overlapping_reservations = query.all()
        print(f"[调试信息] 排除后找到 {len(overlapping_reservations)} 个重叠的预约")

        for res in overlapping_reservations:
            print(f"[调试信息] 重叠预约 ID: {res.id}, 开始时间: {res.start_datetime}, 结束时间: {res.end_datetime}")
            print(f"[调试信息] 重叠条件分析:")
            print(f"  条件1 (已有预约结束>新预约开始): {res.start_datetime <= start_datetime and res.end_datetime > start_datetime}")
            print(f"  条件2 (已有预约开始<新预约结束): {res.start_datetime < end_datetime and res.end_datetime >= end_datetime}")
            print(f"  条件3 (已有预约包含在新预约内): {res.start_datetime >= start_datetime and res.end_datetime <= end_datetime}")
            print(f"  条件4 (新预约包含在已有预约内): {res.start_datetime <= start_datetime and res.end_datetime >= end_datetime}")

        # 如果找到任何冲突的预定，则时间段不可用
        is_available = len(overlapping_reservations) == 0
        print(f"[调试信息] 时间段可用: {is_available}")
        return is_available

def is_equipment_currently_reserved(db: Session, equipment_id: int) -> bool:
    """
    检查设备当前是否被预约
    Check if equipment is currently reserved
    """
    now = datetime.now()

    # 查询当前时间是否在任何预约的时间范围内
    reservation = db.query(Reservation).filter(
        Reservation.equipment_id == equipment_id,
        Reservation.status.in_(["confirmed", "in_use"]),  # 同时检查confirmed和in_use状态
        Reservation.start_datetime <= now,
        Reservation.end_datetime > now
    ).first()

    return reservation is not None

def is_equipment_available(
    db: Session,
    equipment_id: int,
    start_date: str,
    end_date: str,
    exclude_reservation_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    获取设备可用性
    Get equipment availability
    """
    # 添加调试日志
    print(f"[调试信息] 检查设备可用性 - 设备ID: {equipment_id}")
    print(f"[调试信息] 开始日期时间: {start_date}, 结束日期时间: {end_date}")

    # 解析日期时间 - 保留完整的时间信息
    start = parse_datetime(start_date)
    end = parse_datetime(end_date)

    print(f"[调试信息] 解析后的开始日期时间: {start}, 结束日期时间: {end}")

    # 检查是否包含具体时间
    has_specific_time = True

    # 如果没有具体时间，或者只有日期部分，则使用整天
    if start and (start.hour == 0 and start.minute == 0 and start.second == 0) and \
       end and (end.hour == 0 and end.minute == 0 and end.second == 0):
        print(f"[调试信息] 没有具体时间，使用整天检查")
        has_specific_time = False

    # 检查日期顺序
    if start and end and start > end:
        print(f"[调试信息] 警告: 开始日期时间晚于结束日期时间! 交换日期时间...")
        start, end = end, start
        print(f"[调试信息] 交换后: 开始日期时间: {start}, 结束日期时间: {end}")

    if not start or not end:
        print(f"[调试信息] 错误: 无法解析日期时间")
        return {
            "equipment_id": equipment_id,
            "dates": [],
            "available": []
        }

    # 获取设备信息
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        print(f"[调试信息] 错误: 设备不存在")
        return {
            "equipment_id": equipment_id,
            "dates": [],
            "available": []
        }

    print(f"[调试信息] 设备名称: {equipment.name}, 允许同时预约: {equipment.allow_simultaneous}")

    # 如果有具体时间，直接检查这个时间段是否可用
    if has_specific_time:
        print(f"[调试信息] 检查具体时间段: {start} 至 {end}")

        # 直接使用is_time_available函数检查，排除指定的预定ID
        is_available = is_time_available(db, equipment_id, start, end, exclude_reservation_id)

        # 获取冲突的预定信息
        conflicting_reservations = []
        if not is_available:
            conflicting_reservations = get_conflicting_reservations(db, equipment_id, start, end, exclude_reservation_id)

        # 构造结果
        result = {
            "equipment_id": equipment_id,
            "specific_time_check": True,
            "start_datetime": format_datetime(start),
            "end_datetime": format_datetime(end),
            "available": [is_available],  # 使用列表保持API一致性
            "conflicting_reservations": conflicting_reservations  # 添加冲突预定信息
        }

        # 如果设备允许同时预定，添加相关信息
        if equipment.allow_simultaneous:
            result["allow_simultaneous"] = True
            result["max_simultaneous"] = equipment.max_simultaneous

        print(f"[调试信息] 具体时间段可用性结果: {result}")
        return result

    # 以下是原来的按日期检查的逻辑（当没有具体时间时使用）

    # 提取日期部分
    start_date = start.date()
    end_date = end.date()

    # 获取日期范围
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)

    print(f"[调试信息] 日期范围: {[d.strftime('%Y-%m-%d') for d in dates]}")

    # 获取设备预定
    reservations = get_equipment_reservations(
        db, equipment_id,
        from_date=datetime.combine(start_date, datetime.min.time()),
        to_date=datetime.combine(end_date, datetime.max.time()),
        status=["confirmed", "in_use"]  # 包括confirmed和in_use状态
    )

    print(f"[调试信息] 找到 {len(reservations)} 个预约")
    for r in reservations:
        print(f"[调试信息] 预约ID: {r.id}, 开始时间: {r.start_datetime}, 结束时间: {r.end_datetime}, 状态: {r.status}")

    # 检查每天的可用性
    availability = []
    reservation_counts = []  # 存储每天的预约数量

    for date in dates:
        date_start = datetime.combine(date, datetime.min.time())
        date_end = datetime.combine(date, datetime.max.time())

        print(f"[调试信息] 检查日期: {date.strftime('%Y-%m-%d')}, 开始时间: {date_start}, 结束时间: {date_end}")

        # 如果允许同时预定，计算每天的预约数量
        if equipment.allow_simultaneous:
            # 计算当天重叠的预约数量
            day_reservations = [r for r in reservations if
                               (r.start_datetime <= date_end and
                                r.end_datetime >= date_start)]

            count = len(day_reservations)
            reservation_counts.append(count)

            # 如果数量小于最大同时预定数量，则日期可用
            is_available = count < equipment.max_simultaneous
            print(f"[调试信息] 同时预约: 当天预约数量: {count}, 最大允许: {equipment.max_simultaneous}, 可用: {is_available}")
        else:
            # 检查是否有预定冲突
            is_available = True
            for reservation in reservations:
                if (reservation.start_datetime <= date_end and
                    reservation.end_datetime >= date_start):
                    is_available = False
                    print(f"[调试信息] 发现冲突预约: ID: {reservation.id}, 开始: {reservation.start_datetime}, 结束: {reservation.end_datetime}")
                    break

            print(f"[调试信息] 不允许同时预约: 可用: {is_available}")

        availability.append(is_available)

    result = {
        "equipment_id": equipment_id,
        "specific_time_check": False,
        "dates": [format_datetime(d, "%Y-%m-%d") for d in dates],
        "available": availability
    }

    # 如果允许同时预定，添加预约数量信息
    if equipment and equipment.allow_simultaneous:
        result["allow_simultaneous"] = True
        result["max_simultaneous"] = equipment.max_simultaneous
        result["reservation_counts"] = reservation_counts

    print(f"[调试信息] 可用性结果: {result}")
    return result

def update_reservation(
    db: Session,
    reservation_code: str,
    reservation: ReservationUpdate,
    user_type: str = "user",
    user_id: Optional[str] = None,
    reservation_number: Optional[str] = None
) -> Tuple[Optional[Reservation], str]:
    """
    更新预定
    Update reservation

    Args:
        db: 数据库会话
        reservation_code: 预定码
        reservation: 更新数据
        user_type: 用户类型，默认为"user"，可选值为"admin"或"user"
        user_id: 用户ID或用户名，可选
        reservation_number: 预约序号，可选，如果提供则优先使用

    Returns:
        (更新后的预定对象, 消息)
    """
    # 获取预定 - 优先使用预约序号
    if reservation_number:
        logger.info(f"[更新预约] 使用预约序号查询: {reservation_number}")
        db_reservation = db.query(Reservation).filter(
            Reservation.reservation_number == reservation_number
        ).first()
    else:
        logger.info(f"[更新预约] 使用预约码查询: {reservation_code}")
        db_reservation = db.query(Reservation).filter(
            Reservation.reservation_code == reservation_code
        ).first()

    if not db_reservation:
        return None, "预定不存在"

    # 检查预定是否已取消
    if db_reservation.status == "cancelled":
        return None, "预定已取消，无法修改"

    # 检查预定是否已开始（非管理员不能修改已开始的预定）
    from datetime import datetime
    now = datetime.now()
    if user_type != "admin" and db_reservation.start_datetime <= now:
        return None, "预定已开始，无法修改"

    # 准备更新数据
    try:
        update_data = reservation.model_dump(exclude_unset=True)
    except AttributeError:
        # 兼容旧版本pydantic
        update_data = reservation.dict(exclude_unset=True)

    # 如果非管理员尝试修改状态，则忽略
    if user_type != "admin" and "status" in update_data:
        del update_data["status"]

    # 如果更新了时间，检查是否有冲突
    if "start_datetime" in update_data or "end_datetime" in update_data:
        start_datetime = update_data.get("start_datetime", db_reservation.start_datetime)
        end_datetime = update_data.get("end_datetime", db_reservation.end_datetime)

        # 检查时间是否有效
        if start_datetime >= end_datetime:
            return None, "开始时间必须早于结束时间"

        # 检查是否与现有预定冲突
        if not is_time_available(
            db,
            db_reservation.equipment_id,
            start_datetime,
            end_datetime,
            exclude_reservation_id=db_reservation.id
        ):
            # 获取设备信息，检查是否允许同时预定
            equipment = db.query(Equipment).filter(Equipment.id == db_reservation.equipment_id).first()
            if equipment and equipment.allow_simultaneous:
                return None, f"所选时间段已达到最大同时预定数量({equipment.max_simultaneous})"
            else:
                return None, "所选时间段已被预定"

    # 记录修改历史
    try:
        # 记录每个字段的修改
        for key, new_value in update_data.items():
            old_value = getattr(db_reservation, key, None)

            # 跳过未实际修改的字段
            if old_value == new_value:
                continue

            # 转换为字符串以便存储
            old_value_str = str(old_value) if old_value is not None else ""
            new_value_str = str(new_value) if new_value is not None else ""

            # 创建历史记录
            db_history = ReservationHistory(
                reservation_id=db_reservation.id,
                reservation_code=db_reservation.reservation_code,
                reservation_number=db_reservation.reservation_number,
                user_type=user_type,
                user_id=user_id,
                action="update",
                field_name=key,
                old_value=old_value_str,
                new_value=new_value_str
            )
            db.add(db_history)

        # 提交历史记录
        db.flush()
    except Exception as e:
        print(f"记录修改历史失败: {str(e)}")
        # 继续执行，不因历史记录失败而中断更新操作

    # 更新字段
    for key, value in update_data.items():
        setattr(db_reservation, key, value)

    db.commit()
    db.refresh(db_reservation)

    # 注意：邮件发送已在API路由处理函数中处理
    # 这里不需要发送邮件，因为在reservation.py的update_reservation_api函数中已经处理了邮件发送
    # 如果在这里发送邮件，会导致重复发送

    return db_reservation, "预定已更新"

def cancel_reservation(db: Session, reservation_id: int, user_cancel: bool = True) -> Tuple[bool, str]:
    """
    取消预约
    Cancel reservation
    """
    # 查找预约
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        return False, "预约不存在"

    # 添加调试日志 - 取消预约时的时间段信息
    if reservation.time_slot_id:
        time_slot = db.query(EquipmentTimeSlot).filter(EquipmentTimeSlot.id == reservation.time_slot_id).first()
        equipment = db.query(Equipment).filter(Equipment.id == reservation.equipment_id).first()
        if time_slot and equipment:
            print(f"[调试信息] 取消预约 - 设备ID: {equipment.id}, 名称: {equipment.name}, 时间段ID: {time_slot.id}")
            print(f"[调试信息] 同时预约计数取消前: {time_slot.current_count}/{equipment.max_simultaneous}")

    # 如果是循环预约的子预约，需要特殊处理
    if reservation.recurring_reservation_id and user_cancel:
        # 设置为例外
        reservation.is_exception = 1
        reservation.status = "cancelled"
        db.commit()
        db.refresh(reservation)
        return True, "预约已取消"

    # 如果是普通预约，直接更新状态
    from backend.routes.crud.time_slot import decrement_time_slot_count

    try:
        # 更新预约状态
        reservation.status = "cancelled"

        # 如果有关联的时间段，减少时间段的计数
        if reservation.time_slot_id:
            old_count = None
            time_slot = db.query(EquipmentTimeSlot).filter(EquipmentTimeSlot.id == reservation.time_slot_id).first()
            if time_slot:
                old_count = time_slot.current_count

            decrement_time_slot_count(db, reservation.time_slot_id)

            # 添加调试日志 - 显示时间段计数减少情况
            if old_count:
                # 检查时间段是否仍然存在
                time_slot = db.query(EquipmentTimeSlot).filter(EquipmentTimeSlot.id == reservation.time_slot_id).first()
                equipment = db.query(Equipment).filter(Equipment.id == reservation.equipment_id).first()
                if time_slot:
                    print(f"[调试信息] 同时预约计数取消后: {time_slot.current_count}/{equipment.max_simultaneous}")
                else:
                    print(f"[调试信息] 时间段已删除 (计数为0)")

        db.commit()
        db.refresh(reservation)

        # 更新ICS文件
        update_ics_for_reservation(db, reservation)

        # 从日历中移除（如果启用）
        # 注意：此功能暂未实现，需要在未来版本中添加
        # if check_reservation_calendar_sync_enabled():
        #     remove_reservation_from_calendar(reservation)

        # 如果是用户主动取消，发送取消邮件
        if user_cancel:
            send_reservation_cancel_email(reservation)

        return True, "预约已取消"
    except Exception as e:
        db.rollback()
        print(f"取消预约失败: {str(e)}")
        return False, f"取消预约失败: {str(e)}"

def cancel_reservation_by_code(db: Session, reservation_code: str, reservation_number: Optional[str] = None) -> Tuple[bool, str]:
    """
    通过预约码和预约序号取消预约
    Cancel reservation by reservation code and reservation number

    Args:
        db: 数据库会话
        reservation_code: 预约码
        reservation_number: 预约序号（可选），如果提供，则只取消指定预约序号的预约

    Returns:
        (成功标志, 消息)
    """
    try:
        # 构建查询条件
        query = db.query(Reservation)

        # 先尝试使用预约序号（如果提供）
        if reservation_number:
            query = query.filter(Reservation.reservation_number == reservation_number)
        else:
            # 如果没有提供预约序号，则使用预约码
            query = query.filter(Reservation.reservation_code == reservation_code)

        # 获取预约
        reservation = query.first()

        if not reservation:
            print(f"[调试信息] 未找到要取消的预约: 预约码={reservation_code}, 预约序号={reservation_number}")
            return False, "预约不存在"

        # 获取到预约ID后，调用原有的取消预约函数
        return cancel_reservation(db, reservation.id, True)

    except Exception as e:
        db.rollback()
        print(f"通过预约码取消预约失败: {str(e)}")
        return False, f"取消预约失败: {str(e)}"
