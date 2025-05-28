"""
物品预定系统主应用入口
Equipment Reservation System main application entry
"""
import logging
import os
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
import sys
from contextlib import asynccontextmanager
import uvicorn
import asyncio
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# 直接从项目根目录导入config.py
sys.path.insert(0, project_root)  # 确保项目根目录在导入路径的最前面

# 导入新的日志系统
from log_config import setup_logging, check_log_file, backup_logs, force_log_rotation

# 导入配置和模块
from config import TEMPLATES_DIR, STATIC_DIR, APP_NAME, DEFAULT_LANGUAGE
from backend.database import init_db, get_db
from backend.i18n import setup_i18n, get_locale, I18nMiddleware
from backend.utils.status_updater import update_reservation_statuses
from backend.utils.duplicate_checker import check_and_fix_duplicate_numbers

# 设置新的日志系统
logger, log_handler = setup_logging()
check_log_file()
logger.info("FastAPI应用初始化中...")

# 定义状态更新任务
async def status_update_task():
    """定期更新预约状态的后台任务"""
    while True:
        # 先检查日志文件是否存在
        check_log_file()

        logger.info("执行预约状态更新任务")
        db = None
        try:
            # 获取数据库会话
            db = next(get_db())
            # 更新预约状态
            update_reservation_statuses(db)
        except Exception as e:
            logger.error(f"更新预约状态时出错: {str(e)}", exc_info=True)
            # 发生错误时尝试备份日志
            backup_logs()
        finally:
            # 确保数据库连接被关闭
            if db:
                db.close()

        # 每1分钟执行一次
        await asyncio.sleep(60)

# 周期性日志维护任务
async def log_maintenance_task():
    """周期性日志维护任务"""
    try:
        while True:
            # 每小时执行一次
            await asyncio.sleep(3600)  # 3600秒 = 1小时

            logger.info("执行日志维护任务")

            # 检查日志文件
            check_log_file()

            # 备份日志
            backup_logs()

            # 每天午夜左右（0:30）强制执行一次日志轮转，确保日志按天分割
            current_hour = datetime.now().hour
            current_minute = datetime.now().minute
            if current_hour == 0 and current_minute >= 30 and current_minute < 35:
                logger.info("执行每日日志轮转")
                force_log_rotation()

    except Exception as e:
        logger.error(f"日志维护任务异常: {e}", exc_info=True)

# 定期检查重复预约序号任务
async def duplicate_check_task():
    """定期检查重复预约序号的后台任务"""
    try:
        while True:
            # 每1小时执行一次
            await asyncio.sleep(3600)  # 3600秒 = 1小时

            logger.info("执行预约序号重复检查任务")
            db = None
            try:
                # 获取数据库会话
                db = next(get_db())
                # 检查并修复重复的预约序号
                fixed_count = check_and_fix_duplicate_numbers(db)
                if fixed_count > 0:
                    logger.info(f"成功修复 {fixed_count} 个重复的预约序号")
                else:
                    logger.info("没有发现重复的预约序号")
            except Exception as e:
                logger.error(f"检查重复预约序号时出错: {str(e)}", exc_info=True)
                # 发生错误时尝试备份日志
                backup_logs()
            finally:
                # 确保数据库连接被关闭
                if db:
                    db.close()
    except Exception as e:
        logger.error(f"预约序号重复检查任务异常: {e}", exc_info=True)

# 定义生命周期管理器
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    logger.info("应用启动 / Application started")
    await init_db()

    # 启动状态更新后台任务
    status_task = asyncio.create_task(status_update_task())

    # 启动日志维护任务
    log_task = asyncio.create_task(log_maintenance_task())

    # 启动预约序号重复检查任务
    duplicate_task = asyncio.create_task(duplicate_check_task())

    logger.info("后台任务已启动")

    yield

    # 关闭时执行
    status_task.cancel()
    log_task.cancel()
    duplicate_task.cancel()
    try:
        await status_task
        await log_task
        await duplicate_task
    except asyncio.CancelledError:
        logger.info("后台任务已取消")

    # 关闭日志处理器
    for handler in logger.handlers:
        handler.close()

    logger.info("应用关闭 / Application shut down")

# 创建FastAPI应用
app = FastAPI(
    title=APP_NAME[DEFAULT_LANGUAGE],
    description="设备预定系统 / Equipment Reservation System",
    lifespan=lifespan,
    default_response_class=JSONResponse
)

# 设置默认JSON响应类设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，包括局域网IP
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# 添加日志中间件
from backend.middlewares.log_middleware import LogMiddleware
app.add_middleware(LogMiddleware)

# 自定义JSON响应处理
@app.middleware("http")
async def add_utf8_content_type(request, call_next):
    response = await call_next(request)
    if response.headers.get("content-type") == "application/json":
        response.headers["content-type"] = "application/json; charset=utf-8"
    return response

# 设置国际化中间件
setup_i18n()
app.add_middleware(I18nMiddleware)

# 设置静态文件
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 设置模板
templates = Jinja2Templates(directory=TEMPLATES_DIR)
templates.env.globals["get_locale"] = get_locale

# 导入路由模块
from backend.routes.equipment import router as equipment_router
from backend.routes.equipment_category import router as equipment_category_router
from backend.routes.reservation import router as reservation_router
from backend.routes.recurring_reservation import router as recurring_reservation_router
from backend.routes.admin import router as admin_router
from backend.routes.statistics import router as statistics_router
from backend.routes.upload import router as upload_router
from backend.routes.calendar import router as calendar_router
from backend.routes.db_admin import router as db_admin_router  # 导入数据库表查看路由
from backend.routes.announcements import router as announcements_router
from backend.routes.system_logs import router as system_logs_router  # 导入系统日志路由

# 注册路由
app.include_router(equipment_router)
app.include_router(equipment_category_router)
app.include_router(reservation_router)
app.include_router(recurring_reservation_router)
app.include_router(admin_router)
app.include_router(statistics_router)
app.include_router(upload_router)
app.include_router(calendar_router)
app.include_router(db_admin_router)  # 注册数据库表查看路由
app.include_router(announcements_router)
app.include_router(system_logs_router)  # 注册系统日志路由

@app.get("/")
def root(request: Request):
    """
    首页路由
    Home page route
    """
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )

@app.get("/api/health")
def health_check():
    """
    健康检查端点
    Health check endpoint
    """
    try:
        # 简单返回健康状态，不进行数据库检查
        return {
            "status": "ok",
            "message": "Service is healthy",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"健康检查失败: {str(e)}")

@app.get("/language/{lang}")
def change_language(lang: str):
    """
    切换语言
    Change language
    """
    response = RedirectResponse(url="/")
    response.set_cookie(key="language", value=lang)
    return response

# 当直接运行此文件时启动服务器
if __name__ == "__main__":
    # 启动服务器，绑定到所有网络接口
    uvicorn.run(app, host="0.0.0.0", port=8000)
