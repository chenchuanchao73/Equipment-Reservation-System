"""
日期处理工具
Date utilities
"""
import datetime
import calendar
from datetime import date, time, datetime, timedelta, timezone
import logging

# 设置日志
logger = logging.getLogger(__name__)

# 北京时区 (UTC+8)
BEIJING_TIMEZONE = timezone(timedelta(hours=8))

def convert_to_beijing_time(dt):
    """
    将UTC时间转换为北京时间（UTC+8）
    Convert UTC time to Beijing time (UTC+8)
    """
    if dt is None:
        return None

    try:
        # 如果datetime对象没有时区信息，假定它是UTC时间
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        # 转换为北京时间
        beijing_time = dt.astimezone(BEIJING_TIMEZONE)
        return beijing_time
    except Exception as e:
        logger.error(f"转换为北京时间失败: {e}")
        return dt

def format_datetime(dt, format_str="%Y-%m-%d %H:%M", to_beijing=True):
    """
    格式化日期时间
    Format datetime

    Args:
        dt: 要格式化的日期时间
        format_str: 格式化字符串
        to_beijing: 是否转换为北京时间
    """
    if dt is None:
        return ""

    try:
        # 转换为北京时间
        if to_beijing:
            dt = convert_to_beijing_time(dt)

        return dt.strftime(format_str)
    except Exception as e:
        logger.error(f"格式化日期时间失败: {e}")
        return str(dt)

def parse_datetime(dt_str, format_str="%Y-%m-%d %H:%M"):
    """
    解析日期时间字符串
    Parse datetime string
    """
    if not dt_str:
        return None

    try:
        return datetime.strptime(dt_str, format_str)
    except Exception as e:
        logger.error(f"解析日期时间字符串失败: {e}")
        return None

def get_date_range(start_date, end_date):
    """
    获取日期范围
    Get date range
    """
    if not start_date or not end_date:
        return []

    try:
        # 确保start_date和end_date是datetime.date类型
        if isinstance(start_date, datetime.datetime):
            start_date = start_date.date()
        if isinstance(end_date, datetime.datetime):
            end_date = end_date.date()

        # 生成日期范围
        date_range = []
        current_date = start_date
        while current_date <= end_date:
            date_range.append(current_date)
            current_date += datetime.timedelta(days=1)

        return date_range
    except Exception as e:
        logger.error(f"获取日期范围失败: {e}")
        return []

def is_date_in_range(date, start_date, end_date):
    """
    判断日期是否在范围内
    Check if date is in range
    """
    if not date or not start_date or not end_date:
        return False

    try:
        # 确保date、start_date和end_date是datetime.date类型
        if isinstance(date, datetime.datetime):
            date = date.date()
        if isinstance(start_date, datetime.datetime):
            start_date = start_date.date()
        if isinstance(end_date, datetime.datetime):
            end_date = end_date.date()

        return start_date <= date <= end_date
    except Exception as e:
        logger.error(f"判断日期是否在范围内失败: {e}")
        return False

def get_datetime_range(start_datetime, end_datetime, interval_minutes=30):
    """
    获取时间范围
    Get datetime range
    """
    if not start_datetime or not end_datetime:
        return []

    try:
        # 生成时间范围
        datetime_range = []
        current_datetime = start_datetime
        while current_datetime <= end_datetime:
            datetime_range.append(current_datetime)
            current_datetime += datetime.timedelta(minutes=interval_minutes)

        return datetime_range
    except Exception as e:
        logger.error(f"获取时间范围失败: {e}")
        return []

def combine_date_time(date_obj, time_obj):
    """
    合并日期和时间
    Combine date and time
    """
    try:
        return datetime.combine(date_obj, time_obj)
    except Exception as e:
        logger.error(f"合并日期和时间失败: {e}")
        return None

def get_weekday(date_obj):
    """
    获取星期几 (0-6, 0表示周日)
    Get weekday (0-6, 0 means Sunday)
    """
    try:
        return date_obj.weekday() + 1 if date_obj.weekday() < 6 else 0
    except Exception as e:
        logger.error(f"获取星期几失败: {e}")
        return None

def get_next_occurrence_date(start_date, pattern_type, days_of_week=None, days_of_month=None):
    """
    获取下一个符合条件的日期
    Get next occurrence date
    """
    if not start_date:
        return None

    try:
        current_date = start_date

        if pattern_type == "daily":
            # 每天，直接返回下一天
            return current_date + datetime.timedelta(days=1)

        elif pattern_type == "weekly" and days_of_week:
            # 每周，找到下一个符合条件的星期几
            weekday = get_weekday(current_date)
            days_to_add = 1

            while True:
                next_date = current_date + datetime.timedelta(days=days_to_add)
                next_weekday = get_weekday(next_date)
                if next_weekday in days_of_week:
                    return next_date
                days_to_add += 1

                # 防止无限循环
                if days_to_add > 7:
                    return None

        elif pattern_type == "monthly" and days_of_month:
            # 每月，找到下一个符合条件的日期
            current_month = current_date.month
            current_year = current_date.year

            # 检查当前月份剩余的日期
            for day in sorted(days_of_month):
                if day > current_date.day and day <= calendar.monthrange(current_year, current_month)[1]:
                    return datetime.date(current_year, current_month, day)

            # 如果当前月份没有符合条件的日期，检查下一个月
            next_month = current_month + 1 if current_month < 12 else 1
            next_year = current_year if current_month < 12 else current_year + 1

            for day in sorted(days_of_month):
                if day <= calendar.monthrange(next_year, next_month)[1]:
                    return datetime.date(next_year, next_month, day)

        return None
    except Exception as e:
        logger.error(f"获取下一个符合条件的日期失败: {e}")
        return None
