"""
循环预约API路由
Recurring Reservation API routes
"""
import logging
from typing import Optional
from datetime import date, time, datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.recurring_reservation import RecurringReservation
from backend.schemas.recurring_reservation import (
    RecurringReservationCreate, RecurringReservationUpdate,
    RecurringReservationList, RecurringReservation as RecurringReservationSchema,
    RecurringReservationResponse
)
from backend.routes.crud.recurring_reservation import (
    create_recurring_reservation, get_recurring_reservation, get_recurring_reservations,
    get_recurring_reservation_count, update_recurring_reservation, cancel_recurring_reservation,
    get_child_reservations
)
from backend.routes.crud.equipment import get_equipment
from backend.utils.email_sender import (
    send_reservation_confirmation, send_reservation_update,
    send_reservation_cancellation
)
from backend.routes.auth import get_current_admin, optional_admin
from backend.utils.date_utils import format_datetime

router = APIRouter(
    prefix="/api/recurring-reservation",
    tags=["recurring_reservation"],
)

logger = logging.getLogger(__name__)

@router.post("/", response_model=RecurringReservationResponse)
async def create_recurring_reservation_api(
    recurring_reservation: RecurringReservationCreate,
    db: Session = Depends(get_db)
):
    """
    创建新循环预约
    Create new recurring reservation
    """
    try:
        # 检查设备是否存在
        equipment = get_equipment(db, recurring_reservation.equipment_id)
        if not equipment:
            return RecurringReservationResponse(success=False, message="设备不存在", data=None)

        # 创建循环预约
        db_recurring_reservation, message, child_reservations = create_recurring_reservation(db, recurring_reservation)

        if not db_recurring_reservation:
            return RecurringReservationResponse(success=False, message=message, data=None)

        # 发送确认邮件（如果提供了邮箱）
        if db_recurring_reservation.user_email and child_reservations:
            try:
                # 组装循环预约整体信息
                # 解析重复规则
                pattern_type = db_recurring_reservation.pattern_type
                days_of_week = db_recurring_reservation.days_of_week
                days_of_month = db_recurring_reservation.days_of_month
                # 生成重复规则描述
                recurrence_rule = ""
                if pattern_type == "daily":
                    recurrence_rule = "每天 / Daily"
                elif pattern_type == "weekly" and days_of_week:
                    week_map = ['周日','周一','周二','周三','周四','周五','周六']
                    import json
                    days = json.loads(days_of_week) if isinstance(days_of_week, str) else days_of_week
                    recurrence_rule = "每周" + "、".join([week_map[d] for d in days])
                elif pattern_type == "monthly" and days_of_month:
                    import json
                    days = json.loads(days_of_month) if isinstance(days_of_month, str) else days_of_month
                    recurrence_rule = "每月" + "、".join([str(d) + "号" for d in days])
                else:
                    recurrence_rule = pattern_type
                await send_reservation_confirmation(
                    to_email=db_recurring_reservation.user_email,
                    reservation_data={
                        "reservation_code": db_recurring_reservation.reservation_code,
                        "user_name": db_recurring_reservation.user_name,
                        "equipment_name": equipment.name,
                        "equipment_category": equipment.category if hasattr(equipment, 'category') else '',
                        "location": equipment.location if hasattr(equipment, 'location') else '',
                        "description": equipment.description if hasattr(equipment, 'description') else '',
                        "start_date": db_recurring_reservation.start_date.strftime('%Y-%m-%d'),
                        "end_date": db_recurring_reservation.end_date.strftime('%Y-%m-%d'),
                        "recurrence_rule": recurrence_rule,
                        "start_time": db_recurring_reservation.start_time.strftime('%H:%M'),
                        "end_time": db_recurring_reservation.end_time.strftime('%H:%M'),
                        "status": "已确认 / Confirmed"
                    },
                    lang=recurring_reservation.lang or "zh_CN",
                    db=db,
                    is_recurring=True
                )
            except Exception as e:
                logger.error(f"发送预约确认邮件失败: {str(e)}")

        return RecurringReservationResponse(
            success=True,
            message=f"循环预约创建成功，已生成{len(child_reservations)}个预约",
            data=db_recurring_reservation
        )
    except Exception as e:
        logger.error(f"创建循环预约出错: {str(e)}")
        return RecurringReservationResponse(success=False, message=f"创建循环预约出错: {str(e)}", data=None)

@router.get("/", response_model=RecurringReservationList)
async def get_recurring_reservations_api(
    skip: int = 0,
    limit: int = 10,
    equipment_id: Optional[int] = None,
    user_name: Optional[str] = None,
    user_contact: Optional[str] = None,
    status: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_admin = Depends(optional_admin)
):
    """
    获取循环预约列表（管理员可以查看所有循环预约，非管理员只能查看自己的循环预约）
    Get recurring reservation list (admin can view all recurring reservations, non-admin can only view their own)
    """
    try:
        # 非管理员只能查看设备的循环预约，不能查看用户名等信息
        if not current_admin and user_name:
            raise HTTPException(status_code=403, detail="没有权限查看其他用户的循环预约")

        # 获取循环预约列表
        items = get_recurring_reservations(
            db, skip, limit, equipment_id, user_name, user_contact, status, from_date, to_date
        )
        total = get_recurring_reservation_count(
            db, equipment_id, user_name, user_contact, status, from_date, to_date
        )

        # 添加设备信息
        for item in items:
            equipment = get_equipment(db, item.equipment_id)
            if equipment:
                item.equipment_name = equipment.name
                item.equipment_category = equipment.category
                item.equipment_location = equipment.location

        return {"items": items, "total": total}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取循环预约列表出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取循环预约列表出错: {str(e)}")

