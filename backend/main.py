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
from fastapi.responses import RedirectResponse
import sys
from contextlib import asynccontextmanager
import uvicorn
import asyncio
from datetime import datetime, timedelta
import logging.handlers

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# 直接从项目根目录导入config.py
sys.path.insert(0, project_root)  # 确保项目根目录在导入路径的最前面

# 导入配置和模块
from config import TEMPLATES_DIR, STATIC_DIR, APP_NAME, DEFAULT_LANGUAGE
from backend.database import init_db, get_db
from backend.i18n import setup_i18n, get_locale, I18nMiddleware
from backend.utils.status_updater import update_reservation_statuses

# 确保日志目录存在
logs_dir = os.path.join(project_root, "logs")
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# 设置日志（按天轮转，保留30天的日志）
# 确保日志目录存在
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# 创建日志格式化器
log_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# 获取当前日期作为文件名
def get_log_filename():
    """获取基于当前日期的日志文件名"""
    current_date = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(logs_dir, f"app.{current_date}.log")

# 创建自定义的FileHandler，每天使用新的日志文件
class DailyFileHandler(logging.FileHandler):
    """每天使用新的日志文件的处理器"""
    def __init__(self, filename_func, mode='a', encoding=None, delay=False):
        self.filename_func = filename_func
        # 使用当前日期初始化文件名
        filename = self.filename_func()
        super().__init__(filename, mode, encoding, delay)
        self.date = datetime.now().date()

    def emit(self, record):
        """发出日志记录前检查日期是否变化"""
        current_date = datetime.now().date()
        # 如果日期变化，关闭当前文件并打开新文件
        if current_date != self.date:
            self.close()
            self.baseFilename = self.filename_func()
            self.stream = self._open()
            self.date = current_date
        super().emit(record)

# 创建每日新文件的处理器
file_handler = DailyFileHandler(
    filename_func=get_log_filename,
    encoding="utf-8",
    delay=True  # 延迟创建文件，直到第一条日志记录
)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)

# 配置根日志记录器
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

# 获取当前模块的日志记录器
logger = logging.getLogger(__name__)

# 定义状态更新任务
async def status_update_task():
    """定期更新预约状态的后台任务"""
    while True:
        logger.info("执行预约状态更新任务")
        db = None
        try:
            # 获取数据库会话
            db = next(get_db())
            # 更新预约状态
            update_reservation_statuses(db)
        except Exception as e:
            logger.error(f"更新预约状态时出错: {str(e)}")
        finally:
            # 确保数据库连接被关闭
            if db:
                db.close()

        # 每1分钟执行一次
        await asyncio.sleep(60)

# 定义生命周期管理器
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行
    logger.info("应用启动 / Application started")
    await init_db()

    # 启动状态更新后台任务
    task = asyncio.create_task(status_update_task())

    yield

    # 关闭时执行
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logger.info("状态更新任务已取消")

    logger.info("应用关闭 / Application shut down")

# 创建FastAPI应用
app = FastAPI(
    title=APP_NAME[DEFAULT_LANGUAGE],
    description="设备预定系统 / Equipment Reservation System",
    lifespan=lifespan
)

# 设置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

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
        logger.error(f"健康检查失败: {str(e)}")
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
