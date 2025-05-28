import sqlite3
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.routes.auth import get_current_admin
from backend.utils.date_utils import convert_to_beijing_time
from datetime import datetime, date, time

router = APIRouter(
    prefix="/api/db",
    tags=["db_admin"],
)

# 获取所有表名
@router.get("/tables")
async def list_tables(db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    try:
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()
        return {"tables": tables}
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"获取数据库表名失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取数据库表名失败: {e}")

# 获取表字段结构
@router.get("/table/{table_name}/columns")
async def get_table_columns(table_name: str, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    inspector = inspect(db.bind)
    try:
        columns = inspector.get_columns(table_name)
        return {"columns": columns}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"表不存在: {table_name}")

# 分页获取表数据
@router.get("/table/{table_name}/rows")
async def get_table_rows(
    table_name: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    try:
        # 检查表是否存在
        inspector = inspect(db.bind)
        available_tables = inspector.get_table_names()
        if table_name not in available_tables:
            raise HTTPException(status_code=404, detail=f"表不存在: {table_name}")

        # 获取表的总行数
        count_sql = text(f'SELECT COUNT(*) FROM "{table_name}"')
        count_result = db.execute(count_sql).fetchone()
        total = count_result[0]

        # 获取表的列信息，用于判断列类型
        columns_info = inspector.get_columns(table_name)
        column_types = {col['name']: col['type'] for col in columns_info}

        # 使用双引号包裹表名，避免 SQLite 关键字冲突
        sql = text(f'SELECT * FROM "{table_name}" LIMIT :limit OFFSET :skip')
        result = db.execute(sql, {"limit": limit, "skip": skip})
        # 处理不同版本 SQLAlchemy 的结果集转换
        rows = []
        # 获取列名
        column_names = result.keys()
        for row in result:
            # 使用列名和值创建字典
            row_dict = {}
            for idx, column_name in enumerate(column_names):
                value = row[idx]

                # 特殊处理各种日期时间类型
                if isinstance(value, datetime):
                    # 对于更新时间字段，直接显示数据库中的值，不做时区转换
                    # 因为数据库中已经存储了北京时间
                    if column_name in ['updated_at', 'created_at']:
                        value = value.strftime("%Y-%m-%d %H:%M:%S")
                    # 对于预约的开始和结束时间，也不做时区转换
                    elif column_name in ['start_datetime', 'end_datetime']:
                        value = value.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        # 其他datetime字段，保持原样
                        value = value.strftime("%Y-%m-%d %H:%M:%S")
                # 特殊处理日期类型
                elif isinstance(value, date) and not isinstance(value, datetime):
                    # 日期类型，只显示日期部分
                    value = value.strftime("%Y-%m-%d")
                # 特殊处理时间类型
                elif isinstance(value, time):
                    # 时间类型，只显示时间部分，不显示微秒
                    value = value.strftime("%H:%M:%S")
                # 处理SQLite的日期时间文本格式
                elif isinstance(value, str):
                    # 尝试检测日期时间字符串
                    if table_name == 'recurring_reservation' and column_name in ['start_date', 'end_date']:
                        try:
                            # 如果是日期字符串，只保留日期部分
                            dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
                            value = dt.strftime("%Y-%m-%d")
                        except:
                            pass
                    elif table_name == 'recurring_reservation' and column_name in ['start_time', 'end_time']:
                        try:
                            # 如果是时间字符串，只保留时间部分，去掉微秒
                            if ' ' in value:  # 格式如 "09:00:00 000000"
                                value = value.split(' ')[0]
                        except:
                            pass

                row_dict[column_name] = value
            rows.append(row_dict)
        return {"rows": rows, "total": total}
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"查询表数据失败: {table_name}, 错误: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"查询表数据失败: {str(e)}")