@router.get("/{recurring_reservation_id}", response_model=RecurringReservationResponse)
async def get_recurring_reservation_api(
    recurring_reservation_id: int,
    db: Session = Depends(get_db)
):
    """
    获取循环预约详情
    Get recurring reservation details
    """
    try:
        # 获取循环预约
        db_recurring_reservation = get_recurring_reservation(db, recurring_reservation_id)
        if not db_recurring_reservation:
            return RecurringReservationResponse(success=False, message="循环预约不存在", data=None)

        # 添加设备信息
        equipment = get_equipment(db, db_recurring_reservation.equipment_id)
        if equipment:
            db_recurring_reservation.equipment_name = equipment.name
            db_recurring_reservation.equipment_category = equipment.category
            db_recurring_reservation.equipment_location = equipment.location

        return RecurringReservationResponse(success=True, message="获取循环预约成功", data=db_recurring_reservation)
    except Exception as e:
        logger.error(f"获取循环预约详情出错: {str(e)}")
        return RecurringReservationResponse(success=False, message=f"获取循环预约详情出错: {str(e)}", data=None)

@router.put("/{recurring_reservation_id}", response_model=RecurringReservationResponse)
async def update_recurring_reservation_api(
    recurring_reservation_id: int,
    recurring_reservation_update: RecurringReservationUpdate,
    update_future_only: int = 1,
    db: Session = Depends(get_db)
):
    """
    更新循环预约信息
    Update recurring reservation information
    """
    try:
        # 获取原循环预约信息
        db_recurring_reservation = get_recurring_reservation(db, recurring_reservation_id)
        if not db_recurring_reservation:
            return RecurringReservationResponse(success=False, message="循环预约不存在", data=None)

        # 检查循环预约是否已取消
        if db_recurring_reservation.status == "cancelled":
            return RecurringReservationResponse(success=False, message="循环预约已取消，无法修改", data=None)

        # 更新循环预约
        updated_reservation, message = update_recurring_reservation(
            db, recurring_reservation_id, recurring_reservation_update, update_future_only
        )

        if not updated_reservation:
            return RecurringReservationResponse(success=False, message=message, data=None)

        # 添加设备信息
        equipment = get_equipment(db, updated_reservation.equipment_id)
        if equipment:
            updated_reservation.equipment_name = equipment.name
            updated_reservation.equipment_category = equipment.category
            updated_reservation.equipment_location = equipment.location

        # 发送更新邮件（如果提供了邮箱）
        if updated_reservation.user_email:
            try:
                # 获取子预约
                child_reservations = get_child_reservations(db, recurring_reservation_id, 0)
                if child_reservations:
                    # 只为第一个子预约发送更新邮件
                    first_reservation = child_reservations[0]
                    await send_reservation_update(
                        first_reservation.user_email,
                        first_reservation.reservation_code,
                        first_reservation.user_name,
                        equipment.name,
                        first_reservation.start_datetime,
                        first_reservation.end_datetime,
                        recurring_reservation_update.lang or "zh_CN"
                    )
            except Exception as e:
                logger.error(f"发送预约更新邮件失败: {str(e)}")

        return RecurringReservationResponse(success=True, message="循环预约已更新", data=updated_reservation)
    except Exception as e:
        logger.error(f"更新循环预约出错: {str(e)}")
        return RecurringReservationResponse(success=False, message=f"更新循环预约出错: {str(e)}", data=None)

