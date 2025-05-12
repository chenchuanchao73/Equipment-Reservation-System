"""
邮件相关模型
Email related models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, func
from backend.utils.db_utils import BeijingNow
from sqlalchemy.orm import relationship

from backend.database import Base

class EmailSettings(Base):
    """
    邮件设置模型类
    Email settings model class
    """
    __tablename__ = "email_settings"

    id = Column(Integer, primary_key=True, index=True)
    smtp_server = Column(String(100), nullable=False, default="smtp.example.com", comment="SMTP服务器")
    smtp_port = Column(Integer, nullable=False, default=587, comment="SMTP端口")
    sender_email = Column(String(100), nullable=False, default="your_email@example.com", comment="发件人邮箱")
    sender_name = Column(String(100), nullable=False, default="设备预定系统", comment="发件人名称")
    smtp_username = Column(String(100), nullable=False, default="your_email@example.com", comment="SMTP用户名")
    smtp_password = Column(String(100), nullable=False, default="your_email_password", comment="SMTP密码")
    cc_list = Column(Text, nullable=True, default="", comment="抄送人列表，多个邮箱用逗号分隔")
    bcc_list = Column(Text, nullable=True, default="", comment="密送人列表，多个邮箱用逗号分隔")
    use_ssl = Column(Boolean, default=True, comment="使用SSL")
    enabled = Column(Boolean, default=False, comment="是否启用邮件功能")
    created_at = Column(DateTime, default=BeijingNow(), comment="创建时间")
    updated_at = Column(DateTime, default=BeijingNow(), onupdate=BeijingNow(), comment="更新时间")

    def __repr__(self):
        return f"<EmailSettings {self.sender_email}>"

class EmailTemplate(Base):
    """
    邮件模板模型类
    Email template model class
    """
    __tablename__ = "email_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="模板名称")
    template_key = Column(String(100), nullable=False, unique=True, comment="模板键名")
    subject = Column(String(200), nullable=False, comment="邮件主题")
    content_html = Column(Text, nullable=False, comment="HTML内容")
    content_text = Column(Text, comment="纯文本内容")
    variables = Column(JSON, comment="可用变量")
    language = Column(String(10), default="zh_CN", comment="语言")
    created_at = Column(DateTime, default=BeijingNow(), comment="创建时间")
    updated_at = Column(DateTime, default=BeijingNow(), onupdate=BeijingNow(), comment="更新时间")

    def __repr__(self):
        return f"<EmailTemplate {self.name}>"

class EmailLog(Base):
    """
    邮件日志模型类
    Email log model class
    """
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, index=True)
    recipient = Column(String(100), nullable=False, comment="收件人")
    subject = Column(String(200), nullable=False, comment="邮件主题")
    template_key = Column(String(100), comment="使用的模板键名")
    event_type = Column(String(50), comment="事件类型(预定创建、取消等)")
    status = Column(String(20), default="success", comment="状态: success, failed")
    error_message = Column(Text, comment="错误信息")
    reservation_code = Column(String(20), comment="关联的预定码")
    reservation_number = Column(String(20), comment="关联的预约序号")
    created_at = Column(DateTime, default=BeijingNow(), comment="创建时间")
    content_html = Column(Text, comment="邮件内容HTML")

    def __repr__(self):
        return f"<EmailLog {self.id}: {self.recipient}>"