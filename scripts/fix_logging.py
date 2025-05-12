"""
修复日志配置脚本
Fix Logging Configuration Script

此脚本用于修复backend/main.py中的日志配置，使其正确地按天轮转。
This script is used to fix the logging configuration in backend/main.py to correctly rotate logs daily.
"""
import os
import re
from pathlib import Path

def fix_logging():
    """修复日志配置"""
    # 获取项目根目录
    project_root = Path(__file__).resolve().parent.parent
    main_py_path = os.path.join(project_root, "backend", "main.py")
    
    # 检查main.py文件是否存在
    if not os.path.exists(main_py_path):
        print(f"main.py文件不存在: {main_py_path}")
        return
    
    # 读取main.py文件内容
    with open(main_py_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 定义要替换的日志配置部分
    old_logging_config = r"""# 设置日志（.*?）
log_formatter = logging\.Formatter\(
    "%(asctime)s \| %(levelname)s \| %(name)s \| %(lineno)d \| %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
\)

log_file = os\.path\.join\(logs_dir, "app\.log"\)
file_handler = logging\.handlers\.TimedRotatingFileHandler\(
    log_file, when=".*?", interval=\d+, backupCount=\d+, encoding="utf-8"
\)
# 设置日志文件后缀为日期格式
file_handler\.suffix = ".*?"
file_handler\.setFormatter\(log_formatter\)
file_handler\.setLevel\(logging\.DEBUG\)"""
    
    # 定义新的日志配置
    new_logging_config = """# 设置日志（按天轮转，保留30天，格式更详细）
log_formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(lineno)d | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

log_file = os.path.join(logs_dir, "app.log")
file_handler = logging.handlers.TimedRotatingFileHandler(
    log_file, when="midnight", interval=1, backupCount=30, encoding="utf-8"
)
# 设置日志文件后缀为日期格式
file_handler.suffix = "%Y-%m-%d"
# 设置延迟创建文件，直到第一条日志记录
file_handler.delay = True
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.DEBUG)"""
    
    # 使用正则表达式替换日志配置部分
    new_content = re.sub(old_logging_config, new_logging_config, content, flags=re.DOTALL)
    
    # 如果内容没有变化，说明正则表达式没有匹配到
    if new_content == content:
        print("未找到匹配的日志配置部分，尝试使用简单替换")
        
        # 定义要替换的简单日志配置部分
        simple_old_config = """file_handler = logging.handlers.TimedRotatingFileHandler(
    log_file, when="midnight", interval=1, backupCount=30, encoding="utf-8"
)
# 设置日志文件后缀为日期格式
file_handler.suffix = ".%Y-%m-%d"
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.DEBUG)"""
        
        simple_new_config = """file_handler = logging.handlers.TimedRotatingFileHandler(
    log_file, when="midnight", interval=1, backupCount=30, encoding="utf-8"
)
# 设置日志文件后缀为日期格式
file_handler.suffix = "%Y-%m-%d"
# 设置延迟创建文件，直到第一条日志记录
file_handler.delay = True
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.DEBUG)"""
        
        new_content = content.replace(simple_old_config, simple_new_config)
        
        # 如果内容仍然没有变化，说明简单替换也没有匹配到
        if new_content == content:
            print("简单替换也未找到匹配的日志配置部分，请手动修改")
            return
    
    # 写入修改后的内容
    with open(main_py_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print(f"日志配置已修复: {main_py_path}")
    
    # 修改start.py中的uvicorn配置
    start_py_path = os.path.join(project_root, "start.py")
    
    # 检查start.py文件是否存在
    if not os.path.exists(start_py_path):
        print(f"start.py文件不存在: {start_py_path}")
        return
    
    # 读取start.py文件内容
    with open(start_py_path, "r", encoding="utf-8") as f:
        start_content = f.read()
    
    # 定义要替换的uvicorn配置部分
    old_uvicorn_config = r"""uvicorn\.run\("backend\.main:app", host="0\.0\.0\.0", port=port, reload=True.*?\)"""
    
    # 定义新的uvicorn配置
    new_uvicorn_config = """uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True, log_config=None)"""
    
    # 使用正则表达式替换uvicorn配置部分
    new_start_content = re.sub(old_uvicorn_config, new_uvicorn_config, start_content)
    
    # 如果内容没有变化，说明正则表达式没有匹配到
    if new_start_content == start_content:
        print("未找到匹配的uvicorn配置部分，尝试使用简单替换")
        
        # 定义要替换的简单uvicorn配置部分
        simple_old_config = """uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)"""
        
        simple_new_config = """uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True, log_config=None)"""
        
        new_start_content = start_content.replace(simple_old_config, simple_new_config)
        
        # 如果内容仍然没有变化，说明简单替换也没有匹配到
        if new_start_content == start_content:
            print("简单替换也未找到匹配的uvicorn配置部分，请手动修改")
            return
    
    # 写入修改后的内容
    with open(start_py_path, "w", encoding="utf-8") as f:
        f.write(new_start_content)
    
    print(f"uvicorn配置已修复: {start_py_path}")
    
    print("日志配置修复完成!")

if __name__ == "__main__":
    fix_logging()
