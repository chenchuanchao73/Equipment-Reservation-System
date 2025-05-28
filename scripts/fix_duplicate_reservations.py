#!/usr/bin/env python
"""
修复重复的预约编号的命令行脚本
Command line script to fix duplicate reservation numbers
"""
import os
import sys
from pathlib import Path

# 获取项目根目录
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# 导入修复函数
from backend.migrations.fix_duplicate_reservation_numbers import fix_duplicate_reservation_numbers

if __name__ == "__main__":
    print("开始修复重复的预约编号...")
    fixed = fix_duplicate_reservation_numbers()
    print(f"修复完成，共修复 {fixed} 个重复的预约编号")
    print("请重启设备预约系统以应用更改。") 