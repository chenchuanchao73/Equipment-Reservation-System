"""
预定API路由
Reservation API routes
"""
import logging
from typing import Optional
from datetime import datetime, timedelta
import traceback
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend.models.reservation import Reservation
from backend.models.equipment import Equipment
from backend.schemas.reservation import (
    ReservationCreate, ReservationUpdate,
    ReservationList, Reservation as ReservationSchema,
    ReservationResponse, ReservationCancel
)
from backend.routes.crud.reservation import (
    create_reservation, get_reservation_by_code, get_reservation_by_id,
    get_reservations, get_reservation_count,
    update_reservation, cancel_reservation, is_equipment_available
)
from backend.routes.crud.equipment import get_equipment
from backend.utils.date_utils import format_datetime
from backend.utils.email_sender import (
    send_reservation_confirmation, send_reservation_update,
    send_reservation_cancellation
)
from backend.routes.auth import get_current_admin, optional_admin

router = APIRouter(
    prefix="/api/reservation",
    tags=["reservation"],
)

logger = logging.getLogger(__name__)

@router.post("/", response_model=ReservationResponse)
async def create_reservation_api(
    reservation: ReservationCreate,
    db: Session = Depends(get_db)
):
    """
    创建新预定
    Create new reservation
    """
    try:
        # 检查设备是否存在
        equipment = get_equipment(db, reservation.equipment_id)
        if not equipment:
            return ReservationResponse(success=False, message="设备不存在", data=None)

        # 创建预定
        db_reservation, message = create_reservation(db, reservation)

        if not db_reservation:
            return ReservationResponse(success=False, message=message, data=None)

        # 生成预定二维码
        base_url = "http://localhost:8080"
        # 二维码功能已移除

        # 准备邮件数据
        if reservation.user_email:
            email_data = {
                "reservation_code": db_reservation.reservation_code,
                "user_name": db_reservation.user_name,
                "equipment_name": equipment.name,
                "equipment_category": equipment.category,
                "location": equipment.location,
                "start_datetime": format_datetime(db_reservation.start_datetime),
                "end_datetime": format_datetime(db_reservation.end_datetime),
                "purpose": db_reservation.purpose,
                "description": equipment.description,
                # 二维码功能已移除
                "site_url": "http://localhost:8000",  # 应该从配置中获取
                "status": "已确认 / Confirmed"  # 补充状态字段，确保邮件模板能显示
            }

            # 发送邮件
            await send_reservation_confirmation(
                to_email=reservation.user_email,
                reservation_data=email_data,
                lang=reservation.lang or "zh_CN",
                db=db
            )

        # 返回预定信息
        return ReservationResponse(
            success=True,
            message="预定创建成功",
            data=db_reservation
        )
    except Exception as e:
        logger.error(f"创建预定出错: {str(e)}")
        return ReservationResponse(
            success=False,
            message=f"创建预定出错: {str(e)}",
            data=None
        )

@router.get("/", response_model=ReservationList)
async def get_reservations_api(
    skip: int = 0,
    limit: int = 10,
    equipment_id: Optional[int] = None,
    user_name: Optional[str] = None,
    user_contact: Optional[str] = None,
    status: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    category: Optional[str] = None,
    reservation_code: Optional[str] = None,
    code: Optional[str] = None,  # 兼容旧版参数
    sort_by: Optional[str] = None,  # 排序字段
    sort_order: Optional[str] = None,  # 排序方式
    db: Session = Depends(get_db),
    current_admin = Depends(optional_admin)
):
    """
    获取预定列表（管理员可以查看所有预定，非管理员只能查看自己的预定）
    Get reservation list (admin can view all reservations, non-admin can only view their own)
    """
    try:
        # 非管理员只能查看设备的预定，不能查看用户名等信息
        if not current_admin and user_name:
            raise HTTPException(status_code=403, detail="没有权限查看其他用户的预定")

        # 如果提供了code参数，优先使用code参数
        effective_reservation_code = code if code else reservation_code

        # 记录排序参数
        logger.info(f"排序参数: sort_by={sort_by}, sort_order={sort_order}")

        items = get_reservations(
            db, equipment_id, user_name, user_contact, status,
            from_date, to_date, category, effective_reservation_code, skip, limit,
            sort_by, sort_order
        )
        total = get_reservation_count(
            db, equipment_id, user_name, user_contact, status,
            from_date, to_date, category, effective_reservation_code
        )
        return {"items": items, "total": total}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取预定列表出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取预定列表出错: {str(e)}")

