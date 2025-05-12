"""
预约状态更新工具
Reservation status update utility
"""
import logging
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.models.reservation import Reservation

logger = logging.getLogger(__name__)

def update_reservation_statuses(db: Session):
    """
    更新所有预约状态:
    1. 已确认 -> 使用中（如果已经开始但未结束）
    2. 已确认/使用中 -> 已过期（如果已经结束）

    Update all reservation statuses:
    1. confirmed -> in_use (if started but not ended)
    2. confirmed/in_use -> expired (if already ended)

    优化版本：使用批量更新而不是逐条更新，减少数据库操作次数
    """
    try:
        now = datetime.now()
        logger.info(f"当前时间: {now}")

        # 记录当前时间的详细信息，用于调试
        logger.info(f"当前时间详细信息: 年={now.year}, 月={now.month}, 日={now.day}, 时={now.hour}, 分={now.minute}, 秒={now.second}")

        # 查找并记录一些预约的日期时间格式，用于调试
        sample_reservations = db.query(
            Reservation.id,
            Reservation.reservation_number,
            Reservation.start_datetime,
            Reservation.end_datetime,
            Reservation.status
        ).order_by(Reservation.id.desc()).limit(5).all()

        # logger.info("数据库中的日期时间格式示例:")
        # for res in sample_reservations:
        #     logger.info(f"ID: {res.id}, 预约序号: {res.reservation_number}, 状态: {res.status}, "
        #                f"开始时间类型: {type(res.start_datetime)}, 开始时间: {res.start_datetime}, "
        #                f"结束时间类型: {type(res.end_datetime)}, 结束时间: {res.end_datetime}")

        #     # 检查日期时间是否为字符串类型，这可能导致比较问题
        #     if isinstance(res.start_datetime, str) or isinstance(res.end_datetime, str):
        #         logger.warning(f"预约ID: {res.id} 的日期时间是字符串类型，这可能导致比较问题")

        # 查找应该更新为"使用中"的预约
        logger.info("执行查询：查找应该更新为'使用中'的预约")
        logger.info(f"SQL查询条件: Reservation.status == 'confirmed' AND "
                   f"Reservation.start_datetime <= {now} AND Reservation.end_datetime > {now}")

        # 使用try-except块来捕获可能的日期时间比较错误
        try:
            in_use_candidates = db.query(Reservation).filter(
                Reservation.status == "confirmed",
                Reservation.start_datetime <= now,
                Reservation.end_datetime > now
            ).all()

            logger.info(f"找到 {len(in_use_candidates)} 个应该更新为'使用中'的预约")
            for res in in_use_candidates:
                logger.info(f"预约ID: {res.id}, 开始时间: {res.start_datetime}, 结束时间: {res.end_datetime}, 当前状态: {res.status}")

                # 检查日期时间是否合理
                try:
                    start_diff = (now - res.start_datetime).total_seconds()
                    end_diff = (res.end_datetime - now).total_seconds()
                    logger.info(f"预约ID: {res.id}, 当前时间与开始时间的差值(秒): {start_diff}, "
                               f"结束时间与当前时间的差值(秒): {end_diff}")

                    # 验证时间差值是否合理
                    if start_diff < 0 or end_diff <= 0:
                        logger.warning(f"预约ID: {res.id} 的时间差值不合理，跳过更新")
                        continue
                except Exception as e:
                    logger.error(f"计算预约ID: {res.id} 的时间差值时出错: {str(e)}")
                    continue
        except Exception as e:
            logger.error(f"查询应该更新为'使用中'的预约时出错: {str(e)}")
            in_use_candidates = []

        # 查找应该更新为"已过期"的预约
        logger.info("执行查询：查找应该更新为'已过期'的预约")
        logger.info(f"SQL查询条件: Reservation.status.in_(['confirmed', 'in_use']) AND Reservation.end_datetime <= {now}")

        # 使用try-except块来捕获可能的日期时间比较错误
        try:
            expired_candidates = db.query(Reservation).filter(
                Reservation.status.in_(["confirmed", "in_use"]),
                Reservation.end_datetime <= now
            ).all()

            logger.info(f"找到 {len(expired_candidates)} 个应该更新为'已过期'的预约")
            for res in expired_candidates:
                logger.info(f"预约ID: {res.id}, 开始时间: {res.start_datetime}, 结束时间: {res.end_datetime}, 当前状态: {res.status}")

                # 检查日期时间是否合理
                try:
                    time_diff = (res.end_datetime - now).total_seconds()
                    logger.info(f"预约ID: {res.id}, 结束时间与当前时间的差值(秒): {time_diff}")

                    # 验证时间差值是否合理
                    if time_diff > 0:
                        logger.warning(f"预约ID: {res.id} 的结束时间尚未到达，跳过更新")
                        continue
                except Exception as e:
                    logger.error(f"计算预约ID: {res.id} 的时间差值时出错: {str(e)}")
                    continue
        except Exception as e:
            logger.error(f"查询应该更新为'已过期'的预约时出错: {str(e)}")
            expired_candidates = []

        # 使用批量更新 - 将已确认但已开始的预约更新为"使用中"
        # 只更新通过了上面验证的预约
        in_use_ids = [res.id for res in in_use_candidates]
        if in_use_ids:
            in_use_result = db.query(Reservation).filter(
                Reservation.id.in_(in_use_ids)
            ).update({"status": "in_use"}, synchronize_session=False)
        else:
            in_use_result = 0

        # 使用批量更新 - 将已确认或使用中但已结束的预约更新为"已过期"
        # 只更新通过了上面验证的预约
        expired_ids = [res.id for res in expired_candidates]
        if expired_ids:
            logger.info(f"执行SQL更新: 将ID在 {expired_ids} 中的预约状态更新为'已过期'")
            expired_result = db.query(Reservation).filter(
                Reservation.id.in_(expired_ids)
            ).update({"status": "expired"}, synchronize_session=False)
        else:
            expired_result = 0

        # 记录更新结果
        logger.info(f"ORM更新结果: 使用中={in_use_result}条, 已过期={expired_result}条")

        # 提交更改
        if in_use_result > 0 or expired_result > 0:
            db.commit()
            logger.info(f"已更新预约状态: {in_use_result}个更新为'使用中', {expired_result}个更新为'已过期'")

            # 记录更新后的预约状态，用于验证
            if expired_ids:
                updated_reservations = db.query(
                    Reservation.id,
                    Reservation.reservation_number,
                    Reservation.status,
                    Reservation.start_datetime,
                    Reservation.end_datetime
                ).filter(Reservation.id.in_(expired_ids)).all()

                logger.info("更新后的预约状态:")
                for res in updated_reservations:
                    logger.info(f"ID: {res.id}, 预约序号: {res.reservation_number}, 状态: {res.status}, "
                               f"开始时间: {res.start_datetime}, 结束时间: {res.end_datetime}")
        else:
            logger.info("没有预约需要更新状态")

        return True
    except Exception as e:
        db.rollback()
        logger.error(f"更新预约状态时出错: {str(e)}")
        logger.exception("详细错误信息:")
        return False