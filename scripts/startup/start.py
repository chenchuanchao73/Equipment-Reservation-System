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
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

# 加载环境变量
load_dotenv()

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
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
        webbrowser.open(f"http://localhost:{port}")

    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()

    print(f"应用程序将在 http://localhost:{port} 启动")
    print("按Ctrl+C可以停止应用程序")

    # 启动应用
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n应用程序已停止")
    except Exception as e:
        logger.error(f"应用程序启动失败: {e}")
        input("\n按Enter键退出...")