@router.get("/number/{reservation_number}", response_model=ReservationResponse)
async def get_reservation_by_number_api(
    reservation_number: str,
    db: Session = Depends(get_db)
):
    """
    通过预约序号获取预约详情
    Get reservation details by reservation number

    Args:
        reservation_number: 预约序号
        db: 数据库会话
    """
    try:
        logger.info(f"[API调用] 通过预约序号获取预约详情: 预约序号={reservation_number}")

        # 记录所有预约序号，用于调试
        all_reservations = db.query(Reservation).all()
        logger.debug(f"[数据库调试] 数据库中的所有预约序号: {[r.reservation_number for r in all_reservations]}")

        # 直接通过预约序号查询
        logger.debug(f"[数据库查询] 执行查询: Reservation.reservation_number == {reservation_number}")
        reservation = db.query(Reservation).filter(
            Reservation.reservation_number == reservation_number
        ).first()

        if not reservation:
            logger.warning(f"[数据库查询] 未找到预约: 预约序号={reservation_number}")

            # 尝试模糊匹配
            similar_reservations = db.query(Reservation).filter(
                Reservation.reservation_number.like(f"%{reservation_number}%")
            ).all()

            if similar_reservations:
                logger.info(f"[数据库查询] 找到类似的预约: {[(r.id, r.reservation_number) for r in similar_reservations]}")

            return ReservationResponse(success=False, message="预约不存在", data=None)

        logger.info(f"[数据库查询] 通过预约序号找到预约: ID={reservation.id}, 状态={reservation.status}, 预约序号={reservation.reservation_number}")

        # 获取设备信息
        equipment = get_equipment(db, reservation.equipment_id)
        if equipment:
            reservation.equipment_name = equipment.name
            reservation.equipment_category = equipment.category
            reservation.equipment_location = equipment.location
            logger.debug(f"[数据库查询] 获取设备信息: ID={equipment.id}, 名称={equipment.name}")

        # 创建返回对象
        reservation_dict = reservation.__dict__.copy()
        if '_sa_instance_state' in reservation_dict:
            del reservation_dict['_sa_instance_state']

        logger.info(f"[API响应] 成功获取预约: ID={reservation.id}, 状态={reservation.status}, 开始时间={reservation.start_datetime}, 结束时间={reservation.end_datetime}, 预约序号={reservation.reservation_number}")
        return ReservationResponse(success=True, message="获取预约成功", data=reservation_dict)
    except Exception as e:
        logger.error(f"获取预约详情出错: {str(e)}")
        logger.error(traceback.format_exc())
        return ReservationResponse(
            success=False,
            message=f"获取预约详情出错: {str(e)}",
            data=None
        )

