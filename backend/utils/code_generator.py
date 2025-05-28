"""
预定码生成器
Reservation code generator
"""
import random
import string
import logging
from datetime import datetime
import time

# 设置日志
logger = logging.getLogger(__name__)

def generate_random_code(length=8):
    """
    生成随机码
    Generate random code
    """
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def generate_reservation_code(length=8):
    """
    生成预约码
    Generate reservation code
    """
    return generate_random_code(length)

def generate_reservation_number(db=None):
    """
    生成预约编号
    Generate reservation number

    格式：RN-YYYYMMDD-####（例如：RN-20220101-0001）
    Format: RN-YYYYMMDD-#### (e.g., RN-20220101-0001)
    """
    # 获取当前日期
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")

    # 生成基础编号
    prefix = f"RN-{date_str}-"

    # 如果提供了数据库连接，检查是否已存在同名编号
    if db:
        from backend.models.reservation import Reservation
        # 查找今天已存在的最大编号
        last_reservation = db.query(Reservation).filter(
            Reservation.reservation_number.like(f"{prefix}%")
        ).order_by(Reservation.reservation_number.desc()).first()

        if last_reservation:
            try:
                last_number = int(last_reservation.reservation_number.split('-')[-1])
                new_number = last_number + 1
            except (ValueError, IndexError):
                # 如果解析出错，使用时间戳和随机数生成唯一编号
                new_number = int(time.time() * 1000) % 10000 + random.randint(1, 999)
        else:
            # 如果没有找到今天的预约，从1000开始
            new_number = 1000
    else:
        # 如果没有提供数据库连接，使用时间戳和随机数生成唯一编号
        timestamp = int(time.time() * 1000) % 10000  # 获取毫秒级时间戳后4位
        random_part = random.randint(1, 999)  # 1-999的随机数
        new_number = timestamp + random_part

    # 确保编号至少是4位数
    if new_number < 1000:
        new_number += 1000

    # 生成完整的预约序号
    reservation_number = f"{prefix}{new_number}"

    # 添加查重机制：如果提供了数据库连接，检查生成的序号是否已存在
    if db:
        from backend.models.reservation import Reservation

        # 最多尝试10次生成唯一序号
        max_attempts = 10
        attempt = 1

        while attempt <= max_attempts:
            # 检查序号是否已存在
            existing = db.query(Reservation).filter(
                Reservation.reservation_number == reservation_number
            ).first()

            if not existing:
                # 序号不存在，可以使用
                break

            # 序号已存在，生成新的序号
            logger.warning(f"预约序号 {reservation_number} 已存在，尝试生成新序号 (尝试 {attempt}/{max_attempts})")

            # 使用时间戳和随机数生成新序号
            timestamp = int(time.time() * 1000) % 10000
            random_part = random.randint(1000, 9999)
            new_number = timestamp + random_part

            # 确保编号至少是4位数
            if new_number < 1000:
                new_number += 1000

            # 生成新的预约序号
            reservation_number = f"{prefix}{new_number}"
            attempt += 1

        if attempt > max_attempts:
            # 如果尝试多次仍未生成唯一序号，使用更复杂的方式生成
            logger.error(f"无法生成唯一预约序号，使用备用方法")
            timestamp = int(time.time() * 1000000) % 1000000  # 使用微秒级时间戳
            random_part = random.randint(1000, 9999)
            reservation_number = f"{prefix}{timestamp}-{random_part}"

    # 记录生成的编号，用于调试
    logger.info(f"生成预约编号: {reservation_number}")

    return reservation_number

def generate_recurring_reservation_number(current_date, index, base_number=None, db=None):
    """
    生成循环预约的子预约编号
    Generate reservation number for a child reservation in a recurring series

    格式：RN-YYYYMMDD-XXXX-N（例如：RN-20220101-8901-1）
    Format: RN-YYYYMMDD-XXXX-N (e.g., RN-20220101-8901-1)

    参数:
    current_date: 预约日期
    index: 子预约序号
    base_number: 基础编号，如果为None且index=1，则生成新的基础编号；否则必须提供
    db: 数据库会话，用于检查编号唯一性
    """
    # 获取日期字符串
    date_str = current_date.strftime("%Y%m%d")

    # 生成基础编号(第一次调用时生成，序号相同的预约共享此编号)
    if index == 1 and base_number is None:
        # 生成一个随机的基础编号
        base_number = random.randint(1000, 9999)
    elif base_number is None:
        # 如果不是第一个子预约，且没有提供基础编号，使用随机数但记录警告
        base_number = random.randint(1000, 9999)
        logger.warning(f"非第一个子预约没有提供基础编号，使用随机生成: {base_number}")

    # 格式: RN-YYYYMMDD-XXXX-N
    reservation_number = f"RN-{date_str}-{base_number}-{index}"

    # 添加查重机制：如果提供了数据库连接，检查生成的序号是否已存在
    if db:
        from backend.models.reservation import Reservation

        # 最多尝试10次生成唯一序号
        max_attempts = 10
        attempt = 1

        while attempt <= max_attempts:
            # 检查序号是否已存在
            existing = db.query(Reservation).filter(
                Reservation.reservation_number == reservation_number
            ).first()

            if not existing:
                # 序号不存在，可以使用
                break

            # 序号已存在，生成新的序号
            logger.warning(f"循环预约序号 {reservation_number} 已存在，尝试生成新序号 (尝试 {attempt}/{max_attempts})")

            # 为避免与其他子预约冲突，增加基础编号
            base_number = random.randint(1000, 9999)

            # 生成新的预约序号
            reservation_number = f"RN-{date_str}-{base_number}-{index}"
            attempt += 1

        if attempt > max_attempts:
            # 如果尝试多次仍未生成唯一序号，使用更复杂的方式生成
            logger.error(f"无法生成唯一循环预约序号，使用备用方法")
            timestamp = int(time.time() * 1000) % 10000
            random_part = random.randint(1000, 9999)
            reservation_number = f"RN-{date_str}-{timestamp}-{random_part}-{index}"

    # 记录生成的编号，用于调试
    logger.info(f"生成循环预约子预约编号: {reservation_number}")

    return reservation_number, base_number

# 注意：以下QRCode相关函数已弃用，保留函数签名但返回空值，以避免调用处出错

def generate_equipment_qrcode(equipment_id, equipment_name):  # pylint: disable=unused-argument
    """
    生成设备二维码（已弃用）
    Generate equipment QR code (deprecated)
    """
    logger.warning("generate_equipment_qrcode函数已弃用")
    return None

def generate_multi_function_qrcode(item_type, item_id, data):  # pylint: disable=unused-argument
    """
    生成多功能二维码（已弃用）
    Generate multi-function QR code (deprecated)
    """
    logger.warning("generate_multi_function_qrcode函数已弃用")
    return None
