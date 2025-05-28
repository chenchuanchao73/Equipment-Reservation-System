"""
日志服务
Log service
"""
import logging
import json
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from backend.models.system_log import SystemLog

# 设置日志
logger = logging.getLogger(__name__)

async def log_operation(
    db: Session,
    user_type: str,
    user_id: Optional[str],
    user_name: Optional[str],
    action: str,
    module: str,
    description: str,
    ip_address: Optional[str] = None,
    status: str = "success",
    error_message: Optional[str] = None,
    target_id: Optional[str] = None,
    target_type: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """
    记录操作日志
    Log operation
    """
    try:
        # 将details转换为JSON字符串
        details_json = None
        if details:
            try:
                details_json = json.dumps(details, ensure_ascii=False, default=str)
            except Exception as e:
                logger.error(f"转换日志详情为JSON失败: {e}")
                details_json = str(details)

        # 创建日志记录
        log = SystemLog(
            user_type=user_type,
            user_id=user_id,
            user_name=user_name,
            action=action,
            module=module,
            description=description,
            ip_address=ip_address,
            status=status,
            error_message=error_message,
            target_id=target_id,
            target_type=target_type,
            details=details_json
        )
        db.add(log)
        db.commit()
        logger.info(f"操作日志已记录: {description}")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"记录操作日志失败: {e}")
        return False
