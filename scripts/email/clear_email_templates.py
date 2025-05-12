"""
一键清空 email_templates 表
Usage: python clear_email_templates.py
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.database import SessionLocal
from backend.models.email import EmailTemplate

def main():
    session = SessionLocal()
    try:
        count = session.query(EmailTemplate).delete(synchronize_session=False)
        session.commit()
        print(f"已清空 {count} 条邮件模板")
    except Exception as e:
        session.rollback()
        print(f"清空失败: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    main() 