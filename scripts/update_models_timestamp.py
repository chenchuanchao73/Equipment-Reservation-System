"""
更新模型文件中的时间戳生成逻辑
Update timestamp generation logic in model files
"""
import os
import re
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 模型文件目录
MODELS_DIR = os.path.join('backend', 'models')

# 替换模式
REPLACE_PATTERNS = [
    # 替换 default=func.now() 为 default=BeijingNow()
    (r'default=func\.now\(\)', 'default=BeijingNow()'),
    # 替换 default=func.now(), onupdate=func.now() 为 default=BeijingNow(), onupdate=BeijingNow()
    (r'default=func\.now\(\),\s*onupdate=func\.now\(\)', 'default=BeijingNow(), onupdate=BeijingNow()'),
]

def update_model_file(file_path):
    """更新单个模型文件"""
    print(f"处理文件: {file_path}")
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否需要添加导入语句
    if 'from backend.utils.db_utils import BeijingNow' not in content:
        # 添加导入语句
        import_pattern = r'from sqlalchemy import (.*?)(?=\n)'
        if re.search(import_pattern, content, re.DOTALL):
            # 如果已经有sqlalchemy导入，添加BeijingNow到导入列表
            content = re.sub(
                import_pattern,
                r'from sqlalchemy import \1\nfrom backend.utils.db_utils import BeijingNow',
                content,
                flags=re.DOTALL
            )
        else:
            # 如果没有sqlalchemy导入，添加新的导入语句
            content = re.sub(
                r'from sqlalchemy import (.*?)(?=\n)',
                r'from sqlalchemy import \1\nfrom backend.utils.db_utils import BeijingNow',
                content,
                flags=re.DOTALL
            )
    
    # 应用替换模式
    modified = False
    for pattern, replacement in REPLACE_PATTERNS:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            modified = True
    
    # 如果文件被修改，写回文件
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"已更新文件: {file_path}")
    else:
        print(f"文件无需更新: {file_path}")

def update_all_model_files():
    """更新所有模型文件"""
    # 确保模型目录存在
    if not os.path.exists(MODELS_DIR):
        print(f"错误: 模型目录不存在: {MODELS_DIR}")
        return
    
    # 遍历模型目录中的所有Python文件
    for filename in os.listdir(MODELS_DIR):
        if filename.endswith('.py'):
            file_path = os.path.join(MODELS_DIR, filename)
            update_model_file(file_path)

if __name__ == '__main__':
    print("开始更新模型文件...")
    update_all_model_files()
    print("模型文件更新完成。")
