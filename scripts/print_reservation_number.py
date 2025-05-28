#!/usr/bin/env python
"""
测试generate_reservation_number函数的行为
Test generate_reservation_number function
"""
import os
import sys
from pathlib import Path
from datetime import datetime

# 获取项目根目录
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# 导入函数
from backend.utils.code_generator import generate_reservation_number

def test_reservation_number():
    """测试预约编号生成函数"""
    # 获取单次预约编号
    regular_number = generate_reservation_number()
    print(f"单次预约编号: {regular_number}")
    
    # 测试给循环预约定义的版本
    try:
        # 获取当前日期
        now = datetime.now()
        date_str = now.strftime("%Y%m%d")
        prefix = f"RN-{date_str}"
        
        # 循环预约子预约编号格式是 RN-YYYYMMDD-XXXX-N
        # 这里我们模拟生成几个不同index的编号
        for i in range(1, 6):
            base_number = "1234"  # 循环预约的基础序号
            child_number = f"{prefix}-{base_number}-{i}"
            print(f"循环预约子预约编号 (index={i}): {child_number}")
        
        print("\n这表明循环预约的编号格式为：RN-YYYYMMDD-XXXX-N")
        print("其中 XXXX 是基础序号，N 是子预约的序号（从1开始递增）")
    except Exception as e:
        print(f"测试循环预约编号生成失败: {e}")
    
    # 查找定义覆盖的generate_reservation_number函数
    print("\n检查是否有自定义的generate_reservation_number函数:")
    for root, dirs, files in os.walk(os.path.join(ROOT_DIR, "backend")):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "def generate_reservation_number" in content and "current_date" in content and "index" in content:
                        print(f"找到定义: {file_path}")
                        lines = content.split("\n")
                        for i, line in enumerate(lines):
                            if "def generate_reservation_number" in line and "current_date" in line:
                                # 打印函数定义和几行实现
                                start = max(0, i - 1)
                                end = min(len(lines), i + 15)
                                print("\n".join(lines[start:end]))
                                print("...")
                                break

if __name__ == "__main__":
    test_reservation_number() 