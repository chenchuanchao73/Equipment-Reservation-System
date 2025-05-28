#!/usr/bin/env python
"""
检查并修复重复的预约序号
Check and fix duplicate reservation numbers
"""
import sys
import os
import logging
from pathlib import Path

# 获取项目根目录
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """主函数"""
    try:
        # 导入必要的模块
        from backend.database import SessionLocal
        from backend.utils.duplicate_checker import check_and_fix_duplicate_numbers
        
        logger.info("开始检查重复的预约序号...")
        
        # 创建数据库会话
        db = SessionLocal()
        
        try:
            # 检查并修复重复的预约序号
            fixed_count = check_and_fix_duplicate_numbers(db)
            
            if fixed_count > 0:
                logger.info(f"成功修复 {fixed_count} 个重复的预约序号")
            else:
                logger.info("没有发现重复的预约序号")
                
        finally:
            # 确保数据库连接被关闭
            db.close()
            
        logger.info("检查完成")
        
    except Exception as e:
        logger.error(f"检查重复预约序号时出错: {str(e)}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
