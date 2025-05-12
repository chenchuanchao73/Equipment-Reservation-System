"""
打印 email_logs 表最近 20 条日志
Usage: python print_email_logs.py
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import SessionLocal
from backend.models.email import EmailLog

def main():
    session = SessionLocal()
    try:
        logs = session.query(EmailLog).order_by(EmailLog.created_at.desc()).limit(20).all()
        for log in logs:
            print(f"ID: {log.id}")
            print(f"  event_type: {log.event_type}")
            print(f"  subject: {log.subject}")
            print(f"  recipient: {log.recipient}")
            print(f"  status: {log.status}")
            print(f"  created_at: {log.created_at}")
            content = log.content_html or ''
            print(f"  content_html: {content[:100]}{'...' if len(content) > 100 else ''}")
            print("-" * 40)
    except Exception as e:
        print(f"查询失败: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    main() 