"""
预定CRUD操作
Reservation CRUD operations
"""
import logging
import traceback
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_

from backend.models.reservation import Reservation
from backend.models.equipment import Equipment
from backend.schemas.reservation import ReservationCreate, ReservationUpdate
from backend.utils.code_generator import generate_reservation_code
from backend.utils.date_utils import parse_datetime, format_datetime, get_date_range

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

    # 检查是否与现有预定冲突
    if not is_time_available(db, reservation.equipment_id, reservation.start_datetime, reservation.end_datetime):
        return None, "所选时间段已被预定"

    # 生成预定码
    reservation_code = generate_reservation_code()
    while db.query(Reservation).filter(Reservation.reservation_code == reservation_code).first():
        reservation_code = generate_reservation_code()

    # 生成唯一预约序号
    from backend.utils.code_generator import generate_reservation_number
    reservation_number = generate_reservation_number()
    while db.query(Reservation).filter(Reservation.reservation_number == reservation_number).first():
        reservation_number = generate_reservation_number()

    # 创建预定
    # 根据时间计算初始状态
    now = datetime.now()
    if reservation.start_datetime <= now < reservation.end_datetime:
        initial_status = "in_use"  # 如果预约已经开始但还没结束，状态为"使用中"
    elif now >= reservation.end_datetime:
        initial_status = "expired"  # 如果预约已经结束，状态为"已过期"
    else:
        initial_status = "confirmed"  # 如果预约还没开始，状态为"已确认"

    logger.info(f"创建预约，计算初始状态: {initial_status}, 开始时间: {reservation.start_datetime}, 结束时间: {reservation.end_datetime}, 当前时间: {now}")

    db_reservation = Reservation(
        equipment_id=reservation.equipment_id,
        reservation_code=reservation_code,
        reservation_number=reservation_number,  # 添加唯一预约序号
        user_name=reservation.user_name,
        user_department=reservation.user_department,
        user_contact=reservation.user_contact,
        user_email=reservation.user_email,
        start_datetime=reservation.start_datetime,
        end_datetime=reservation.end_datetime,
        purpose=reservation.purpose,
        status=initial_status  # 使用计算好的初始状态
    )

    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)

    # 添加设备信息
    db_reservation.equipment_name = equipment.name
    db_reservation.equipment_category = equipment.category
    db_reservation.equipment_location = equipment.location

    return db_reservation, "预定创建成功"

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
    status: str = "confirmed"
) -> List[Reservation]:
    """
    获取设备预定列表
    Get equipment reservations
    """
    query = db.query(Reservation).filter(
        Reservation.equipment_id == equipment_id,
        Reservation.status == status
    )

    if from_date:
        query = query.filter(Reservation.end_datetime >= from_date)
    if to_date:
        query = query.filter(Reservation.start_datetime <= to_date)

    return query.order_by(Reservation.start_datetime).all()

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
    # 构建基本查询
    query = db.query(Reservation).filter(
        Reservation.equipment_id == equipment_id,
        Reservation.status == "confirmed"
    )

    # 添加时间冲突条件
    query = query.filter(
        # 开始时间在现有预定的时间范围内
        # 或结束时间在现有预定的时间范围内
        # 或完全包含现有预定
        or_(
            and_(
                Reservation.start_datetime <= start_datetime,
                Reservation.end_datetime > start_datetime
            ),
            and_(
                Reservation.start_datetime < end_datetime,
                Reservation.end_datetime >= end_datetime
            ),
            and_(
                Reservation.start_datetime >= start_datetime,
                Reservation.end_datetime <= end_datetime
            )
        )
    )

    # 排除当前预定（用于更新预定时）
    if exclude_reservation_id is not None:
        query = query.filter(Reservation.id != exclude_reservation_id)

    # 执行查询
    result = query.first()

    # 如果查询结果为空，则时间段可用
    if result is None:
        return True
    else:
        return False

def is_equipment_currently_reserved(db: Session, equipment_id: int) -> bool:
    """
    检查设备当前是否被预约
    Check if equipment is currently reserved
    """
    now = datetime.now()

    # 查询当前时间是否在任何预约的时间范围内
    reservation = db.query(Reservation).filter(
        Reservation.equipment_id == equipment_id,
        Reservation.status == "confirmed",
        Reservation.start_datetime <= now,
        Reservation.end_datetime > now
    ).first()

    return reservation is not None

