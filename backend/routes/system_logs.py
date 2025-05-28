"""
系统日志API路由
System log API routes
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta

from backend.database import get_db
from backend.models.system_log import SystemLog
from backend.schemas.system_log import SystemLogOut, PaginatedSystemLogs
from backend.routes.auth import get_current_admin
from backend.services.log_service import log_operation

# 设置日志
logger = logging.getLogger(__name__)

# 创建路由
router = APIRouter(
    prefix="/api/system/logs",
    tags=["system_logs"],
    dependencies=[Depends(get_current_admin)]
)

@router.get("/", response_model=PaginatedSystemLogs)
async def get_system_logs(
    skip: int = 0,
    limit: int = 20,
    user_type: Optional[str] = None,
    user_id: Optional[str] = None,
    action: Optional[str] = None,
    module: Optional[str] = None,
    status: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """获取系统日志列表"""
    query = db.query(SystemLog)

    # 应用过滤条件
    if user_type:
        query = query.filter(SystemLog.user_type == user_type)
    if user_id:
        query = query.filter(SystemLog.user_id.ilike(f"%{user_id}%"))
    if action:
        query = query.filter(SystemLog.action == action)
    if module:
        query = query.filter(SystemLog.module == module)
    if status:
        query = query.filter(SystemLog.status == status)
    
    # 日期过滤
    if from_date:
        try:
            from_datetime = datetime.strptime(from_date, "%Y-%m-%d")
            query = query.filter(SystemLog.created_at >= from_datetime)
        except ValueError:
            pass
    
    if to_date:
        try:
            to_datetime = datetime.strptime(to_date, "%Y-%m-%d")
            to_datetime = to_datetime.replace(hour=23, minute=59, second=59)
            query = query.filter(SystemLog.created_at <= to_datetime)
        except ValueError:
            pass

    # 获取总数
    total = query.count()

    # 应用分页并按创建时间降序排序
    logs = query.order_by(desc(SystemLog.created_at)).offset(skip).limit(limit).all()

    return {"items": logs, "total": total}

@router.delete("/")
async def clear_system_logs(
    days: Optional[int] = Query(None, description="清除多少天前的日志，不提供则清除所有"),
    user_type: Optional[str] = Query(None, description="要清除的用户类型，例如 'admin'或'user'"),
    module: Optional[str] = Query(None, description="要清除的模块，例如 'equipment'或'reservation'"),
    status: Optional[str] = Query(None, description="要清除的日志状态，例如 'success'或'failed'"),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """清除系统日志"""
    # 验证当前用户是否为超级管理员
    if current_admin.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有超级管理员可以清除系统日志"
        )

    query = db.query(SystemLog)

    # 应用过滤条件
    if days:
        cutoff_date = datetime.now() - timedelta(days=days)
        query = query.filter(SystemLog.created_at < cutoff_date)

    if user_type:
        query = query.filter(SystemLog.user_type == user_type)

    if module:
        query = query.filter(SystemLog.module == module)

    if status:
        query = query.filter(SystemLog.status == status)

    # 获取要删除的日志数量
    count = query.count()

    try:
        # 删除日志
        query.delete(synchronize_session=False)
        db.commit()

        # 记录清理日志
        await log_operation(
            db=db,
            user_type="admin",
            user_id=current_admin.username,
            user_name=current_admin.name,
            action="delete",
            module="system",
            description=f"管理员 {current_admin.name} 清除了 {count} 条系统日志",
            status="success",
            details={
                "days": days,
                "user_type": user_type,
                "module": module,
                "status": status,
                "count": count
            }
        )

        return {"message": f"成功清除 {count} 条系统日志"}
    except Exception as e:
        db.rollback()
        logger.error(f"清除系统日志失败: {e}")
        raise HTTPException(status_code=500, detail=f"清除系统日志失败: {e}")
