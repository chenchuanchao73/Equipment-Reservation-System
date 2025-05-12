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

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

# 加载环境变量
load_dotenv()

# 确保日志目录存在
logs_dir = os.path.join(project_root, "logs")
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# 设置日志
log_file = os.path.join(logs_dir, "app.log")

# 配置根日志记录器
# 创建日志格式化器
log_formatter = logging.Formatter(
    "%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# 创建按天轮转的文件处理器
file_handler = logging.handlers.TimedRotatingFileHandler(
    log_file,
    when="midnight",  # 每天午夜轮转
    interval=1,       # 每1天轮转一次
    backupCount=30,   # 保留30天的日志
    encoding="utf-8"
)
# 设置日志文件后缀为日期格式
file_handler.suffix = "%Y-%m-%d"
file_handler.setFormatter(log_formatter)

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)

# 配置根日志记录器
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)

# 禁用其他日志记录器的传播，避免重复日志
logging.getLogger("uvicorn").propagate = False
logging.getLogger("uvicorn.error").propagate = False
logging.getLogger("uvicorn.access").propagate = False

logger = logging.getLogger(__name__)

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
        return True
    except ImportError as e:
        logger.error(f"缺少依赖: {e}")
        logger.info("请运行 'pip install -r requirements.txt' 安装所需依赖")
        return False

def main():
    """主函数"""
    print("\n=== 欢迎使用设备预定系统 ===\n")

    # 检查依赖
    if not check_dependencies():
        input("按Enter键退出...")
        return

    # 获取端口
    port = int(os.getenv("PORT", "8000"))

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

    print(f"应用程序将在 http://localhost:{port} 启动")
    print("按Ctrl+C可以停止应用程序")

    # 启动应用，使用我们自己的日志配置
    # 创建一个日志配置，使用TimedRotatingFileHandler按天轮转日志
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
            "file": {
                "formatter": "default",
                "class": "logging.FileHandler",
                "filename": log_file,
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["default", "file"], "level": "INFO", "propagate": False},
            "uvicorn.error": {"handlers": ["default", "file"], "level": "INFO", "propagate": False},
            "uvicorn.access": {"handlers": ["default", "file"], "level": "INFO", "propagate": False},
        },
    }

    # 启动uvicorn，使用我们的日志配置
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True, log_config=log_config)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n应用程序已停止")
    except Exception as e:
        logger.error(f"应用程序启动失败: {e}")
        input("\n按Enter键退出...")
