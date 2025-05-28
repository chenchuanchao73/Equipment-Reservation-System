#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查询邮件模板表
Check email templates table
"""
import os
import sys
import sqlite3
import json

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def main():
    """主函数"""
    # 连接数据库
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'equipment_reservation.db')
    print(f"连接数据库: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 查询邮件模板
        cursor.execute("SELECT id, name, template_key, subject, language FROM email_templates")
        templates = cursor.fetchall()
        
        if templates:
            print(f"找到 {len(templates)} 个邮件模板:")
            for template in templates:
                print(f"ID: {template[0]}, 名称: {template[1]}, 键名: {template[2]}, 主题: {template[3]}, 语言: {template[4]}")
                
                # 检查特定的模板内容
                if template[2] == 'reservation_recurring_all_cancelled':
                    cursor.execute("SELECT subject, content_html FROM email_templates WHERE id = ?", (template[0],))
                    template_content = cursor.fetchone()
                    if template_content:
                        print(f"模板主题: {template_content[0]}")
                        print(f"模板内容前100个字符: {template_content[1][:100]}")
        else:
            print("未找到邮件模板")
            
        # 检查邮件日志中的reservation_recurring_all_cancelled
        cursor.execute("SELECT id, recipient, subject FROM email_logs WHERE event_type = 'reservation_recurring_all_cancelled' ORDER BY id DESC LIMIT 3")
        logs = cursor.fetchall()
        
        if logs:
            print(f"\n找到 {len(logs)} 个循环预约取消的邮件日志:")
            for log in logs:
                print(f"ID: {log[0]}, 收件人: {log[1]}, 主题: {log[2]}")
                
    except sqlite3.Error as e:
        print(f"查询失败: {e}")
    finally:
        conn.close()
        
    print("查询完成")

if __name__ == "__main__":
    main() 