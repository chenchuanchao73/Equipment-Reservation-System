#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
按天轮转日志系统测试脚本
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta
from log_config import setup_logging, check_log_file, force_log_rotation, test_log_rotation

def main():
    print("开始测试按天轮转日志系统...")
    
    # 初始化日志系统
    logger, handler = setup_logging()
    check_log_file()
    
    # 写入一些基本日志
    logger.info("这是测试日志消息 - 当前日期: %s", datetime.now().strftime("%Y-%m-%d"))
    logger.warning("这是一条警告消息")
    logger.error("这是一条错误消息")
    
    # 显示当前日志文件情况
    log_dir = "logs"
    today = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"app.log.{today}")
    main_log = os.path.join(log_dir, "app.log")
    
    print("\n当前日志文件情况:")
    if os.path.exists(log_file):
        print(f"今日日志文件存在: {log_file}")
        print(f"大小: {os.path.getsize(log_file)/1024:.2f}KB")
    else:
        print(f"今日日志文件不存在: {log_file}")
    
    if os.path.exists(main_log):
        print(f"主日志文件存在: {main_log}")
        print(f"大小: {os.path.getsize(main_log)/1024:.2f}KB")
    else:
        print("主日志文件不存在!")
    
    # 显示所有日志文件
    if os.path.exists(log_dir):
        print("\n所有日志文件:")
        log_files = [f for f in os.listdir(log_dir) if f.startswith("app.log")]
        for file in log_files:
            file_path = os.path.join(log_dir, file)
            print(f"- {file}: {os.path.getsize(file_path)/1024:.2f}KB")
    
    # 询问是否测试手动轮转
    choice = input("\n是否测试手动日志轮转? (y/n): ")
    if choice.lower() == 'y':
        print("执行手动日志轮转...")
        
        # 记录一些额外的日志
        for i in range(5):
            logger.info(f"测试日志 #{i+1} - 轮转前")
            time.sleep(0.5)
        
        # 执行手动轮转
        success = force_log_rotation()
        
        # 再次记录一些日志
        for i in range(5):
            logger.info(f"测试日志 #{i+1} - 轮转后")
            time.sleep(0.5)
        
        # 显示轮转后的日志文件
        print("\n轮转后的日志文件:")
        log_files = [f for f in os.listdir(log_dir) if f.startswith("app.log")]
        for file in log_files:
            file_path = os.path.join(log_dir, file)
            print(f"- {file}: {os.path.getsize(file_path)/1024:.2f}KB")
            
        if success:
            print("手动日志轮转测试成功完成!")
        else:
            print("手动日志轮转测试失败!")
    
    # 询问是否运行完整测试
    choice = input("\n是否运行完整的日志轮转测试? (y/n): ")
    if choice.lower() == 'y':
        print("开始完整日志轮转测试...")
        success = test_log_rotation(logger, handler)
        
        if success:
            print("完整日志轮转测试成功完成!")
        else:
            print("完整日志轮转测试失败!")
    
    print("\n测试完成!")

if __name__ == "__main__":
    main() 