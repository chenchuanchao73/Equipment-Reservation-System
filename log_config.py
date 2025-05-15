import os
import time
import logging
import shutil
from datetime import datetime, timedelta
from concurrent_log_handler import ConcurrentTimedRotatingFileHandler

# 日志配置
LOG_DIR = "logs"
LOG_FILE = "app.log"
BACKUP_COUNT = 30  # 保留30天的日志

def setup_logging():
    """设置日志系统"""
    # 确保日志目录存在
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # 获取根日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # 移除所有现有的处理器，避免重复
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 添加按天轮转的并发日志处理器
    log_path = os.path.join(LOG_DIR, LOG_FILE)
    handler = ConcurrentTimedRotatingFileHandler(
        filename=log_path,
        when='midnight',  # 每天午夜轮转
        interval=1,       # 每1天轮转一次
        backupCount=BACKUP_COUNT,
        encoding='utf-8',
        delay=False,      # 立即打开文件
        utc=False         # 使用本地时间
    )
    
    # 设置后缀格式为日期 YYYYMMDD
    handler.suffix = "%Y%m%d"
    
    # 设置日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # 添加到根日志记录器
    logger.addHandler(handler)
    
    # 添加控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger, handler

def check_log_file():
    """检查日志文件是否存在，如不存在则创建"""
    log_path = os.path.join(LOG_DIR, LOG_FILE)
    
    # 检查当天的日志文件
    today = datetime.now().strftime("%Y%m%d")
    today_log = f"{log_path}.{today}"
    
    if not os.path.exists(log_path) or os.path.getsize(log_path) == 0:
        # 记录恢复日志
        recovery_log = os.path.join(LOG_DIR, "log_recovery.log")
        with open(recovery_log, "a", encoding='utf-8') as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - 检测到日志文件丢失，正在重新创建\n")
        
        # 创建新的日志文件
        with open(log_path, "a", encoding='utf-8') as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - 日志文件已重新创建\n")
        
        logging.warning("警告：日志文件丢失，已重新创建")
    
    # 检查当天的日志文件是否存在
    if not os.path.exists(today_log):
        # 如果存在基本日志文件但没有当天的日志，强制创建
        logger = logging.getLogger()
        for handler in logger.handlers:
            if isinstance(handler, ConcurrentTimedRotatingFileHandler):
                handler.doRollover()
                break

# 备份现有日志文件
def backup_logs():
    """创建当前日志文件的备份"""
    # 备份当天的日志文件
    today = datetime.now().strftime("%Y%m%d")
    log_path = os.path.join(LOG_DIR, f"{LOG_FILE}.{today}")
    
    # 如果当天的日志文件不存在，查找主日志文件
    if not os.path.exists(log_path):
        log_path = os.path.join(LOG_DIR, LOG_FILE)
    
    if os.path.exists(log_path):
        backup_dir = os.path.join(LOG_DIR, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        backup_path = os.path.join(backup_dir, f"app-{timestamp}.log")
        
        try:
            shutil.copy2(log_path, backup_path)
            logging.info(f"日志备份已创建: {backup_path}")
            return True
        except Exception as e:
            logging.error(f"创建日志备份失败: {e}")
            return False
    return False

# 手动触发日志轮转
def force_log_rotation():
    """手动触发日志轮转"""
    try:
        logger = logging.getLogger()
        for handler in logger.handlers:
            if isinstance(handler, ConcurrentTimedRotatingFileHandler):
                logging.info("手动触发日志轮转...")
                handler.doRollover()
                logging.info("日志轮转完成")
                return True
        logging.warning("未找到TimedRotatingFileHandler，无法执行轮转")
        return False
    except Exception as e:
        logging.error(f"手动轮转日志失败: {e}", exc_info=True)
        return False

# 测试日志轮转函数
def test_log_rotation(logger, handler):
    """测试日志轮转功能"""
    try:
        # 先备份现有日志
        backup_logs()
        
        # 写入一些测试日志
        logger.info("开始测试日志轮转...")
        
        # 显示当前日志文件
        log_dir_files = os.listdir(LOG_DIR)
        log_files = [f for f in log_dir_files if f.startswith(LOG_FILE)]
        
        logger.info(f"当前日志文件: {log_files}")
        
        # 手动触发轮转
        logger.info("手动触发日志轮转...")
        force_log_rotation()
        
        # 验证轮转结果
        log_dir_files = os.listdir(LOG_DIR)
        log_files = [f for f in log_dir_files if f.startswith(LOG_FILE)]
        
        logger.info(f"轮转后的日志文件: {log_files}")
        for file in log_files:
            file_path = os.path.join(LOG_DIR, file)
            file_size = os.path.getsize(file_path)
            logger.info(f"日志文件: {file}, 大小: {file_size/1024:.2f}KB")
        
        logger.info("日志轮转测试完成!")
        return True
        
    except Exception as e:
        logging.error(f"日志轮转测试失败: {e}", exc_info=True)
        return False

# 初始化时运行
if __name__ == "__main__":
    logger, handler = setup_logging()
    check_log_file()
    logger.info("日志系统已初始化")
    
    # 如果需要测试，取消下面的注释
    # test_log_rotation(logger, handler) 