@router.post("/cancel/{recurring_reservation_id}")
async def cancel_recurring_reservation_api(
    recurring_reservation_id: int,
    user_email: Optional[str] = None,
    lang: str = "zh_CN",
    db: Session = Depends(get_db)
):
    """
    取消循环预约
    Cancel recurring reservation
    """
    try:
        # 获取循环预约信息（用于邮件发送）
        db_recurring_reservation = get_recurring_reservation(db, recurring_reservation_id)
        if not db_recurring_reservation:
            return {"success": False, "message": "循环预约不存在"}

        # 检查循环预约是否已取消
        if db_recurring_reservation.status == "cancelled":
            return {"success": False, "message": "循环预约已取消"}

        # 获取设备信息
        equipment = get_equipment(db, db_recurring_reservation.equipment_id)

        # 取消循环预约，固定为0表示取消所有已确认状态的预约
        success, message = cancel_recurring_reservation(db, recurring_reservation_id, 0)

        if not success:
            return {"success": False, "message": message}

        # 发送取消邮件（如果提供了邮箱）
        email = user_email or db_recurring_reservation.user_email
        if email:
            try:
                # 解析重复规则
                pattern_type = db_recurring_reservation.pattern_type
                days_of_week = db_recurring_reservation.days_of_week
                days_of_month = db_recurring_reservation.days_of_month
                # 生成重复规则描述
                recurrence_rule = ""
                if pattern_type == "daily":
                    recurrence_rule = "每天 / Daily"
                elif pattern_type == "weekly" and days_of_week:
                    week_map = ['周日','周一','周二','周三','周四','周五','周六']
                    import json
                    days = json.loads(days_of_week) if isinstance(days_of_week, str) else days_of_week
                    recurrence_rule = "每周" + "、".join([week_map[d] for d in days])
                elif pattern_type == "monthly" and days_of_month:
                    import json
                    days = json.loads(days_of_month) if isinstance(days_of_month, str) else days_of_month
                    recurrence_rule = "每月" + "、".join([str(d) + "号" for d in days])
                else:
                    recurrence_rule = pattern_type

                # 创建循环预约数据
                recurring_data = {
                    "reservation_code": db_recurring_reservation.reservation_code,
                    "user_name": db_recurring_reservation.user_name,
                    "equipment_name": equipment.name if equipment else "",
                    "equipment_category": equipment.category if equipment and hasattr(equipment, 'category') else '',
                    "location": equipment.location if equipment and hasattr(equipment, 'location') else '',
                    "pattern_type": recurrence_rule,
                    "start_date": db_recurring_reservation.start_date.strftime('%Y-%m-%d'),
                    "end_date": db_recurring_reservation.end_date.strftime('%Y-%m-%d'),
                    "start_time": db_recurring_reservation.start_time.strftime('%H:%M') if db_recurring_reservation.start_time else "",
                    "end_time": db_recurring_reservation.end_time.strftime('%H:%M') if db_recurring_reservation.end_time else "",
                    "status": "已取消 / Cancelled"
                }

                # 发送整个循环预约取消邮件
                await send_reservation_cancellation(
                    to_email=email,
                    reservation_data=recurring_data,
                    lang=lang,
                    db=db,
                    is_recurring=True,
                    is_child=False
                )
                logger.info(f"发送循环预约取消邮件成功: 收件人={email}")
            except Exception as e:
                logger.error(f"发送预约取消邮件失败: {str(e)}")

        return {"success": True, "message": "循环预约已取消"}
    except Exception as e:
        logger.error(f"取消循环预约出错: {str(e)}")
        return {"success": False, "message": f"取消循环预约出错: {str(e)}"}

@router.get("/code/{reservation_code}", response_model=RecurringReservationResponse)
async def get_recurring_reservation_by_code_api(
    reservation_code: str,
    db: Session = Depends(get_db)
):
    """
    通过预定码获取循环预约详情
    Get recurring reservation details by reservation code
    """
    try:
        # 查询循环预约
        db_recurring_reservation = db.query(RecurringReservation).filter(
            RecurringReservation.reservation_code == reservation_code
        ).first()

        if not db_recurring_reservation:
            return RecurringReservationResponse(success=False, message="循环预约不存在", data=None)

        # 添加设备信息
        equipment = get_equipment(db, db_recurring_reservation.equipment_id)
        if equipment:
            db_recurring_reservation.equipment_name = equipment.name
            db_recurring_reservation.equipment_category = equipment.category
            db_recurring_reservation.equipment_location = equipment.location

        return RecurringReservationResponse(success=True, message="获取循环预约成功", data=db_recurring_reservation)
    except Exception as e:
        logger.error(f"通过预定码获取循环预约详情出错: {str(e)}")
        return RecurringReservationResponse(success=False, message=f"获取循环预约详情出错: {str(e)}", data=None)

@router.get("/{recurring_reservation_id}/reservations")
async def get_child_reservations_api(
    recurring_reservation_id: int,
    include_past: int = 0,
    db: Session = Depends(get_db)
):
    """
    获取循环预约的子预约
    Get child reservations of recurring reservation
    """
    try:
        # 检查循环预约是否存在
        db_recurring_reservation = get_recurring_reservation(db, recurring_reservation_id)
        if not db_recurring_reservation:
            return {"success": False, "message": "循环预约不存在", "reservations": []}

        # 获取子预约
        reservations = get_child_reservations(db, recurring_reservation_id, include_past)

        # 格式化返回数据
        reservation_list = []
        for reservation in reservations:
            reservation_list.append({
                "id": reservation.id,
                "reservation_code": reservation.reservation_code,
                "reservation_number": reservation.reservation_number,  # 添加预约序号字段
                "start_datetime": reservation.start_datetime,
                "end_datetime": reservation.end_datetime,
                "status": reservation.status,
                "is_exception": reservation.is_exception
            })

        return {
            "success": True,
            "message": "获取子预约成功",
            "reservations": reservation_list
        }
    except Exception as e:
        logger.error(f"获取子预约出错: {str(e)}")
        return {"success": False, "message": f"获取子预约出错: {str(e)}", "reservations": []}
