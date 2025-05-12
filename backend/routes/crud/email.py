"""
邮件设置CRUD操作
Email settings CRUD operations
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.database import get_db
from backend.models.email import EmailSettings, EmailTemplate, EmailLog
from backend.schemas.email import (
    EmailSettingsCreate, EmailSettings as EmailSettingsSchema,
    EmailTemplateCreate, EmailTemplate as EmailTemplateSchema,
    EmailLog as EmailLogSchema, PaginatedEmailLogs
)
from backend.routes.auth import get_current_admin

# 设置日志
logger = logging.getLogger(__name__)

# 创建路由
router = APIRouter()

# 邮件设置CRUD操作
@router.get("/settings", response_model=EmailSettingsSchema)
async def get_email_settings(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """获取邮件设置"""
    email_settings = db.query(EmailSettings).first()
    if not email_settings:
        # 创建默认设置
        email_settings = EmailSettings(
            smtp_server="smtp.example.com",
            smtp_port=587,
            sender_email="your_email@example.com",
            sender_name="设备预定系统",
            smtp_username="your_email@example.com",
            smtp_password="your_email_password",
            use_ssl=True,
            enabled=False
        )
        db.add(email_settings)
        db.commit()
        db.refresh(email_settings)

    return email_settings

@router.post("/settings", response_model=EmailSettingsSchema)
async def create_or_update_email_settings(
    settings: EmailSettingsCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """创建或更新邮件设置"""
    email_settings = db.query(EmailSettings).first()
    if email_settings:
        # 更新现有设置
        for key, value in settings.dict().items():
            setattr(email_settings, key, value)
    else:
        # 创建新设置
        email_settings = EmailSettings(**settings.dict())
        db.add(email_settings)

    try:
        db.commit()
        db.refresh(email_settings)
        return email_settings
    except Exception as e:
        db.rollback()
        logger.error(f"更新邮件设置失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新邮件设置失败: {e}")

# 邮件模板CRUD操作
@router.get("/templates", response_model=List[EmailTemplateSchema])
async def get_email_templates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """获取邮件模板列表（自动初始化4个双语模板）"""
    templates = db.query(EmailTemplate).offset(skip).limit(limit).all()

    # 如果没有模板，自动插入4个双语模板
    if db.query(EmailTemplate).count() == 0:
        default_templates = [
            EmailTemplate(
                name="设备预定创建通知 / Reservation Created",
                template_key="reservation_created",
                subject="设备预约已确认 / Your Equipment Reservation is Confirmed",
                content_html="""
                    <p>尊敬的 {{ reservation.user_name }}，您的设备预约已确认。<br>
                    Dear {{ reservation.user_name }}, your equipment reservation is confirmed.</p>
                    <p>设备：{{ reservation.equipment_name }}<br>
                    Equipment: {{ reservation.equipment_name }}</p>
                    <p>时间：{{ reservation.start_datetime }} ~ {{ reservation.end_datetime }}<br>
                    Time: {{ reservation.start_datetime }} ~ {{ reservation.end_datetime }}</p>
                    <p>预约码：{{ reservation.reservation_code }}<br>
                    Reservation Code: {{ reservation.reservation_code }}</p>
                """,
                language="all"
            ),
            EmailTemplate(
                name="设备预定取消通知 / Reservation Cancelled",
                template_key="reservation_cancelled",
                subject="设备预约已取消 / Your Equipment Reservation is Cancelled",
                content_html="""
                    <p>尊敬的 {{ reservation.user_name }}，您的设备预约已取消。<br>
                    Dear {{ reservation.user_name }}, your equipment reservation has been cancelled.</p>
                    <p>设备：{{ reservation.equipment_name }}<br>
                    Equipment: {{ reservation.equipment_name }}</p>
                    <p>时间：{{ reservation.start_datetime }} ~ {{ reservation.end_datetime }}<br>
                    Time: {{ reservation.start_datetime }} ~ {{ reservation.end_datetime }}</p>
                    <p>预约码：{{ reservation.reservation_code }}<br>
                    Reservation Code: {{ reservation.reservation_code }}</p>
                """,
                language="all"
            ),
            EmailTemplate(
                name="设备循环预定创建通知 / Recurring Reservation Created",
                template_key="recurring_reservation_created",
                subject="循环预约已创建 / Your Recurring Equipment Reservation is Created",
                content_html="""
                    <p>尊敬的 {{ reservation.user_name }}，您的设备循环预约已创建。<br>
                    Dear {{ reservation.user_name }}, your recurring equipment reservation is created.</p>
                    <p>设备：{{ reservation.equipment_name }}<br>
                    Equipment: {{ reservation.equipment_name }}</p>
                    <p>循环时间：{{ reservation.start_datetime }} ~ {{ reservation.end_datetime }}<br>
                    Recurring Time: {{ reservation.start_datetime }} ~ {{ reservation.end_datetime }}</p>
                    <p>循环预约编号：{{ reservation.recurring_code }}<br>
                    Recurring Reservation Code: {{ reservation.recurring_code }}</p>
                """,
                language="all"
            ),
            EmailTemplate(
                name="设备循环预定（子项）取消通知 / Recurring Reservation (Child) Cancelled",
                template_key="recurring_reservation_cancelled",
                subject="循环预约子项已取消 / A Child of Your Recurring Reservation is Cancelled",
                content_html="""
                    <p>尊敬的 {{ reservation.user_name }}，您的设备循环预约中的某一子项已取消。<br>
                    Dear {{ reservation.user_name }}, a child reservation of your recurring equipment reservation has been cancelled.</p>
                    <p>设备：{{ reservation.equipment_name }}<br>
                    Equipment: {{ reservation.equipment_name }}</p>
                    <p>子项时间：{{ reservation.start_datetime }} ~ {{ reservation.end_datetime }}<br>
                    Child Time: {{ reservation.start_datetime }} ~ {{ reservation.end_datetime }}</p>
                    <p>循环预约编号：{{ reservation.recurring_code }}<br>
                    Recurring Reservation Code: {{ reservation.recurring_code }}</p>
                """,
                language="all"
            ),
        ]
        db.add_all(default_templates)
        db.commit()
        templates = db.query(EmailTemplate).offset(skip).limit(limit).all()

    return templates

@router.get("/templates/{template_id}", response_model=EmailTemplateSchema)
async def get_email_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """获取邮件模板详情"""
    template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="邮件模板未找到")
    return template

@router.post("/templates", response_model=EmailTemplateSchema)
async def create_email_template(
    template: EmailTemplateCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """创建邮件模板"""
    # 检查模板键名是否已存在
    existing_template = db.query(EmailTemplate).filter(
        EmailTemplate.template_key == template.template_key,
        EmailTemplate.language == template.language
    ).first()

    if existing_template:
        raise HTTPException(status_code=400, detail=f"模板键名'{template.template_key}'和语言'{template.language}'的组合已存在")

    new_template = EmailTemplate(**template.dict())
    db.add(new_template)

    try:
        db.commit()
        db.refresh(new_template)
        return new_template
    except Exception as e:
        db.rollback()
        logger.error(f"创建邮件模板失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建邮件模板失败: {e}")

@router.put("/templates/{template_id}", response_model=EmailTemplateSchema)
async def update_email_template(
    template_id: int,
    template: EmailTemplateCreate,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """更新邮件模板"""
    existing_template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
    if not existing_template:
        raise HTTPException(status_code=404, detail="邮件模板未找到")

    # 检查是否有其他模板使用相同的键名和语言组合
    duplicate = db.query(EmailTemplate).filter(
        EmailTemplate.template_key == template.template_key,
        EmailTemplate.language == template.language,
        EmailTemplate.id != template_id
    ).first()

    if duplicate:
        raise HTTPException(status_code=400, detail=f"模板键名'{template.template_key}'和语言'{template.language}'的组合已存在")

    # 更新模板
    for key, value in template.dict().items():
        setattr(existing_template, key, value)

    try:
        db.commit()
        db.refresh(existing_template)
        return existing_template
    except Exception as e:
        db.rollback()
        logger.error(f"更新邮件模板失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新邮件模板失败: {e}")

@router.delete("/templates/{template_id}")
async def delete_email_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """删除邮件模板"""
    template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="邮件模板未找到")

    try:
        db.delete(template)
        db.commit()
        return {"message": "邮件模板已删除"}
    except Exception as e:
        db.rollback()
        logger.error(f"删除邮件模板失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除邮件模板失败: {e}")

@router.delete("/templates")
async def clear_email_templates(
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """清空所有邮件模板"""
    try:
        count = db.query(EmailTemplate).delete(synchronize_session=False)
        db.commit()
        return {"message": f"已清空 {count} 条邮件模板"}
    except Exception as e:
        db.rollback()
        logger.error(f"清空邮件模板失败: {e}")
        raise HTTPException(status_code=500, detail=f"清空邮件模板失败: {e}")

# 邮件日志CRUD操作
@router.get("/logs", response_model=PaginatedEmailLogs)
async def get_email_logs(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    event_type: Optional[str] = None,
    recipient: Optional[str] = None,
    reservation_code: Optional[str] = None,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """获取邮件日志列表"""
    query = db.query(EmailLog)

    # 应用过滤条件
    if status:
        query = query.filter(EmailLog.status == status)
    if event_type:
        query = query.filter(EmailLog.event_type == event_type)
    if recipient:
        query = query.filter(EmailLog.recipient.ilike(f"%{recipient}%"))
    if reservation_code:
        query = query.filter(EmailLog.reservation_code == reservation_code)

    # 获取总数
    total = query.count()

    # 应用分页并按创建时间降序排序
    logs = query.order_by(desc(EmailLog.created_at)).offset(skip).limit(limit).all()

    return {"items": logs, "total": total}

@router.delete("/logs/{log_id}")
async def delete_email_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """删除邮件日志"""
    log = db.query(EmailLog).filter(EmailLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="邮件日志未找到")

    try:
        db.delete(log)
        db.commit()
        return {"message": "邮件日志已删除"}
    except Exception as e:
        db.rollback()
        logger.error(f"删除邮件日志失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除邮件日志失败: {e}")

@router.delete("/logs")
async def clear_email_logs(
    days: Optional[int] = Query(None, description="清除多少天前的日志，不提供则清除所有"),
    status: Optional[str] = Query(None, description="要清除的日志状态，例如 'success'或'failed'"),
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """清除邮件日志"""
    from datetime import datetime, timedelta

    query = db.query(EmailLog)

    # 应用过滤条件
    if days:
        cutoff_date = datetime.now() - timedelta(days=days)
        query = query.filter(EmailLog.created_at < cutoff_date)

    if status:
        query = query.filter(EmailLog.status == status)

    try:
        # 获取要删除的日志数量
        count = query.count()

        # 执行删除
        query.delete(synchronize_session=False)
        db.commit()

        return {"message": f"已清除 {count} 条邮件日志"}
    except Exception as e:
        db.rollback()
        logger.error(f"清除邮件日志失败: {e}")
        raise HTTPException(status_code=500, detail=f"清除邮件日志失败: {e}")

# 其他有用的端点
@router.get("/templates/by-key/{template_key}")
async def get_template_by_key(
    template_key: str,
    language: Optional[str] = "zh_CN",
    db: Session = Depends(get_db),
    current_admin = Depends(get_current_admin)
):
    """根据键名获取模板"""
    template = db.query(EmailTemplate).filter(
        EmailTemplate.template_key == template_key,
        EmailTemplate.language == language
    ).first()

    if not template:
        # 尝试获取默认语言的模板
        if language != "zh_CN":
            template = db.query(EmailTemplate).filter(
                EmailTemplate.template_key == template_key,
                EmailTemplate.language == "zh_CN"
            ).first()

        if not template:
            raise HTTPException(status_code=404, detail="邮件模板未找到")

    return template

@router.post("/test")
async def test_email_settings(
    smtp_server: str = Body(...),
    smtp_port: int = Body(...),
    sender_email: str = Body(...),
    sender_name: str = Body(...),
    smtp_username: str = Body(...),
    smtp_password: str = Body(...),
    cc_list: str = Body(""),
    bcc_list: str = Body(""),
    use_ssl: bool = Body(...),
    to_email: str = Body(..., embed=True),
    db: Session = Depends(get_db),
):
    """
    测试邮件发送，并写入日志
    """
    import smtplib
    from email.mime.text import MIMEText

    status = "success"
    error_message = None
    try:
        msg = MIMEText("这是一封测试邮件（This is a test email）", "plain", "utf-8")
        msg["Subject"] = "测试邮件"
        msg["From"] = f"{sender_name} <{sender_email}>"
        msg["To"] = to_email

        # 处理抄送人
        cc_recipients = []
        if cc_list:
            cc_emails = [email.strip() for email in cc_list.split(',') if email.strip()]
            if cc_emails:
                msg["Cc"] = ", ".join(cc_emails)
                cc_recipients = cc_emails

        # 处理密送人
        bcc_recipients = []
        if bcc_list:
            bcc_emails = [email.strip() for email in bcc_list.split(',') if email.strip()]
            if bcc_emails:
                msg["Bcc"] = ", ".join(bcc_emails)
                bcc_recipients = bcc_emails

        # 收件人列表包括主收件人、抄送人和密送人
        all_recipients = [to_email] + cc_recipients + bcc_recipients

        if use_ssl:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=10)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
            server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender_email, all_recipients, msg.as_string())
        server.quit()

        cc_info = f", 已抄送给 {len(cc_recipients)} 人" if cc_recipients else ""
        bcc_info = f", 已密送给 {len(bcc_recipients)} 人" if bcc_recipients else ""
        result = {"success": True, "message": f"测试邮件发送成功！{cc_info}{bcc_info}"}
    except Exception as e:
        status = "failed"
        error_message = str(e)
        result = {"success": False, "message": f"测试邮件发送失败: {e}"}

    # 写入日志
    try:
        log = EmailLog(
            recipient=to_email,
            subject="测试邮件",
            event_type="test",
            status=status,
            error_message=error_message,
            content_html="这是一封测试邮件（This is a test email）"
        )
        db.add(log)
        db.commit()
    except Exception as log_err:
        db.rollback()
        logger.error(f"写入测试邮件日志失败: {log_err}")

    return result