def is_equipment_available(
    db: Session,
    equipment_id: int,
    start_date: str,
    end_date: str
) -> Dict[str, Any]:
    """
    获取设备可用性
    Get equipment availability
    """
    # 解析日期
    start = parse_datetime(start_date, "%Y-%m-%d")
    end = parse_datetime(end_date, "%Y-%m-%d")

    if not start or not end:
        return {
            "equipment_id": equipment_id,
            "dates": [],
            "available": []
        }

    # 获取日期范围
    dates = []
    current = start
    while current <= end:
        dates.append(current)
        current += timedelta(days=1)

    # 获取设备预定
    reservations = get_equipment_reservations(
        db, equipment_id,
        from_date=start,
        to_date=end + timedelta(days=1)
    )

    # 检查每天的可用性
    availability = []
    for date in dates:
        date_start = datetime.combine(date, datetime.min.time())
        date_end = datetime.combine(date, datetime.max.time())

        # 检查是否有预定冲突
        is_available = True
        for reservation in reservations:
            if (reservation.start_datetime <= date_end and
                reservation.end_datetime >= date_start):
                is_available = False
                break

        availability.append(is_available)

    return {
        "equipment_id": equipment_id,
        "dates": [format_datetime(d, "%Y-%m-%d") for d in dates],
        "available": availability
    }

def update_reservation(
    db: Session,
    reservation_code: str,
    reservation: ReservationUpdate
) -> Tuple[Optional[Reservation], str]:
    """
    更新预定
    Update reservation
    """
    # 获取预定
    db_reservation = db.query(Reservation).filter(
        Reservation.reservation_code == reservation_code
    ).first()

    if not db_reservation:
        return None, "预定不存在"

    # 检查预定是否已取消
    if db_reservation.status == "cancelled":
        return None, "预定已取消，无法修改"

    # 准备更新数据
    update_data = reservation.dict(exclude_unset=True)

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
            return None, "所选时间段已被预定"

    # 更新字段
    for key, value in update_data.items():
        setattr(db_reservation, key, value)

    db.commit()
    db.refresh(db_reservation)

    return db_reservation, "预定已更新"

def cancel_reservation(
    db: Session,
    reservation_code: str,
    reservation_number: Optional[str] = None
) -> Tuple[bool, str]:
    """
    取消预定
    Cancel reservation

    Args:
        db: 数据库会话
        reservation_code: 预约码
        reservation_number: 预约序号，如果提供，则只取消指定预约序号的预约
    """
    try:
        # 构建基本查询
        query = db.query(Reservation).filter(
            Reservation.reservation_code == reservation_code
        )

        # 如果提供了预约序号，则只取消指定预约序号的预约
        if reservation_number:
            logger.info(f"[数据库操作] 根据预约序号取消预约: 预约码={reservation_code}, 预约序号={reservation_number}")
            query = query.filter(Reservation.reservation_number == reservation_number)

        # 获取预约记录
        all_reservations = query.all()

        if not all_reservations:
            logger.error(f"预定不存在: 预约码={reservation_code}" + (f", 预约序号={reservation_number}" if reservation_number else ""))
            return False, "预定不存在"

        logger.info(f"[数据库操作] 找到预约数量: {len(all_reservations)}, 预约码={reservation_code}" + (f", 预约序号={reservation_number}" if reservation_number else ""))

        # 记录所有预约的状态
        for res in all_reservations:
            logger.info(f"[数据库状态] 预约状态: ID={res.id}, 预约序号={res.reservation_number}, 状态={res.status}, 开始时间={res.start_datetime}, 结束时间={res.end_datetime}")

        # 更新预约的状态
        updated_count = 0
        for res in all_reservations:
            # 检查预约是否已取消
            if res.status == "cancelled":
                logger.info(f"[数据库操作] 预约已取消，跳过: ID={res.id}, 预约序号={res.reservation_number}")
                continue

            # 记录取消前的状态
            original_status = res.status
            logger.info(f"[数据库操作] 取消预约前状态: ID={res.id}, 预约序号={res.reservation_number}, 状态={original_status}")

            # 更新状态
            res.status = "cancelled"
            updated_count += 1
            logger.info(f"[数据库操作] 已将预约状态更新为cancelled: ID={res.id}, 预约序号={res.reservation_number}")

            # 移除下面取消同一时间段子预约的代码，确保只取消指定的预约
            # 只有当没有提供预约序号时，才考虑循环预约的相关子预约
            if not reservation_number and res.recurring_reservation_id:
                logger.info(f"[数据库操作] 跳过处理循环预约的相关子预约，因为已提供预约序号")

        if updated_count == 0:
            logger.warning(f"[数据库操作] 没有预约的状态被更新为已取消: 预约码={reservation_code}" + (f", 预约序号={reservation_number}" if reservation_number else ""))
            return False, "没有预约的状态被更新"

        # 提交更改
        db.commit()

        # 验证预约状态是否已更新
        verification_count = 0
        all_reservations = query.all()
        for res in all_reservations:
            logger.info(f"[数据库验证] 验证预约状态: ID={res.id}, 预约序号={res.reservation_number}, 状态={res.status}")
            if res.status == "cancelled":
                verification_count += 1

        logger.info(f"[数据库验证] 成功更新预约状态数量: {verification_count}/{len(all_reservations)}")

        return True, "预定已取消"
    except Exception as e:
        db.rollback()
        logger.error(f"取消预定时出错: {str(e)}")
        logger.error(traceback.format_exc())
        return False, f"取消预定时出错: {str(e)}"
