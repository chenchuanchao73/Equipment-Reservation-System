#!/usr/bin/env python
"""
检查循环预约代码以找出子预约编号生成的实现
Inspect recurring reservation code to find out how child reservation numbers are generated
"""
import os
import sys
from pathlib import Path

# 获取项目根目录
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

def monkey_patch_test():
    """尝试打印循环预约子预约编号生成函数的调用"""
    # 导入相关模块
    import inspect
    import types
    from datetime import datetime, date
    from backend.utils.code_generator import generate_reservation_number
    
    # 定义一个追踪装饰器
    original_func = generate_reservation_number
    
    def traced_generate_number(*args, **kwargs):
        """追踪函数调用"""
        print(f"generate_reservation_number被调用，参数: {args}, 关键字参数: {kwargs}")
        
        # 如果传入的参数不符合原函数签名，尝试生成特殊的循环预约编号
        if len(args) >= 2 and isinstance(args[0], (date, datetime)) and isinstance(args[1], int):
            current_date = args[0]
            index = args[1]
            date_str = current_date.strftime("%Y%m%d")
            
            # 第一个子预约取基础编号
            if index == 1:
                # 生成基础编号（随机或从数据库获取）
                base_number = "8901"  # 循环预约案例中使用的基础编号
                print(f"为循环预约第1个子预约生成基础编号: {base_number}")
            else:
                # 后续子预约使用第一个的基础编号
                base_number = "8901"
                print(f"为循环预约后续子预约重用基础编号: {base_number}")
            
            # 格式: RN-YYYYMMDD-XXXX-N
            reservation_number = f"RN-{date_str}-{base_number}-{index}"
            print(f"生成循环预约子预约编号: {reservation_number}")
            return reservation_number
        
        # 否则调用原始函数
        result = original_func(*args, **kwargs)
        print(f"原始函数生成结果: {result}")
        return result
    
    # 打印原函数和我们推测的实现的签名比较
    print(f"原始函数签名: {inspect.signature(original_func)}")
    print(f"推测的循环预约子预约编号生成函数签名: (current_date, index)")
    
    print("\n这里是我们推测的循环预约子预约编号生成实现:")
    print("""
def generate_reservation_number(current_date, index):
    # 生成预约编号，current_date是日期，index是子预约序号
    date_str = current_date.strftime("%Y%m%d")
    
    # 第一个子预约生成基础编号，后续子预约使用相同基础编号
    if index == 1:
        # 生成一个基础编号
        base_number = "XXXX"  # 例如"8901"
    else:
        # 使用相同的基础编号
        base_number = "XXXX"  # 与第一个子预约相同
    
    # 格式: RN-YYYYMMDD-XXXX-N
    return f"RN-{date_str}-{base_number}-{index}"
    """)
    
    # 根据数据库中的例子推测
    print("\n根据数据库中的例子:")
    print("- RN-20250618-8901-1")
    print("- RN-20250623-8901-2")
    print("- RN-20250625-8901-3")
    print("- RN-20250630-8901-4")
    print("\n每个子预约使用所属日期YYYYMMDD，但共享相同的基础编号8901，尾部增加子预约序号1,2,3,4")

if __name__ == "__main__":
    monkey_patch_test() 