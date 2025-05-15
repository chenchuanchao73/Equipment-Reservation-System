"""
设备预定系统启动脚本
Equipment Reservation System startup script
"""
import os
import sys
import time
import webbrowser
import logging
import uvicorn
from pathlib import Path
from dotenv import load_dotenv
import socket
import asyncio

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

# 导入新的日志配置
from log_config import setup_logging, check_log_file, backup_logs, force_log_rotation

# 加载环境变量
load_dotenv()

# 设置新的日志系统
logger, log_handler = setup_logging()
check_log_file()
logger.info("设备预定系统启动中...")

# 禁用其他日志记录器的传播，避免重复日志
logging.getLogger("uvicorn").propagate = False
logging.getLogger("uvicorn.error").propagate = False
logging.getLogger("uvicorn.access").propagate = False

def check_dependencies():
    """检查依赖是否已安装"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import pydantic
        import jinja2
        import aiofiles
        import i18n
        from concurrent_log_handler import ConcurrentTimedRotatingFileHandler
        return True
    except ImportError as e:
        logger.error(f"缺少依赖: {e}")
        logger.info("请运行 'pip install -r requirements.txt 和 pip install -r requirements_for_logging.txt' 安装所需依赖")
        return False

# 日志维护任务
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
            
    except Exception as e:
        logger.error(f"日志维护任务异常: {e}", exc_info=True)

def main():
    """主函数"""
    print("\n=== 欢迎使用设备预定系统 ===\n")

    # 检查依赖
    if not check_dependencies():
        input("按Enter键退出...")
        return

    # 获取端口
    port = int(os.getenv("PORT", "8000"))

    # 获取本机IP地址
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)

    # 打开浏览器
    def open_browser():
        time.sleep(2)
        # 打开前端应用程序的URL
        frontend_url = "http://localhost:8080"
        print(f"正在打开前端应用程序: {frontend_url}")
        webbrowser.open(frontend_url)

    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()

    # 启动日志维护任务
    async def start_log_task():
        asyncio.create_task(log_maintenance_task())
        
    # 执行日志任务
    asyncio.run(start_log_task())

    logger.info(f"应用程序将在 http://localhost:{port} 启动")
    logger.info(f"局域网可通过 http://{ip_address}:{port} 访问")
    print(f"应用程序将在 http://localhost:{port} 启动")
    print(f"局域网可通过 http://{ip_address}:{port} 访问")
    print("按Ctrl+C可以停止应用程序")

    # 使用新的日志配置启动uvicorn
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "logging.Formatter",
                "fmt": "%(asctime)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
            "uvicorn.error": {"handlers": ["default"], "level": "INFO", "propagate": False},
            "uvicorn.access": {"handlers": ["default"], "level": "INFO", "propagate": False},
        },
    }

    # 启动uvicorn，使用我们的日志配置
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True, log_config=log_config)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n应用程序已停止")
        logger.info("应用程序已停止")
        # 关闭日志处理器
        for handler in logger.handlers:
            handler.close()
    except Exception as e:
        logger.error(f"应用程序启动失败: {e}", exc_info=True)
        input("\n按Enter键退出...")
