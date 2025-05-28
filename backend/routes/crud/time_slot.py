"""
时间段管理模块
Time slot management module
"""
from typing import List, Optional, Tuple, Dict, Any, Union
from datetime import datetime
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from backend.models.equipment_time_slot import EquipmentTimeSlot
from backend.models.equipment import Equipment
from backend.models.reservation import Reservation

def find_overlapping_time_slots(
    db: Session,
    equipment_id: int,
    start_datetime: datetime,
    end_datetime: datetime
) -> List[EquipmentTimeSlot]:
    """
    查找与指定时间段重叠的时间段
    Find time slots that overlap with the specified time range
    """
    return db.query(EquipmentTimeSlot).filter(
        EquipmentTimeSlot.equipment_id == equipment_id,
        # 重叠条件：包含所有四种可能的重叠情况
        or_(
            # 情况1：已有预约的结束时间在新预约的开始时间之后（部分重叠）
            and_(
                EquipmentTimeSlot.start_datetime <= start_datetime,
                EquipmentTimeSlot.end_datetime > start_datetime
            ),
            # 情况2：已有预约的开始时间在新预约的结束时间之前（部分重叠）
            and_(
                EquipmentTimeSlot.start_datetime < end_datetime,
                EquipmentTimeSlot.end_datetime >= end_datetime
            ),
            # 情况3：已有预约完全包含在新预约内（完全重叠）
            and_(
                EquipmentTimeSlot.start_datetime >= start_datetime,
                EquipmentTimeSlot.end_datetime <= end_datetime
            ),
            # 情况4：新预约完全包含在已有预约内（完全重叠）
            and_(
                EquipmentTimeSlot.start_datetime <= start_datetime,
                EquipmentTimeSlot.end_datetime >= end_datetime
            )
        )
    ).all()

def find_containing_time_slot(
    db: Session,
    equipment_id: int,
    start_datetime: datetime,
    end_datetime: datetime
) -> Optional[EquipmentTimeSlot]:
    """
    查找完全包含指定时间段的时间段（如果存在）
    Find a time slot that completely contains the specified time range (if exists)
    """
    return db.query(EquipmentTimeSlot).filter(
        EquipmentTimeSlot.equipment_id == equipment_id,
        EquipmentTimeSlot.start_datetime <= start_datetime,
        EquipmentTimeSlot.end_datetime >= end_datetime
    ).first()

def create_time_slot(
    db: Session,
    equipment_id: int,
    start_datetime: datetime,
    end_datetime: datetime
) -> EquipmentTimeSlot:
    """
    创建新的时间段
    Create a new time slot
    """
    db_time_slot = EquipmentTimeSlot(
        equipment_id=equipment_id,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        current_count=1
    )
    db.add(db_time_slot)
    db.commit()
    db.refresh(db_time_slot)
    return db_time_slot

def increment_time_slot_count(
    db: Session,
    time_slot_id: int
) -> Optional[EquipmentTimeSlot]:
    """
    增加时间段的使用计数
    Increment the usage count of a time slot
    """
    time_slot = db.query(EquipmentTimeSlot).filter(EquipmentTimeSlot.id == time_slot_id).first()
    if time_slot:
        # 获取设备信息用于调试
        equipment = db.query(Equipment).filter(Equipment.id == time_slot.equipment_id).first()
        old_count = time_slot.current_count

        time_slot.current_count += 1

        print(f"[调试信息] 时间段使用计数增加 - 时间段ID: {time_slot.id}, 计数: {old_count} -> {time_slot.current_count}")
        if equipment:
            print(f"[调试信息] 设备: {equipment.name}, 最大同时预约数: {equipment.max_simultaneous}")

        db.commit()
        db.refresh(time_slot)
    return time_slot

def decrement_time_slot_count(
    db: Session,
    time_slot_id: int
) -> Optional[EquipmentTimeSlot]:
    """
    减少时间段的使用计数，如果计数为0则删除该时间段
    Decrement the usage count of a time slot, delete it if count becomes 0
    """
    time_slot = db.query(EquipmentTimeSlot).filter(EquipmentTimeSlot.id == time_slot_id).first()
    if time_slot:
        # 获取设备信息用于调试
        equipment = db.query(Equipment).filter(Equipment.id == time_slot.equipment_id).first()
        old_count = time_slot.current_count

        time_slot.current_count -= 1
        print(f"[调试信息] 时间段使用计数减少 - 时间段ID: {time_slot.id}, 计数: {old_count} -> {time_slot.current_count}")

        if time_slot.current_count <= 0:
            print(f"[调试信息] 时间段计数为0，删除时间段 - 时间段ID: {time_slot.id}")
            db.delete(time_slot)
        db.commit()
    return time_slot