@router.get("/code/{reservation_code}", response_model=ReservationResponse)
async def get_reservation_by_code_api(
    reservation_code: str,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    reservation_number: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    通过预定码获取预定详情
    Get reservation details by reservation code

    Args:
        reservation_code: 预约码
        start_time: 开始时间（可选）
        end_time: 结束时间（可选）
        reservation_number: 预约序号（可选），如果提供，则只获取指定预约序号的预约
        db: 数据库会话
    """
    try:
        logger.info(f"获取预约详情: 预约码={reservation_code}, 开始时间={start_time}, 结束时间={end_time}, 预约序号={reservation_number}")

        # 如果提供了预约序号，优先使用预约序号查询
        if reservation_number:
            logger.info(f"提供了预约序号 {reservation_number}，优先使用预约序号查询")

            # 检查预约序号是否是RN-开头的格式
            if isinstance(reservation_number, str) and reservation_number.startswith("RN-"):
                logger.info(f"使用预约序号查询: {reservation_number}")

                # 直接通过预约序号查询，不依赖于预约码
                direct_reservation = db.query(Reservation).filter(
                    Reservation.reservation_number == reservation_number
                ).first()

                if direct_reservation:
                    logger.info(f"通过预约序号直接找到预约: ID={direct_reservation.id}, 状态={direct_reservation.status}")
                    reservation = direct_reservation

                    # 添加设备信息
                    equipment = db.query(Equipment).filter(Equipment.id == reservation.equipment_id).first()
                    if equipment:
                        reservation.equipment_name = equipment.name
                        reservation.equipment_category = equipment.category
                        reservation.equipment_location = equipment.location

                    # 如果是通过预约序号查询，直接返回结果
                    logger.info(f"通过预约序号查询成功，返回预约详情: ID={reservation.id}, 状态={reservation.status}")
                    # 将对象转换为字典
                    reservation_dict = {
                        "id": reservation.id,
                        "equipment_id": reservation.equipment_id,
                        "user_name": reservation.user_name,
                        "user_contact": reservation.user_contact,
                        "user_department": reservation.user_department,
                        "user_email": reservation.user_email,
                        "start_datetime": reservation.start_datetime.isoformat() if reservation.start_datetime else None,
                        "end_datetime": reservation.end_datetime.isoformat() if reservation.end_datetime else None,
                        "status": reservation.status,
                        "purpose": reservation.purpose,
                        "reservation_code": reservation.reservation_code,
                        "reservation_number": reservation.reservation_number,
                        "equipment_name": reservation.equipment_name if hasattr(reservation, "equipment_name") else None,
                        "equipment_category": reservation.equipment_category if hasattr(reservation, "equipment_category") else None,
                        "equipment_location": reservation.equipment_location if hasattr(reservation, "equipment_location") else None,
                        "created_at": reservation.created_at.isoformat() if hasattr(reservation, "created_at") and reservation.created_at else None
                    }

                    # 添加updated_at字段（如果存在）
                    if hasattr(reservation, "updated_at") and reservation.updated_at:
                        reservation_dict["updated_at"] = reservation.updated_at.isoformat()
                    return ReservationResponse(success=True, message="获取预定成功", data=reservation_dict)

        # 首先检查这个预约码是否属于循环预约
        from backend.models.recurring_reservation import RecurringReservation

        # 查询循环预约表
        recurring_reservation = db.query(RecurringReservation).filter(
            RecurringReservation.reservation_code == reservation_code
        ).first()

        if recurring_reservation:
            logger.info(f"预约码 {reservation_code} 属于循环预约，ID={recurring_reservation.id}")

            # 如果提供了预约序号，尝试查找特定的子预约
            if reservation_number:
                logger.info(f"尝试查找循环预约的子预约: 预约码={reservation_code}, 预约序号={reservation_number}")

                # 查询特定的子预约
                child_reservation = db.query(Reservation).filter(
                    Reservation.reservation_code == reservation_code,
                    Reservation.reservation_number == reservation_number
                ).first()

                if child_reservation:
                    logger.info(f"找到循环预约的子预约: ID={child_reservation.id}, 状态={child_reservation.status}")

                    # 添加设备信息
                    equipment = db.query(Equipment).filter(Equipment.id == child_reservation.equipment_id).first()
                    if equipment:
                        child_reservation.equipment_name = equipment.name
                        child_reservation.equipment_category = equipment.category
                        child_reservation.equipment_location = equipment.location

                    # 将对象转换为字典
                    reservation_dict = {
                        "id": child_reservation.id,
                        "equipment_id": child_reservation.equipment_id,
                        "user_name": child_reservation.user_name,
                        "user_contact": child_reservation.user_contact,
                        "user_department": child_reservation.user_department,
                        "user_email": child_reservation.user_email,
                        "start_datetime": child_reservation.start_datetime.isoformat() if child_reservation.start_datetime else None,
                        "end_datetime": child_reservation.end_datetime.isoformat() if child_reservation.end_datetime else None,
                        "status": child_reservation.status,
                        "purpose": child_reservation.purpose,
                        "reservation_code": child_reservation.reservation_code,
                        "reservation_number": child_reservation.reservation_number,
                        "equipment_name": child_reservation.equipment_name if hasattr(child_reservation, "equipment_name") else None,
                        "equipment_category": child_reservation.equipment_category if hasattr(child_reservation, "equipment_category") else None,
                        "equipment_location": child_reservation.equipment_location if hasattr(child_reservation, "equipment_location") else None,
                        "created_at": child_reservation.created_at.isoformat() if hasattr(child_reservation, "created_at") and child_reservation.created_at else None,
                        "is_child_of_recurring": True,
                        "recurring_id": recurring_reservation.id
                    }

                    return ReservationResponse(success=True, message="获取预定成功", data=reservation_dict)
                else:
                    logger.warning(f"未找到循环预约的子预约: 预约码={reservation_code}, 预约序号={reservation_number}")

            # 返回特殊响应，告诉前端这是一个循环预约
            return {
                "success": False,  # 设置为False，让前端知道这不是普通预约
                "message": "这是一个循环预约",
                "data": {
                    "is_recurring": True,
                    "recurring_id": recurring_reservation.id,
                    "reservation_code": reservation_code
                }
            }

        # 如果提供了时间参数，使用时间参数查询特定的预定
        reservation = None
        start_date = None
        end_date = None
        date_matches = False
        exact_datetime_matches = False

        # 解析时间参数
        if start_time:
            logger.info(f"使用时间参数查询特定预定: {start_time} - {end_time}")

            try:
                # 解析时间参数，支持多种格式
                if 'T' in start_time:
                    start_datetime = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                else:
                    start_datetime = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")

                # 提取日期部分
                start_date = start_datetime.date()
                logger.info(f"解析的开始日期: {start_date}")

                # 查找与这个日期匹配的预约
                date_match_query = db.query(Reservation).filter(
                    Reservation.reservation_code == reservation_code,
                    func.date(Reservation.start_datetime) == start_date
                )

                # 记录SQL查询语句用于调试
                logger.debug(f"日期匹配SQL查询: {str(date_match_query)}")

                # 获取匹配查询结果
                date_match_reservation = date_match_query.first()

                if date_match_reservation:
                    logger.info(f"找到日期匹配的预约: ID={date_match_reservation.id}, 状态={date_match_reservation.status}")
                    reservation = date_match_reservation
                    date_matches = True

                    # 进一步检查确切的时间是否匹配
                    if end_time:
                        try:
                            if 'T' in end_time:
                                end_datetime = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
                            else:
                                end_datetime = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")

                            # 获取预约的时间
                            res_start_time = date_match_reservation.start_datetime
                            res_end_time = date_match_reservation.end_datetime

                            # 检查小时和分钟是否匹配
                            if (res_start_time.hour == start_datetime.hour and
                                res_start_time.minute == start_datetime.minute and
                                res_end_time.hour == end_datetime.hour and
                                res_end_time.minute == end_datetime.minute):
                                exact_datetime_matches = True
                                logger.info("找到精确的时间匹配！")
                            else:
                                logger.info(f"日期匹配但时间不完全匹配: 预约时间={res_start_time.hour}:{res_start_time.minute}-{res_end_time.hour}:{res_end_time.minute}, 查询时间={start_datetime.hour}:{start_datetime.minute}-{end_datetime.hour}:{end_datetime.minute}")
                        except Exception as e:
                            logger.error(f"解析结束时间出错: {str(e)}")
                else:
                    logger.warning(f"未找到日期 {start_date} 的精确匹配预约")
            except Exception as e:
                logger.error(f"解析时间参数出错: {str(e)}")
                logger.error(traceback.format_exc())

        # 如果提供了预约序号，则优先使用预约序号查询
        if reservation_number:
            logger.info(f"提供了预约序号参数: {reservation_number}, 类型: {type(reservation_number)}")

            # 确保reservation_number是字符串，处理可能的JSON对象
            try:
                # 如果是字符串但看起来像JSON
                if isinstance(reservation_number, str) and (reservation_number.startswith('{') or reservation_number.startswith('[')):
                    logger.warning(f"预约序号参数是JSON格式，尝试解析: {reservation_number}")
                    import json
                    try:
                        parsed_number = json.loads(reservation_number)
                        if isinstance(parsed_number, dict) and 'reservation_number' in parsed_number:
                            reservation_number = parsed_number['reservation_number']
                            logger.info(f"从JSON对象中提取预约序号: {reservation_number}")
                        elif isinstance(parsed_number, dict) and '$oid' in parsed_number:
                            reservation_number = parsed_number['$oid']
                            logger.info(f"从JSON对象中提取$oid: {reservation_number}")
                    except json.JSONDecodeError:
                        logger.error(f"无法解析JSON格式的预约序号: {reservation_number}")

                # 确保最终的reservation_number是字符串
                if not isinstance(reservation_number, str):
                    reservation_number = str(reservation_number)
                    logger.info(f"将预约序号转换为字符串: {reservation_number}")

            except Exception as e:
                logger.error(f"处理预约序号参数时出错: {str(e)}")
                logger.error(traceback.format_exc())

            # 检查预约序号是否是RN-开头的格式
            if isinstance(reservation_number, str) and reservation_number.startswith("RN-"):
                logger.info(f"使用预约序号查询: {reservation_number}")

                # 直接通过预约序号查询，不依赖于预约码
                direct_reservation = db.query(Reservation).filter(
                    Reservation.reservation_number == reservation_number
                ).first()

                if direct_reservation:
                    logger.info(f"通过预约序号直接找到预约: ID={direct_reservation.id}, 状态={direct_reservation.status}")
                    reservation = direct_reservation

                    # 添加设备信息
                    equipment = db.query(Equipment).filter(Equipment.id == reservation.equipment_id).first()
                    if equipment:
                        reservation.equipment_name = equipment.name
                        reservation.equipment_category = equipment.category
                        reservation.equipment_location = equipment.location

                    # 如果是通过预约序号查询，直接返回结果
                    logger.info(f"通过预约序号查询成功，返回预约详情: ID={reservation.id}, 状态={reservation.status}")
                    return ReservationResponse(success=True, message="获取预定成功", data=reservation.__dict__)
            else:
                logger.warning(f"预约序号格式不正确，忽略: {reservation_number}")
                direct_reservation = None

            if direct_reservation:
                logger.info(f"通过预约序号直接找到预约: ID={direct_reservation.id}, 状态={direct_reservation.status}")
                reservation = direct_reservation

                # 添加设备信息
                equipment = db.query(Equipment).filter(Equipment.id == reservation.equipment_id).first()
                if equipment:
                    reservation.equipment_name = equipment.name
                    reservation.equipment_category = equipment.category
                    reservation.equipment_location = equipment.location
            else:
                # 如果直接查询失败，尝试使用预约码和预约序号组合查询
                logger.info(f"通过预约序号直接查询未找到预约，尝试使用预约码和预约序号组合查询")
                reservation = get_reservation_by_code(db, reservation_code, reservation_number)
                if reservation:
                    logger.info(f"通过预约码和预约序号组合查询找到预约: ID={reservation.id}, 状态={reservation.status}")
                else:
                    logger.warning(f"通过预约序号未找到预约: 预约码={reservation_code}, 预约序号={reservation_number}")

        # 如果没有找到预约或没有时间参数，尝试获取最近的预约
        if not reservation:
            logger.info(f"尝试获取与预约码匹配的预约")

            # 构建基本查询
            base_query = db.query(Reservation).filter(
                Reservation.reservation_code == reservation_code
            )

            if start_date:
                # 如果有日期参数但没找到精确匹配，尝试找最近的日期
                logger.info(f"尝试查找接近 {start_date} 的预约")

                # 首先尝试找同一个星期几的预约（对于循环预约）
                weekday_query = base_query.filter(
                    func.strftime('%w', Reservation.start_datetime) == func.strftime('%w', start_date.strftime("%Y-%m-%d"))
                ).order_by(Reservation.start_datetime)

                weekday_reservation = weekday_query.first()
                if weekday_reservation:
                    logger.info(f"找到同星期几的预约: ID={weekday_reservation.id}, 状态={weekday_reservation.status}")
                    reservation = weekday_reservation
                else:
                    # 如果找不到同星期几的，尝试找最近的日期
                    logger.info("未找到同星期几的预约，尝试找最近的预约")

                    # 查找最接近的预约
                    # 优先选择状态为"confirmed"的预约
                    confirmed_reservation = base_query.filter(
                        Reservation.status == "confirmed"
                    ).order_by(Reservation.start_datetime).first()

                    if confirmed_reservation:
                        logger.info(f"找到已确认的预约: ID={confirmed_reservation.id}")
                        reservation = confirmed_reservation
                    else:
                        # 如果没有找到confirmed状态的预约，获取第一个匹配的预约
                        any_reservation = base_query.order_by(Reservation.start_datetime).first()

                        if any_reservation:
                            logger.info(f"找到预约: ID={any_reservation.id}, 状态={any_reservation.status}")
                            reservation = any_reservation
                        else:
                            logger.warning(f"未找到与预约码匹配的预约: {reservation_code}")
            else:
                # 如果没有日期参数，直接找最近的预约
                logger.info("没有日期参数，直接查找最近的预约")

                # 优先选择状态为"confirmed"的预约
                confirmed_reservation = base_query.filter(
                    Reservation.status == "confirmed"
                ).order_by(Reservation.start_datetime).first()

                if confirmed_reservation:
                    logger.info(f"找到已确认的预约: ID={confirmed_reservation.id}")
                    reservation = confirmed_reservation
                else:
                    # 如果没有找到confirmed状态的预约，获取第一个匹配的预约
                    any_reservation = base_query.order_by(Reservation.start_datetime).first()

                    if any_reservation:
                        logger.info(f"找到预约: ID={any_reservation.id}, 状态={any_reservation.status}")
                        reservation = any_reservation
                    else:
                        logger.warning(f"未找到与预约码匹配的预约: {reservation_code}")

        if not reservation:
            return ReservationResponse(success=False, message="预定不存在", data=None)

        # 获取设备信息
        equipment = get_equipment(db, reservation.equipment_id)
        if equipment:
            reservation.equipment_name = equipment.name
            reservation.equipment_category = equipment.category
            reservation.equipment_location = equipment.location

        # 创建返回对象
        reservation_dict = reservation.__dict__.copy()
        if '_sa_instance_state' in reservation_dict:
            del reservation_dict['_sa_instance_state']

        # 如果提供了时间参数，保存原始时间并添加显示时间
        if start_time and end_time:
            logger.info(f"保存原始时间并添加显示时间")
            reservation_dict['original_start_datetime'] = reservation.start_datetime.isoformat() if hasattr(reservation.start_datetime, 'isoformat') else reservation.start_datetime
            reservation_dict['original_end_datetime'] = reservation.end_datetime.isoformat() if hasattr(reservation.end_datetime, 'isoformat') else reservation.end_datetime
            reservation_dict['display_start_time'] = start_time
            reservation_dict['display_end_time'] = end_time

            # 添加日期匹配标志
            reservation_dict['date_matches'] = date_matches
            reservation_dict['exact_datetime_matches'] = exact_datetime_matches
            logger.info(f"日期匹配标志: {date_matches}, 精确时间匹配标志: {exact_datetime_matches}")

            # 添加日期比较信息用于调试
            if start_date:
                res_date = reservation.start_datetime.date() if hasattr(reservation.start_datetime, 'date') else None
                reservation_dict['debug_info'] = {
                    'query_date': start_date.isoformat(),
                    'reservation_date': res_date.isoformat() if res_date else None,
                    'dates_equal': start_date == res_date if res_date else False,
                    'weekday_query': start_date.weekday() if start_date else None,
                    'res_weekday': res_date.weekday() if res_date else None
                }
                logger.info(f"日期比较信息: {reservation_dict['debug_info']}")

        logger.info(f"成功获取预约: ID={reservation.id}, 状态={reservation.status}, 开始时间={reservation.start_datetime}, 结束时间={reservation.end_datetime}, 预约序号={reservation.reservation_number}")
        return ReservationResponse(success=True, message="获取预定成功", data=reservation_dict)
    except Exception as e:
        logger.error(f"获取预定详情出错: {str(e)}")
        logger.error(traceback.format_exc())
        return ReservationResponse(
            success=False,
            message=f"获取预定详情出错: {str(e)}",
            data=None
        )

@router.put("/code/{reservation_code}", response_model=ReservationResponse)
async def update_reservation_api(
    reservation_code: str,
    reservation_update: ReservationUpdate,
    db: Session = Depends(get_db)
):
    """
    更新预定信息
    Update reservation information
    """
    try:
        # 获取原预定信息
        # 不传递reservation_number参数，以获取与预约码匹配的任何预约
        reservation = get_reservation_by_code(db, reservation_code, None)
        if not reservation:
            return ReservationResponse(success=False, message="预定不存在", data=None)

        # 检查预定是否已取消
        if reservation.status == "cancelled":
            return ReservationResponse(success=False, message="预定已取消，无法修改", data=None)

        # 更新预定
        db_reservation, message = update_reservation(db, reservation_code, reservation_update)

        if not db_reservation:
            return ReservationResponse(success=False, message=message, data=None)

        # 获取设备信息
        equipment = get_equipment(db, db_reservation.equipment_id)
        if equipment:
            db_reservation.equipment_name = equipment.name
            db_reservation.equipment_category = equipment.category
            db_reservation.equipment_location = equipment.location

        # 准备邮件数据
        if reservation_update.user_email or reservation.user_email:
            email_data = {
                "reservation_code": db_reservation.reservation_code,
                "user_name": db_reservation.user_name,
                "equipment_name": equipment.name if equipment else "",
                "equipment_category": equipment.category if equipment else "",
                "location": equipment.location if equipment else "",
                "start_datetime": format_datetime(db_reservation.start_datetime),
                "end_datetime": format_datetime(db_reservation.end_datetime),
                "purpose": db_reservation.purpose,
                "description": equipment.description,
                # 二维码功能已移除
                "site_url": "http://localhost:8000",  # 应该从配置中获取
                "changed": {
                    "start_datetime": reservation_update.start_datetime is not None,
                    "end_datetime": reservation_update.end_datetime is not None,
                    "purpose": reservation_update.purpose is not None
                },
                "status": "已确认 / Confirmed"  # 补充状态字段，确保邮件模板能显示
            }

            # 发送邮件
            send_reservation_update(
                to_email=reservation_update.user_email or reservation.user_email,
                reservation_data=email_data,
                lang=reservation_update.lang or "zh_CN"
            )

        return ReservationResponse(
            success=True,
            message="预定已更新",
            data=db_reservation
        )
    except Exception as e:
        logger.error(f"更新预定出错: {str(e)}")
        return ReservationResponse(
            success=False,
            message=f"更新预定出错: {str(e)}",
            data=None
        )

@router.post("/cancel/code/{reservation_code}")
async def cancel_reservation_api(
    reservation_code: str,
    cancel_data: Optional[ReservationCancel] = None,
    user_email: Optional[str] = None,
    reservation_number: Optional[str] = None,
    lang: str = "zh_CN",
    db: Session = Depends(get_db)
):
    """
    取消预定
    Cancel reservation

    Args:
        reservation_code: 预约码
        cancel_data: 取消预定请求数据
        user_email: 用户邮箱（可选）
        reservation_number: 预约序号（可选），如果提供，则只取消指定预约序号的预约
        lang: 语言
        db: 数据库会话
    """
    try:
        # 如果提供了请求体数据，则使用请求体中的参数
        if cancel_data:
            logger.info(f"[API请求体] 取消预约请求体: {cancel_data.dict()}")
            if cancel_data.user_email:
                user_email = cancel_data.user_email
            if cancel_data.reservation_number:
                reservation_number = cancel_data.reservation_number
            if cancel_data.lang:
                lang = cancel_data.lang

        # 记录API调用信息
        logger.info(f"[API调用] 取消预约API: 预约码={reservation_code}, 用户邮箱={user_email}, 预约序号={reservation_number}, 语言={lang}")

        # 处理reservation_number参数
        if reservation_number:
            # 确保reservation_number是字符串，处理可能的JSON对象
            try:
                if isinstance(reservation_number, str) and (reservation_number.startswith('{') or reservation_number.startswith('[')):
                    logger.warning(f"[API参数] 预约序号参数是JSON格式，尝试解析: {reservation_number}")
                    import json
                    try:
                        parsed_number = json.loads(reservation_number)
                        if isinstance(parsed_number, dict) and 'reservation_number' in parsed_number:
                            reservation_number = parsed_number['reservation_number']
                            logger.info(f"[API参数] 从JSON对象中提取预约序号: {reservation_number}")
                        elif isinstance(parsed_number, dict) and '$oid' in parsed_number:
                            reservation_number = parsed_number['$oid']
                            logger.info(f"[API参数] 从JSON对象中提取$oid: {reservation_number}")
                    except json.JSONDecodeError:
                        logger.error(f"[API参数] 无法解析JSON格式的预约序号: {reservation_number}")
            except Exception as e:
                logger.error(f"[API参数] 处理预约序号参数时出错: {str(e)}")
                logger.error(traceback.format_exc())

            logger.info(f"[API参数] 预约序号参数存在: {reservation_number}")
        else:
            logger.warning(f"[API参数] 预约序号参数不存在，将取消所有具有相同预约码的预约")

        # 构建查询条件
        query = db.query(Reservation).filter(Reservation.reservation_code == reservation_code)
        if reservation_number:
            query = query.filter(Reservation.reservation_number == reservation_number)

        # 获取预定信息（用于邮件发送）
        db_reservation = query.first()
        if not db_reservation:
            error_msg = f"[API错误] 预定不存在: 预约码={reservation_code}" + (f", 预约序号={reservation_number}" if reservation_number else "")
            logger.error(error_msg)
            return {"success": False, "message": "预定不存在"}

        # 检查预定是否已取消
        if db_reservation.status == "cancelled":
            logger.info(f"[API验证] 预定已取消: 预约码={reservation_code}, ID={db_reservation.id}, 预约序号={db_reservation.reservation_number}")
            return {"success": False, "message": "预定已取消"}

        # 获取设备信息
        equipment = get_equipment(db, db_reservation.equipment_id)
        logger.info(f"[API信息] 设备信息: ID={equipment.id if equipment else 'None'}, 名称={equipment.name if equipment else 'None'}")

        # 记录取消前的状态
        logger.info(f"[API状态] 取消预约前状态: 预约码={reservation_code}, ID={db_reservation.id}, 预约序号={db_reservation.reservation_number}, 状态={db_reservation.status}")

        # 取消预定
        success, message = cancel_reservation(db, reservation_code, reservation_number)
        logger.info(f"[API结果] 取消预约结果: 成功={success}, 消息={message}")

        # 记录取消后的状态
        if success:
            # 重新获取预约以确认状态已更新
            updated_query = db.query(Reservation).filter(Reservation.reservation_code == reservation_code)
            if reservation_number:
                updated_query = updated_query.filter(Reservation.reservation_number == reservation_number)
            updated_reservation = updated_query.first()

            logger.info(f"[API验证] 取消预约后状态: 预约码={reservation_code}, ID={updated_reservation.id if updated_reservation else 'None'}, 预约序号={updated_reservation.reservation_number if updated_reservation else 'None'}, 状态={updated_reservation.status if updated_reservation else 'unknown'}")
        else:
            logger.error(f"[API错误] 取消预约失败: 预约码={reservation_code}, 消息={message}")

        # 如果取消成功且提供了邮箱，发送取消确认邮件
        if success and (user_email or db_reservation.user_email):
            # 创建基本邮件数据
            email_data = {
                "user_name": db_reservation.user_name,
                "reservation_code": db_reservation.reservation_code,
                "reservation_number": db_reservation.reservation_number,
                "equipment_name": equipment.name if equipment else "",
                "equipment_category": equipment.category if equipment else "",
                "location": equipment.location if equipment else "",
                "start_datetime": format_datetime(db_reservation.start_datetime),
                "end_datetime": format_datetime(db_reservation.end_datetime),
                "purpose": db_reservation.purpose,
                "description": equipment.description,
                "site_url": "http://localhost:8000",  # 应该从配置中获取
                "status": "已取消 / Cancelled",
                "recurring_reservation_id": getattr(db_reservation, 'recurring_reservation_id', None),
                "pattern_type": getattr(db_reservation, 'pattern_type', None)
            }

            # 判断是否为循环预约的子预约
            if getattr(db_reservation, 'recurring_reservation_id', None):
                # 获取父循环预约信息
                parent_info = None
                try:
                    from backend.routes.crud.recurring_reservation import get_recurring_reservation
                    parent_recurring = get_recurring_reservation(db, db_reservation.recurring_reservation_id)
                    if parent_recurring:
                        parent_info = {
                            "reservation_code": parent_recurring.reservation_code,
                            "equipment_name": equipment.name if equipment else "",
                            "pattern_type": parent_recurring.pattern_type,
                            "start_datetime": format_datetime(parent_recurring.start_date),
                            "end_datetime": format_datetime(parent_recurring.end_date),
                            "status": parent_recurring.status
                        }
                        logger.info(f"[API邮件] 找到父循环预约信息: ID={parent_recurring.id}, 预约码={parent_recurring.reservation_code}")
                except Exception as e:
                    logger.error(f"[API邮件] 获取父循环预约信息失败: {str(e)}")

                # 发送循环子预约取消邮件
                await send_reservation_cancellation(
                    to_email=user_email or db_reservation.user_email,
                    reservation_data=email_data,
                    lang=lang,
                    db=db,
                    is_recurring=True,
                    is_child=True,
                    parent_info=parent_info
                )
                logger.info(f"[API邮件] 发送循环子预约取消邮件: 收件人={user_email or db_reservation.user_email}")
            elif getattr(db_reservation, 'pattern_type', None):
                # 循环父预约
                await send_reservation_cancellation(
                    to_email=user_email or db_reservation.user_email,
                    reservation_data=email_data,
                    lang=lang,
                    db=db,
                    is_recurring=True,
                    is_child=False
                )
                logger.info(f"[API邮件] 发送循环预约取消邮件: 收件人={user_email or db_reservation.user_email}")
            else:
                # 单次预约
                await send_reservation_cancellation(
                    to_email=user_email or db_reservation.user_email,
                    reservation_data=email_data,
                    lang=lang,
                    db=db
                )
                logger.info(f"[API邮件] 发送单次预约取消邮件: 收件人={user_email or db_reservation.user_email}")
        try:
            logger.info(f"[API邮件] 取消确认邮件发送成功")
        except Exception as email_error:
            logger.error(f"[API邮件] 发送取消确认邮件失败: {str(email_error)}")

        return {"success": success, "message": message}
    except Exception as e:
        logger.error(f"[API错误] 取消预约出错: {str(e)}")
        logger.error(f"[API错误] 错误详情: {traceback.format_exc()}")
        return {"success": False, "message": f"取消预约时发生错误: {str(e)}"}

        raise HTTPException(status_code=500, detail=f"获取预定二维码出错: {str(e)}")
