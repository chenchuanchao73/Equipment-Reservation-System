"""
统计相关路由
Statistics routes
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from backend.database import get_db
from backend.models.equipment import Equipment
from backend.models.reservation import Reservation
from backend.routes.auth import get_current_admin

# 设置日志
logger = logging.getLogger(__name__)

# 创建路由
router = APIRouter(
    prefix="/api/statistics",
    tags=["statistics"],
    dependencies=[Depends(get_current_admin)]
)

@router.get("/dashboard")
async def get_dashboard_statistics(
    db: Session = Depends(get_db)
):
    """
    获取仪表盘统计数据
    Get dashboard statistics
    """
    try:
        # 获取设备总数
        total_equipment = db.query(func.count(Equipment.id)).scalar()

        # 获取可用设备数量
        available_equipment = db.query(func.count(Equipment.id)).filter(
            Equipment.status == "available"
        ).scalar()

        # 获取预定总数
        total_reservation = db.query(func.count(Reservation.id)).scalar()

        # 获取活跃预定数量（状态为confirmed且未结束的预定）
        active_reservation = db.query(func.count(Reservation.id)).filter(
            Reservation.status == "confirmed",
            Reservation.end_datetime > datetime.now()
        ).scalar()

        # 获取最近预定
        recent_reservations = db.query(Reservation).order_by(
            Reservation.created_at.desc()
        ).limit(10).all()

        # 构建响应数据
        return {
            "total_equipment": total_equipment,
            "available_equipment": available_equipment,
            "total_reservation": total_reservation,
            "active_reservation": active_reservation,
            "recent_reservations": [
                {
                    "id": reservation.id,
                    "reservation_number": reservation.reservation_number,
                    "reservation_code": reservation.reservation_code,
                    "equipment_id": reservation.equipment_id,
                    "equipment_name": reservation.equipment.name if reservation.equipment else None,
                    "user_name": reservation.user_name,
                    "user_department": reservation.user_department,
                    "user_contact": reservation.user_contact,
                    "start_datetime": reservation.start_datetime,
                    "end_datetime": reservation.end_datetime,
                    "status": reservation.status,
                    "created_at": reservation.created_at
                }
                for reservation in recent_reservations
            ]
        }
    except Exception as e:
        logger.error(f"获取仪表盘统计数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取仪表盘统计数据失败: {str(e)}")

@router.get("/equipment-usage")
async def get_equipment_usage(
    time_range: str = Query("week", description="时间范围: week, month, year"),
    category: Optional[str] = Query(None, description="设备类别"),
    db: Session = Depends(get_db)
):
    """
    获取设备使用率统计
    Get equipment usage statistics
    """
    try:
        # 根据时间范围确定开始日期
        now = datetime.now()
        if time_range == "week":
            start_date = now - timedelta(days=7)
            date_format = "%Y-%m-%d"
            interval = "day"
        elif time_range == "month":
            start_date = now - timedelta(days=30)
            date_format = "%Y-%m-%d"
            interval = "day"
        elif time_range == "year":
            start_date = now - timedelta(days=365)
            date_format = "%Y-%m"
            interval = "month"
        else:
            start_date = now - timedelta(days=7)
            date_format = "%Y-%m-%d"
            interval = "day"

        # 构建查询条件
        query_filter = [Reservation.start_datetime >= start_date]
        if category:
            # 联合查询设备表，按类别筛选
            equipment_ids = db.query(Equipment.id).filter(
                Equipment.category == category
            ).all()
            equipment_ids = [id[0] for id in equipment_ids]
            query_filter.append(Reservation.equipment_id.in_(equipment_ids))

        # 获取预定数据
        reservations = db.query(Reservation).filter(*query_filter).all()

        # 按日期分组统计
        date_stats = {}
        for reservation in reservations:
            # 根据时间间隔格式化日期
            if interval == "day":
                date_key = reservation.start_datetime.strftime(date_format)
            else:
                date_key = reservation.start_datetime.strftime(date_format)

            if date_key not in date_stats:
                date_stats[date_key] = 0

            date_stats[date_key] += 1

        # 生成日期范围
        date_range = []
        if interval == "day":
            delta = timedelta(days=1)
            current = start_date
            while current <= now:
                date_range.append(current.strftime(date_format))
                current += delta
        else:
            # 按月生成日期范围
            current_month = start_date.replace(day=1)
            while current_month <= now:
                date_range.append(current_month.strftime(date_format))
                # 移动到下个月
                if current_month.month == 12:
                    current_month = current_month.replace(year=current_month.year + 1, month=1)
                else:
                    current_month = current_month.replace(month=current_month.month + 1)

        # 填充缺失的日期数据
        for date in date_range:
            if date not in date_stats:
                date_stats[date] = 0

        # 排序日期
        sorted_dates = sorted(date_stats.keys())

        # 构建图表数据
        chart_data = {
            "labels": sorted_dates,
            "datasets": [
                {
                    "label": "预定数量",
                    "data": [date_stats[date] for date in sorted_dates],
                    "backgroundColor": "rgba(64, 158, 255, 0.2)",
                    "borderColor": "rgba(64, 158, 255, 1)",
                    "borderWidth": 1,
                    "fill": True
                }
            ]
        }

        return chart_data
    except Exception as e:
        logger.error(f"获取设备使用率统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取设备使用率统计失败: {str(e)}")

@router.get("/category-distribution")
async def get_category_distribution(
    db: Session = Depends(get_db)
):
    """
    获取设备类别分布统计
    Get equipment category distribution statistics
    """
    try:
        # 按类别统计设备数量
        category_stats = db.query(
            Equipment.category,
            func.count(Equipment.id).label("count")
        ).group_by(Equipment.category).all()

        # 构建图表数据
        labels = [stat[0] for stat in category_stats]
        data = [stat[1] for stat in category_stats]

        # 生成颜色
        colors = [
            "rgba(64, 158, 255, 0.7)",  # 蓝色
            "rgba(103, 194, 58, 0.7)",  # 绿色
            "rgba(230, 162, 60, 0.7)",  # 黄色
            "rgba(245, 108, 108, 0.7)",  # 红色
            "rgba(144, 147, 153, 0.7)",  # 灰色
            "rgba(78, 110, 242, 0.7)",  # 紫色
            "rgba(34, 187, 204, 0.7)",  # 青色
            "rgba(252, 141, 89, 0.7)"   # 橙色
        ]

        # 如果类别数量超过颜色数量，循环使用颜色
        background_colors = []
        for i in range(len(labels)):
            background_colors.append(colors[i % len(colors)])

        chart_data = {
            "labels": labels,
            "datasets": [
                {
                    "label": "设备数量",
                    "data": data,
                    "backgroundColor": background_colors
                }
            ]
        }

        return chart_data
    except Exception as e:
        logger.error(f"获取设备类别分布统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取设备类别分布统计失败: {str(e)}")

@router.get("/reservation-status")
async def get_reservation_status(
    time_range: str = Query("week", description="时间范围: week, month, year"),
    db: Session = Depends(get_db)
):
    """
    获取预定状态统计
    Get reservation status statistics
    """
    try:
        # 根据时间范围确定开始日期
        now = datetime.now()
        if time_range == "week":
            start_date = now - timedelta(days=7)
        elif time_range == "month":
            start_date = now - timedelta(days=30)
        elif time_range == "year":
            start_date = now - timedelta(days=365)
        else:
            start_date = now - timedelta(days=7)

        # 按状态统计预定数量
        status_stats = db.query(
            Reservation.status,
            func.count(Reservation.id).label("count")
        ).filter(
            Reservation.created_at >= start_date
        ).group_by(Reservation.status).all()

        # 构建图表数据
        status_map = {
            "confirmed": "已确认",
            "cancelled": "已取消",
            "completed": "已完成"
        }

        labels = [status_map.get(stat[0], stat[0]) for stat in status_stats]
        data = [stat[1] for stat in status_stats]

        # 生成颜色
        colors = [
            "rgba(103, 194, 58, 0.7)",  # 绿色 - 已确认
            "rgba(144, 147, 153, 0.7)",  # 灰色 - 已取消
            "rgba(64, 158, 255, 0.7)"    # 蓝色 - 已完成
        ]

        chart_data = {
            "labels": labels,
            "datasets": [
                {
                    "label": "预定数量",
                    "data": data,
                    "backgroundColor": colors[:len(labels)]
                }
            ]
        }

        return chart_data
    except Exception as e:
        logger.error(f"获取预定状态统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取预定状态统计失败: {str(e)}")

@router.get("/popular-equipment")
async def get_popular_equipment(
    time_range: str = Query("month", description="时间范围: week, month, year"),
    limit: int = Query(5, description="返回数量"),
    db: Session = Depends(get_db)
):
    """
    获取热门设备统计
    Get popular equipment statistics
    """
    try:
        # 根据时间范围确定开始日期
        now = datetime.now()
        if time_range == "week":
            start_date = now - timedelta(days=7)
        elif time_range == "month":
            start_date = now - timedelta(days=30)
        elif time_range == "year":
            start_date = now - timedelta(days=365)
        else:
            start_date = now - timedelta(days=30)

        # 统计每个设备的预定次数
        equipment_stats = db.query(
            Reservation.equipment_id,
            func.count(Reservation.id).label("count")
        ).filter(
            Reservation.created_at >= start_date,
            Reservation.status != "cancelled"  # 排除已取消的预定
        ).group_by(Reservation.equipment_id).order_by(
            func.count(Reservation.id).desc()
        ).limit(limit).all()

        # 获取设备详情
        equipment_ids = [stat[0] for stat in equipment_stats]
        equipments = db.query(Equipment).filter(Equipment.id.in_(equipment_ids)).all()

        # 构建设备ID到名称的映射
        equipment_map = {equipment.id: equipment.name for equipment in equipments}

        # 构建图表数据
        labels = [equipment_map.get(stat[0], f"设备 {stat[0]}") for stat in equipment_stats]
        data = [stat[1] for stat in equipment_stats]

        # 生成颜色
        colors = [
            "rgba(64, 158, 255, 0.7)",  # 蓝色
            "rgba(103, 194, 58, 0.7)",  # 绿色
            "rgba(230, 162, 60, 0.7)",  # 黄色
            "rgba(245, 108, 108, 0.7)",  # 红色
            "rgba(144, 147, 153, 0.7)"   # 灰色
        ]

        chart_data = {
            "labels": labels,
            "datasets": [
                {
                    "label": "预定次数",
                    "data": data,
                    "backgroundColor": colors[:len(labels)]
                }
            ]
        }

        return chart_data
    except Exception as e:
        logger.error(f"获取热门设备统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取热门设备统计失败: {str(e)}")