def check_time_slot_availability(
    db: Session,
    equipment_id: int,
    start_datetime: datetime,
    end_datetime: datetime
) -> Tuple[bool, str, Optional[EquipmentTimeSlot]]:
    """
    检查指定设备在指定时间段内是否可以预约
    Check if the equipment is available for reservation during the specified time range

    返回值：(是否可用, 错误信息, 包含该时间段的时间槽)
    Returns: (is_available, error_message, containing_time_slot)
    """
    # 获取设备信息
    equipment = db.query(Equipment).filter(Equipment.id == equipment_id).first()
    if not equipment:
        return False, "设备不存在", None

    print(f"[调试信息] 检查时间段可用性 - 设备ID: {equipment.id}, 名称: {equipment.name}")
    print(f"[调试信息] 检查时间段: {start_datetime} 至 {end_datetime}")

    # 如果设备不允许同时预约，则检查是否有任何重叠的预约
    if not equipment.allow_simultaneous:
        # 查询所有可能重叠的预约
        overlapping_reservations_query = db.query(Reservation).filter(
            Reservation.equipment_id == equipment_id,
            Reservation.status.in_(["confirmed", "in_use"]),
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
        overlapping_reservations = overlapping_reservations_query.all()
        print(f"[调试信息] 找到 {len(overlapping_reservations)} 个重叠的预约")

        for res in overlapping_reservations:
            print(f"[调试信息] 重叠预约 ID: {res.id}, 开始时间: {res.start_datetime}, 结束时间: {res.end_datetime}")
            print(f"[调试信息] 重叠条件分析:")
            print(f"  条件1 (已有预约结束>新预约开始): {res.start_datetime <= start_datetime and res.end_datetime > start_datetime}")
            print(f"  条件2 (已有预约开始<新预约结束): {res.start_datetime < end_datetime and res.end_datetime >= end_datetime}")
            print(f"  条件3 (已有预约包含在新预约内): {res.start_datetime >= start_datetime and res.end_datetime <= end_datetime}")
            print(f"  条件4 (新预约包含在已有预约内): {res.start_datetime <= start_datetime and res.end_datetime >= end_datetime}")

        if overlapping_reservations:
            print(f"[调试信息] 设备不允许同时预约，发现重叠预约数: {len(overlapping_reservations)}")
            return False, "该时间段已被预约", None

        print(f"[调试信息] 设备不允许同时预约，没有重叠预约，可以预约")
        return True, "", None

    # 如果设备允许同时预约
    print(f"[调试信息] 设备允许同时预约，最大同时预约数: {equipment.max_simultaneous}")

    # 首先查找完全包含目标时间段的现有时间段
    containing_slot = find_containing_time_slot(db, equipment_id, start_datetime, end_datetime)

    if containing_slot:
        print(f"[调试信息] 找到包含的时间段 ID: {containing_slot.id}, 当前计数: {containing_slot.current_count}/{equipment.max_simultaneous}")
        # 如果找到包含的时间段，检查是否达到最大同时预约数
        if containing_slot.current_count >= equipment.max_simultaneous:
            print(f"[调试信息] 已达到最大同时预约数，无法再预约")
            return False, f"该时间段已达到最大同时预约数({equipment.max_simultaneous})", containing_slot
        # 未达到最大数量，可以继续预约
        print(f"[调试信息] 未达到最大同时预约数，可以预约，将是第 {containing_slot.current_count + 1} 个预约")
        return True, "", containing_slot

    # 如果没有找到完全包含的时间段，检查是否有部分重叠的时间段
    overlapping_slots = find_overlapping_time_slots(db, equipment_id, start_datetime, end_datetime)

    if overlapping_slots:
        print(f"[调试信息] 发现 {len(overlapping_slots)} 个部分重叠时间段，当前实现不允许部分重叠")
        # 如果有重叠的时间段，当前实现不允许部分重叠
        # 未来可以考虑处理部分重叠的复杂情况，例如创建新的时间段并合并
        return False, "该时间段与现有预约部分重叠，请选择其他时间", None

    # 如果没有任何重叠，可以创建新的时间段
    print(f"[调试信息] 没有找到任何重叠时间段，将创建新的时间段")
    return True, "", None

def get_time_slots_for_equipment(
    db: Session,
    equipment_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    获取设备的时间段列表及其当前使用情况
    Get the list of time slots for an equipment and their current usage
    """
    query = db.query(EquipmentTimeSlot).filter(EquipmentTimeSlot.equipment_id == equipment_id)

    if start_date:
        query = query.filter(EquipmentTimeSlot.end_datetime >= start_date)