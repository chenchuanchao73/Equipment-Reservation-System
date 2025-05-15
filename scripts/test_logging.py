#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志系统测试脚本
"""

import os
import sys
import time
import logging
from log_config import setup_logging, check_log_file, test_log_rotation

def main():
    print("开始测试日志系统...")
    
    # 初始化日志系统
    logger, handler = setup_logging()
    check_log_file()
    
    # 写入一些基本日志
    logger.info("这是测试日志消息")
    logger.warning("这是一条警告消息")
    logger.error("这是一条错误消息")
    
    # 询问是否执行轮转测试
    print("\n当前日志文件情况:")
    log_dir = "logs"
    log_file = os.path.join(log_dir, "app.log")
    if os.path.exists(log_file):
        print(f"日志文件存在，大小: {os.path.getsize(log_file)/1024:.2f}KB")
    else:
        print("日志文件不存在!")
    
    choice = input("\n是否测试日志轮转功能? (y/n): ")
    if choice.lower() == 'y':
        print("开始测试日志轮转...")
        success = test_log_rotation(logger, handler)
        
        if success:
            print("日志轮转测试成功完成!")
        else:
            print("日志轮转测试失败!")
    
    print("\n测试完成!")

if __name__ == "__main__":
    main() 