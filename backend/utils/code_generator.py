"""
预定码生成器
Reservation code generator
"""
import random
import string
import logging
import os
from pathlib import Path
from datetime import datetime

# 设置日志
logger = logging.getLogger(__name__)

# 导入配置
from config import RESERVATION_CODE_LENGTH, BASE_DIR

def generate_reservation_code(length=None):
    """
    生成预定码
    Generate reservation code
    """
    if length is None:
        length = RESERVATION_CODE_LENGTH
    
    # 生成随机字符串，包含大写字母和数字
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choice(chars) for _ in range(length))
    
    return code

def generate_reservation_number(date=None, index=None):
    """
    生成唯一的预约序号，格式：RN-年月日-时间戳后4位-序号
    """
    if date is None:
        date_str = datetime.now().strftime("%Y%m%d")
    else:
        date_str = date.strftime("%Y%m%d")
    timestamp = str(int(datetime.now().timestamp()))[-4:]
    if index is not None:
        return f"RN-{date_str}-{timestamp}-{index}"
    else:
        return f"RN-{date_str}-{timestamp}"


def generate_equipment_qrcode(equipment_id, equipment_name):
    """
    生成设备二维码
    Generate equipment QR code
    """
    try:
        # 确保目录存在
        qrcode_dir = os.path.join(BASE_DIR, "backend", "static", "qrcodes", "equipments")
        os.makedirs(qrcode_dir, exist_ok=True)
        
        # 生成二维码
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(f"/qrcode/equipment/{equipment_id}")
        qr.make(fit=True)
        
        # 创建图像
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 保存图像
        qrcode_path = os.path.join(qrcode_dir, f"{equipment_id}.png")
        img.save(qrcode_path)
        
        # 返回相对路径
        return f"/static/qrcodes/equipments/{equipment_id}.png"
    except Exception as e:
        logger.error(f"生成设备二维码失败: {e}")
        return None

def generate_multi_function_qrcode(item_type, item_id, data):
    """
    生成多功能二维码
    Generate multi-function QR code
    """
    try:
        # 确保目录存在
        qrcode_dir = os.path.join(BASE_DIR, "backend", "static", "qrcodes", item_type)
        os.makedirs(qrcode_dir, exist_ok=True)
        
        # 生成二维码
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # 创建图像
        img = qr.make_image(fill_color="black", back_color="white")
        
        # 保存图像
        qrcode_path = os.path.join(qrcode_dir, f"{item_id}.png")
        img.save(qrcode_path)
        
        # 返回相对路径
        return f"/static/qrcodes/{item_type}/{item_id}.png"
    except Exception as e:
        logger.error(f"生成多功能二维码失败: {e}")
        return None
