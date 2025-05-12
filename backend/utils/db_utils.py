"""
数据库工具函数
Database utility functions
"""
from datetime import datetime, timedelta
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import DateTime

class BeijingNow(expression.FunctionElement):
    """
    自定义SQLAlchemy函数，返回北京时间（UTC+8）
    Custom SQLAlchemy function that returns Beijing time (UTC+8)
    """
    type = DateTime()
    name = 'beijing_now'

@compiles(BeijingNow, 'sqlite')
def sqlite_beijing_now(element, compiler, **kw):
    """
    SQLite实现：使用datetime('now', '+8 hours')
    SQLite implementation: use datetime('now', '+8 hours')
    """
    return "datetime('now', '+8 hours')"

@compiles(BeijingNow, 'postgresql')
def pg_beijing_now(element, compiler, **kw):
    """
    PostgreSQL实现：使用now() AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Shanghai'
    PostgreSQL implementation: use now() AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Shanghai'
    """
    return "now() AT TIME ZONE 'UTC' AT TIME ZONE 'Asia/Shanghai'"

@compiles(BeijingNow, 'mysql')
def mysql_beijing_now(element, compiler, **kw):
    """
    MySQL实现：使用CONVERT_TZ(NOW(), 'UTC', 'Asia/Shanghai')
    MySQL implementation: use CONVERT_TZ(NOW(), 'UTC', 'Asia/Shanghai')
    """
    return "CONVERT_TZ(NOW(), 'UTC', 'Asia/Shanghai')"

def get_beijing_now():
    """
    获取当前北京时间
    Get current Beijing time
    """
    return datetime.utcnow() + timedelta(hours=8)
