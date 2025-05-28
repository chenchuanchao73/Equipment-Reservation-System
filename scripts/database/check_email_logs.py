#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查询邮件日志，检查带有Spam Warning的邮件
Check email logs for emails with Spam Warning
"""
import os
import sys
import sqlite3
import logging
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def main():
    """主函数"""
    # 设置日志
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, f'email_logs_check_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logging.info(f"日志文件: {log_file}")
    
    # 连接数据库
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'equipment_reservation.db')
    logging.info(f"连接数据库: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 查询邮件设置
        cursor.execute("SELECT id, smtp_server, smtp_port, sender_email, sender_name, enabled FROM email_settings")
        settings = cursor.fetchall()
        
        if settings:
            logging.info(f"找到 {len(settings)} 条邮件设置:")
            for setting in settings:
                logging.info(f"ID: {setting[0]}, SMTP服务器: {setting[1]}:{setting[2]}, 发件人: {setting[3]}({setting[4]}), 启用: {setting[5]}")
        else:
            logging.info("未找到邮件设置")
        
        # 查询带有Spam Warning的邮件
        cursor.execute("SELECT id, recipient, subject, event_type, status, reservation_code, created_at FROM email_logs WHERE subject LIKE '%Spam%' LIMIT 10")
        spam_emails = cursor.fetchall()
        
        if spam_emails:
            logging.info(f"找到 {len(spam_emails)} 封带有Spam Warning的邮件:")
            for email in spam_emails:
                logging.info(f"ID: {email[0]}, 收件人: {email[1]}, 主题: {email[2]}, 类型: {email[3]}, 状态: {email[4]}, 预约码: {email[5]}, 时间: {email[6]}")
        else:
            logging.info("未找到带有Spam Warning的邮件")
        
        # 查询取消类型的邮件
        cursor.execute("SELECT id, recipient, subject, event_type, status, reservation_code, created_at FROM email_logs WHERE event_type LIKE '%cancelled%' OR event_type LIKE '%cancel%' ORDER BY id DESC LIMIT 10")
        cancel_emails = cursor.fetchall()
        
        if cancel_emails:
            logging.info(f"找到 {len(cancel_emails)} 封取消类型的邮件:")
            for email in cancel_emails:
                logging.info(f"ID: {email[0]}, 收件人: {email[1]}, 主题: {email[2]}, 类型: {email[3]}, 状态: {email[4]}, 预约码: {email[5]}, 时间: {email[6]}")
                
                # 检查这个邮件的内容
                cursor.execute("SELECT content_html FROM email_logs WHERE id = ?", (email[0],))
                content = cursor.fetchone()
                if content and content[0]:
                    logging.info(f"邮件内容前100个字符: {content[0][:100]}")
                else:
                    logging.info("邮件内容为空")
        else:
            logging.info("未找到取消类型的邮件")
        
        # 查询不同类型的邮件计数
        cursor.execute("SELECT event_type, COUNT(*) FROM email_logs GROUP BY event_type")
        email_counts = cursor.fetchall()
        
        if email_counts:
            logging.info("各类型邮件数量:")
            for count in email_counts:
                logging.info(f"类型: {count[0]}, 数量: {count[1]}")
        
        # 查询邮件模板
        cursor.execute("SELECT id, name, template_key, subject, language FROM email_templates")
        templates = cursor.fetchall()
        
        if templates:
            logging.info(f"找到 {len(templates)} 个邮件模板:")
            for template in templates:
                logging.info(f"ID: {template[0]}, 名称: {template[1]}, 键名: {template[2]}, 主题: {template[3]}, 语言: {template[4]}")
        else:
            logging.info("未找到邮件模板")
        
    except sqlite3.Error as e:
        logging.error(f"查询失败: {e}")
    finally:
        conn.close()
        
    logging.info(f"查询完成，结果已保存到: {log_file}")
    print(f"查询完成，结果已保存到: {log_file}")

if __name__ == "__main__":
    main() 