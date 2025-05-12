"""
邮件相关数据模型验证
Email related data model validation
"""
from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class EmailSettingsBase(BaseModel):
    """邮件设置基础模型"""
    smtp_server: str
    smtp_port: int
    sender_email: EmailStr
    sender_name: str
    smtp_username: str
    smtp_password: str
    cc_list: Optional[str] = ""
    bcc_list: Optional[str] = ""
    use_ssl: bool
    enabled: bool

class EmailSettingsCreate(EmailSettingsBase):
    """邮件设置创建模型"""
    pass

class EmailSettings(EmailSettingsBase):
    """邮件设置响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class EmailTemplateBase(BaseModel):
    """邮件模板基础模型"""
    name: str
    template_key: str
    subject: str
    content_html: str
    content_text: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    language: str = "zh_CN"

class EmailTemplateCreate(EmailTemplateBase):
    """邮件模板创建模型"""
    pass

class EmailTemplate(EmailTemplateBase):
    """邮件模板响应模型"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class EmailLogBase(BaseModel):
    """邮件日志基础模型"""
    recipient: EmailStr
    subject: str
    template_key: Optional[str] = None
    event_type: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    reservation_code: Optional[str] = None
    reservation_number: Optional[str] = None
    content_html: Optional[str] = None

class EmailLog(EmailLogBase):
    """邮件日志响应模型"""
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# 用于列表查询的分页响应模型
class PaginatedEmailLogs(BaseModel):
    """分页邮件日志响应模型"""
    items: List[EmailLog]
    total: int