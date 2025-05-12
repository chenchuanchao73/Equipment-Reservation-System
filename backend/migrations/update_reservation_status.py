"""
更新预约状态字段，增加"使用中"和"已过期"状态
Update reservation status field to add "in_use" and "expired" states
"""
import logging
from datetime import datetime
from sqlalchemy import text

logger = logging.getLogger(__name__)

def upgrade(conn):
    """
    升级数据库
    Upgrade database
    """
    try:
        logger.info("开始更新预约状态...")
        
        # 获取当前时间
        now = datetime.now()
        
        # 更新所有已确认但已经开始的预约为"使用中"
        conn.execute(text("""
            UPDATE reservation 
            SET status = 'in_use' 
            WHERE status = 'confirmed' 
            AND start_datetime <= :now 
            AND end_datetime > :now
        """), {"now": now})
        
        # 更新所有已确认但已经结束的预约为"已过期"
        conn.execute(text("""
            UPDATE reservation 
            SET status = 'expired' 
            WHERE status = 'confirmed' 
            AND end_datetime <= :now
        """), {"now": now})
        
        logger.info("预约状态更新完成")
        return True
    except Exception as e:
        logger.error(f"更新预约状态时出错: {str(e)}")
        return False

def downgrade(conn):
    """
    回滚数据库
    Downgrade database
    """
    try:
        # 将所有非"cancelled"状态的预约恢复为"confirmed"
        conn.execute(text("""
            UPDATE reservation 
            SET status = 'confirmed' 
            WHERE status IN ('in_use', 'expired')
        """))
        return True
    except Exception as e:
        logger.error(f"回滚预约状态时出错: {str(e)}")
        return False