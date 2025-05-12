"""
通用工具函数
General utility functions
"""
import os
import logging
import random
import string
from datetime import datetime, timedelta

# 设置日志
logger = logging.getLogger(__name__)

# 导入配置
from config import BASE_DIR

def generate_random_string(length=8, include_lowercase=True, include_uppercase=True, include_digits=True, include_special=False):
    """
    生成随机字符串
    Generate random string
    """
    chars = ""
    if include_lowercase:
        chars += string.ascii_lowercase
    if include_uppercase:
        chars += string.ascii_uppercase
    if include_digits:
        chars += string.digits
    if include_special:
        chars += string.punctuation
    
    if not chars:
        chars = string.ascii_letters + string.digits
    
    return ''.join(random.choice(chars) for _ in range(length))

def ensure_dir_exists(dir_path):
    """
    确保目录存在
    Ensure directory exists
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path

def get_file_extension(filename):
    """
    获取文件扩展名
    Get file extension
    """
    if not filename:
        return ""
    
    return os.path.splitext(filename)[1].lower()

def is_valid_image_extension(extension):
    """
    判断是否为有效的图片扩展名
    Check if extension is valid image extension
    """
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
    return extension.lower() in valid_extensions

def get_relative_path(path):
    """
    获取相对路径
    Get relative path
    """
    if not path:
        return ""
    
    # 将绝对路径转换为相对路径
    if os.path.isabs(path):
        try:
            return os.path.relpath(path, BASE_DIR)
        except ValueError:
            return path
    
    return path

def format_file_size(size_bytes):
    """
    格式化文件大小
    Format file size
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def get_time_ago(dt):
    """
    获取多久以前
    Get time ago
    """
    if not dt:
        return ""
    
    now = datetime.now()
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years}年前"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months}个月前"
    elif diff.days > 0:
        return f"{diff.days}天前"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours}小时前"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes}分钟前"
    else:
        return "刚刚"

def truncate_string(s, max_length=100, suffix="..."):
    """
    截断字符串
    Truncate string
    """
    if not s:
        return ""
    
    if len(s) <= max_length:
        return s
    
    return s[:max_length] + suffix
