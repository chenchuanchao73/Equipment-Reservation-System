from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from backend.database import get_db
from backend.models.reservation import Reservation
from backend.models.equipment import Equipment
from backend.routes.crud.equipment import get_equipment
import logging

logger = logging.getLogger(__name__)
router = APIRouter(
    tags=["calendar"],
)

@router.get("/api/reservations/calendar")
async def get_calendar_reservations(
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db)
):
    """
    获取日历视图的预约数据
    Get reservation data for calendar view
    """
    try:
        # 转换日期字符串为日期对象
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        # 构建查询 - 包括普通预约和循环预约的子预约
        query = db.query(Reservation).filter(
            Reservation.start_datetime >= start,
            Reservation.end_datetime <= end,
            Reservation.status.in_(["confirmed", "in_use"])  # 显示已确认和使用中的预约
        )

        reservations = query.all()

        # 转换为日历事件格式
        events = []
        for res in reservations:
            equipment = get_equipment(db, res.equipment_id)

            # 确定事件颜色 - 基于状态
            color = "blue" if res.status == "in_use" else "green"


            # 构建事件标题 - 包含设备名称
            title = equipment.name

            # 检查是否为循环预约的子预约
            is_recurring = res.recurring_reservation_id is not None

            events.append({
                "id": res.id,
                "title": title,
                "start": res.start_datetime.isoformat(),
                "end": res.end_datetime.isoformat(),
                "color": color,
                "borderColor": "#ff9800" if is_recurring else color,  # 循环预约使用特殊边框
                "extendedProps": {
                    "status": res.status,
                    "userName": res.user_name,
                    "userDepartment": res.user_department,
                    "equipmentId": res.equipment_id,
                    "reservationCode": res.reservation_code,
                    "reservationNumber": res.reservation_number,
                    "isRecurring": is_recurring,
                    "recurringReservationId": res.recurring_reservation_id
                }
            })

        return {"success": True, "events": events}
    except Exception as e:
        logger.error(f"获取日历数据出错: {str(e)}")
        return {"success": False, "message": str(e)}
