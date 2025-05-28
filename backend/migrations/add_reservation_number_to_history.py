"""
为 reservation_history 表添加 reservation_number 字段的迁移脚本
Migration script to add reservation_number field to reservation_history table
"""
import logging
from sqlalchemy import text
from backend.database import engine, SessionLocal

# 设置日志
logger = logging.getLogger(__name__)

def run_migration():
    """
    运行迁移脚本
    Run migration script
    """
    try:
        # 创建数据库会话
        db = SessionLocal()
        
        # 检查 reservation_number 字段是否已存在
        check_sql = """
        PRAGMA table_info(reservation_history);
        """
        result = db.execute(text(check_sql)).fetchall()
        column_names = [row[1] for row in result]
        
        if 'reservation_number' in column_names:
            logger.info("reservation_number 字段已存在，跳过迁移")
            return
        
        # 添加 reservation_number 字段
        alter_sql = """
        ALTER TABLE reservation_history ADD COLUMN reservation_number VARCHAR(20);
        """
        db.execute(text(alter_sql))
        
        # 创建索引
        index_sql = """
        CREATE INDEX ix_reservation_history_reservation_number ON reservation_history (reservation_number);
        """
        db.execute(text(index_sql))
        
        # 更新现有记录的 reservation_number 字段
        update_sql = """
        UPDATE reservation_history
        SET reservation_number = (
            SELECT reservation_number
            FROM reservation
            WHERE reservation.id = reservation_history.reservation_id
        )
        """
        db.execute(text(update_sql))
        
        # 提交事务
        db.commit()
        
        logger.info("成功为 reservation_history 表添加 reservation_number 字段")
    except Exception as e:
        logger.error(f"迁移失败: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    run_migration()
