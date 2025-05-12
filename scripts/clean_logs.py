"""
清理日志文件脚本
Clean Log Files Script

此脚本用于清理logs目录下的旧日志文件，只保留当前的app.log文件。
This script is used to clean up old log files in the logs directory, keeping only the current app.log file.
"""
import os
import shutil
from pathlib import Path

def clean_logs():
    """清理日志文件"""
    # 获取项目根目录
    project_root = Path(__file__).resolve().parent.parent
    logs_dir = os.path.join(project_root, "logs")
    
    # 检查logs目录是否存在
    if not os.path.exists(logs_dir):
        print(f"日志目录不存在: {logs_dir}")
        return
    
    # 获取所有日志文件
    log_files = [f for f in os.listdir(logs_dir) if f.startswith("app.log.")]
    
    # 备份当前的app.log文件
    app_log_path = os.path.join(logs_dir, "app.log")
    if os.path.exists(app_log_path):
        with open(app_log_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 如果有内容，则备份
        if content.strip():
            backup_path = os.path.join(logs_dir, "app.log.backup")
            shutil.copy2(app_log_path, backup_path)
            print(f"已备份当前日志文件到: {backup_path}")
    
    # 删除旧的日志文件
    for log_file in log_files:
        file_path = os.path.join(logs_dir, log_file)
        try:
            os.remove(file_path)
            print(f"已删除日志文件: {log_file}")
        except Exception as e:
            print(f"删除日志文件失败: {log_file}, 原因: {e}")
    
    # 清空当前的app.log文件
    try:
        with open(app_log_path, "w", encoding="utf-8") as f:
            f.write("")
        print(f"已清空当前日志文件: app.log")
    except Exception as e:
        print(f"清空当前日志文件失败: app.log, 原因: {e}")
    
    print("日志清理完成!")

if __name__ == "__main__":
    clean_logs()
