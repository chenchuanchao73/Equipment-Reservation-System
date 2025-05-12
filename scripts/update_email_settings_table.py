#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
更新邮件设置表，添加抄送人和密送人字段
Update email settings table to add CC and BCC fields
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# 添加项目根目录到Python路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# 导入数据库配置
from config import DATABASE_URL

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

def update_email_settings_table():
    """
    更新邮件设置表，添加抄送人和密送人字段
    """
    try:
        # 创建数据库引擎
        engine = create_engine(DATABASE_URL)

        # 检查cc_list字段是否已存在
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(email_settings)"))
            columns = [row[1] for row in result.fetchall()]

            # 如果cc_list字段不存在，添加它
            if "cc_list" not in columns:
                logger.info("添加cc_list字段到email_settings表")
                conn.execute(text("ALTER TABLE email_settings ADD COLUMN cc_list TEXT DEFAULT ''"))
            else:
                logger.info("cc_list字段已存在")

            # 如果bcc_list字段不存在，添加它
            if "bcc_list" not in columns:
                logger.info("添加bcc_list字段到email_settings表")
                conn.execute(text("ALTER TABLE email_settings ADD COLUMN bcc_list TEXT DEFAULT ''"))
            else:
                logger.info("bcc_list字段已存在")

        logger.info("邮件设置表更新成功")
        return True
    except SQLAlchemyError as e:
        logger.error(f"更新邮件设置表时出错: {e}")
        return False

if __name__ == "__main__":
    logger.info("开始更新邮件设置表...")
    if update_email_settings_table():
        logger.info("邮件设置表更新完成")
    else:
        logger.error("邮件设置表更新失败")
