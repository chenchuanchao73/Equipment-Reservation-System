"""
邮件发送工具
Email sender
"""
import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List

# 设置日志
logger = logging.getLogger(__name__)

# 导入配置
from config import (
    BASE_DIR, EMAIL_SENDER, EMAIL_PASSWORD,
    EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT
)

# 导入数据库模型
from backend.models.email import EmailSettings, EmailTemplate, EmailLog
from backend.database import get_db

# 设置Jinja2环境
templates_dir = os.path.join(BASE_DIR, "backend", "templates", "emails")
os.makedirs(templates_dir, exist_ok=True)
env = Environment(loader=FileSystemLoader(templates_dir))

async def send_email(to_email, subject, html_content, text_content=None, db: Session = None, event_type: str = None, reservation_code: str = None, reservation_number: str = None):
    """
    发送邮件
    Send email
    """
    if not to_email or not subject or not html_content:
        logger.error("邮件发送失败: 缺少必要参数")
        return False

    # 获取邮件设置
    smtp_server = EMAIL_SMTP_SERVER
    smtp_port = EMAIL_SMTP_PORT
    sender_email = EMAIL_SENDER
    sender_password = EMAIL_PASSWORD
    use_ssl = True
    cc_list = ""
    bcc_list = ""

    # 如果提供了数据库会话，尝试从数据库获取设置
    if db:
        try:
            email_settings = db.query(EmailSettings).filter(EmailSettings.enabled == True).first()
            if email_settings:
                smtp_server = email_settings.smtp_server
                smtp_port = email_settings.smtp_port
                sender_email = email_settings.sender_email
                sender_password = email_settings.smtp_password
                use_ssl = email_settings.use_ssl
                cc_list = email_settings.cc_list or ""
                bcc_list = email_settings.bcc_list or ""
        except Exception as e:
            logger.warning(f"从数据库获取邮件设置失败: {e}，使用默认配置")

    try:
        # 创建邮件
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender_email
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

        # 添加纯文本内容
        if text_content:
            msg.attach(MIMEText(text_content, "plain", "utf-8"))

        # 添加HTML内容
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        # 发送邮件
        if use_ssl:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()

        server.login(sender_email, sender_password)

        # 收件人列表包括主收件人、抄送人和密送人
        all_recipients = [to_email] + cc_recipients + bcc_recipients
        server.send_message(msg)
        server.quit()

        logger.info(f"邮件发送成功: 主收件人={to_email}, 抄送={cc_recipients}, 密送={bcc_recipients}")

        # 记录发送日志
        if db:
            try:
                email_log = EmailLog(
                    recipient=to_email,
                    subject=subject,
                    event_type=event_type,
                    status="success",
                    reservation_code=reservation_code,
                    reservation_number=reservation_number,
                    content_html=html_content
                )
                db.add(email_log)
                db.commit()
            except Exception as e:
                logger.error(f"记录邮件日志失败: {e}")
                db.rollback()

        return True
    except Exception as e:
        error_message = str(e)
        logger.error(f"邮件发送失败: {error_message}")

        # 记录失败日志
        if db:
            try:
                email_log = EmailLog(
                    recipient=to_email,
                    subject=subject,
                    event_type=event_type,
                    status="failed",
                    error_message=error_message,
                    reservation_code=reservation_code,
                    reservation_number=reservation_number,
                    content_html=html_content
                )
                db.add(email_log)
                db.commit()
            except Exception as log_error:
                logger.error(f"记录邮件日志失败: {log_error}")
                db.rollback()

        return False

async def send_reservation_confirmation(to_email, reservation_data, lang="zh_CN", db: Session = None, is_recurring=False, is_child=False, parent_info=None):
    """
    发送预定确认邮件（支持单次/循环/子循环预约）
    """
    try:
        reservation_data = {k: (v if v is not None else "") for k, v in reservation_data.items()}
        # 选择模板key
        if is_recurring:
            template_key = "reservation_recurring_created"
        else:
            template_key = "reservation_single_created"
        subject = None
        html_content = None
        if db:
            subject, html_content = await get_email_template(template_key, lang, db)
        if not html_content:
            template_name = f"{template_key}_{lang}.html"
            if not os.path.exists(os.path.join(templates_dir, template_name)):
                template_name = f"{template_key}.html"
                if not os.path.exists(os.path.join(templates_dir, template_name)):
                    # 生成默认模板
                    with open(os.path.join(templates_dir, template_name), "w", encoding="utf-8") as f:
                        if is_recurring:
                            f.write("""
                            <!DOCTYPE html>
                            <html><head><meta charset=\"UTF-8\"><title>循环预约创建 / Recurring Reservation Created</title></head><body>
                            <h2>循环预约创建成功 / Recurring Reservation Created</h2>
                            <p>尊敬的 {{ reservation.user_name }}，您的循环设备预约已成功创建。<br>
                            Dear {{ reservation.user_name }}, your recurring equipment reservation has been created successfully.</p>
                            <table border=1 cellpadding=6>
                                <tr><th>循环预约编号 / Recurring Code</th><td>{{ reservation.reservation_code }}</td></tr>
                                <tr><th>设备名称 / Equipment Name</th><td>{{ reservation.equipment_name }}</td></tr>
                                <tr><th>预约周期 / Pattern</th><td>{{ reservation.pattern_type }}</td></tr>
                                <tr><th>开始日期 / Start Date</th><td>{{ reservation.start_datetime }}</td></tr>
                                <tr><th>结束日期 / End Date</th><td>{{ reservation.end_datetime }}</td></tr>
                                <tr><th>状态 / Status</th><td>{{ reservation.status }}</td></tr>
                            </table>
                            <p>如有任何问题，请联系管理员。<br>If you have any questions, please contact the administrator.</p>
                            </body></html>
                            """)
                        else:
                            f.write("""
                            <!DOCTYPE html>
                            <html><head><meta charset=\"UTF-8\"><title>单次预约创建 / Single Reservation Created</title></head><body>
                            <h2>单次预约创建成功 / Single Reservation Created</h2>
                            <p>尊敬的 {{ reservation.user_name }}，您的设备预约已成功创建。<br>
                            Dear {{ reservation.user_name }}, your equipment reservation has been created successfully.</p>
                            <table border=1 cellpadding=6>
                                <tr><th>预约编号 / Reservation Code</th><td>{{ reservation.reservation_code }}</td></tr>
                                <tr><th>设备名称 / Equipment Name</th><td>{{ reservation.equipment_name }}</td></tr>
                                <tr><th>开始时间 / Start Time</th><td>{{ reservation.start_datetime }}</td></tr>
                                <tr><th>结束时间 / End Time</th><td>{{ reservation.end_datetime }}</td></tr>
                                <tr><th>状态 / Status</th><td>{{ reservation.status }}</td></tr>
                            </table>
                            <p>如有任何问题，请联系管理员。<br>If you have any questions, please contact the administrator.</p>
                            </body></html>
                            """)
            template = env.get_template(template_name)
            html_content = template.render(reservation=reservation_data, parent=parent_info)
            subject = "循环预约创建 / Recurring Reservation Created" if is_recurring else "单次预约创建 / Single Reservation Created"
        else:
            template = env.from_string(html_content)
            html_content = template.render(reservation=reservation_data, parent=parent_info)
        return await send_email(
            to_email,
            subject,
            html_content,
            db=db,
            event_type=template_key,
            reservation_code=reservation_data.get("reservation_code"),
            reservation_number=reservation_data.get("reservation_number")
        )
    except Exception as e:
        logger.error(f"发送预定确认邮件失败: {e}")
        return False

async def send_reservation_update(to_email, reservation_data, lang="zh_CN", db: Session = None):
    """
    发送预定更新邮件
    Send reservation update email
    """
    try:
        # 修复：将None值转为''，避免模板渲染为空
        reservation_data = {k: (v if v is not None else "") for k, v in reservation_data.items()}
        template_key = "reservation_updated"
        subject = None
        html_content = None
        if db:
            subject, html_content = await get_email_template(template_key, lang, db)
        if not html_content:
            template_name = f"reservation_updated_{lang}.html"
            if not os.path.exists(os.path.join(templates_dir, template_name)):
                template_name = "reservation_updated.html"
                if not os.path.exists(os.path.join(templates_dir, template_name)):
                    with open(os.path.join(templates_dir, template_name), "w", encoding="utf-8") as f:
                        f.write("""
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <meta charset=\"UTF-8\">
                            <title>设备预定更新 / Reservation Update</title>
                            <style>
                                body { font-family: Arial, sans-serif; line-height: 1.6; }
                                .container { width: 100%; max-width: 600px; margin: 0 auto; }
                                .header { background-color: #2196F3; color: white; padding: 10px; text-align: center; }
                                .content { padding: 20px; }
                                .footer { background-color: #f1f1f1; padding: 10px; text-align: center; font-size: 12px; }
                                table { width: 100%; border-collapse: collapse; }
                                table, th, td { border: 1px solid #ddd; }
                                th, td { padding: 10px; text-align: left; }
                                th { background-color: #f2f2f2; }
                            </style>
                        </head>
                        <body>
                            <div class=\"container\">
                                <div class=\"header\">
                                    <h1>设备预定更新 / Reservation Update</h1>
                                </div>
                                <div class=\"content\">
                                    <p>尊敬的 {{ reservation.user_name }}，您的设备预定信息已更新。<br>
                                    Dear {{ reservation.user_name }}, your equipment reservation information has been updated.</p>
                                    <table>
                                        <tr><th>预定编号 / Reservation Code</th><td>{{ reservation.reservation_code }}</td></tr>
                                        <tr><th>设备名称 / Equipment Name</th><td>{{ reservation.equipment_name }}</td></tr>
                                        <tr><th>开始时间 / Start Time</th><td>{{ reservation.start_datetime }}</td></tr>
                                        <tr><th>结束时间 / End Time</th><td>{{ reservation.end_datetime }}</td></tr>
                                        <tr><th>状态 / Status</th><td>{{ reservation.status }}</td></tr>
                                    </table>
                                    <p>如有任何问题，请联系管理员。<br>
                                    If you have any questions, please contact the administrator.</p>
                                    <p>感谢您使用HTNIA设备预定系统！<br>
                                    Thank you for using the HTNIA Equipment Reservation System!</p>
                                </div>
                                <div class=\"footer\">
                                    <p>此邮件由系统自动发送，请勿回复。<br>This email was sent automatically by the system, please do not reply.</p>
                                </div>
                            </div>
                        </body>
                        </html>
                        """)
            template = env.get_template(template_name)
            html_content = template.render(
                reservation=reservation_data,
                site_url=reservation_data.get("site_url", ""),
                current_year=datetime.now().year
            )
            subject = "设备预定更新 / Reservation Update"
        else:
            template = env.from_string(html_content)
            html_content = template.render(
                reservation=reservation_data,
                site_url=reservation_data.get("site_url", ""),
                current_year=datetime.now().year
            )
        return await send_email(
            to_email,
            subject,
            html_content,
            db=db,
            event_type="reservation_updated",
            reservation_code=reservation_data.get("reservation_code"),
            reservation_number=reservation_data.get("reservation_number")
        )
    except Exception as e:
        logger.error(f"发送预定更新邮件失败: {e}")
        return False

async def send_reservation_cancellation(to_email, reservation_data, lang="zh_CN", db: Session = None, is_recurring=False, is_child=False, parent_info=None):
    """
    发送预定取消邮件（支持单次/循环/子循环预约）
    """
    try:
        reservation_data = {k: (v if v is not None else "") for k, v in reservation_data.items()}
        if is_recurring:
            if is_child:
                template_key = "reservation_recurring_cancelled"
            else:
                template_key = "reservation_recurring_all_cancelled"
        else:
            template_key = "reservation_single_cancelled"
        subject = None
        html_content = None
        logger.info(f"[邮件发送] 类型: {'循环子预约取消' if is_recurring and is_child else ('循环预约取消' if is_recurring else '单次预约取消')}, 模板: {template_key}, 收件人: {to_email}, 预约码: {reservation_data.get('reservation_code')}, 预约序号: {reservation_data.get('reservation_number')}, is_recurring={is_recurring}, is_child={is_child}")
        if db:
            subject, html_content = await get_email_template(template_key, lang, db)
        if not html_content:
            template_name = f"{template_key}_{lang}.html"
            if not os.path.exists(os.path.join(templates_dir, template_name)):
                template_name = f"{template_key}.html"
                if not os.path.exists(os.path.join(templates_dir, template_name)):
                    with open(os.path.join(templates_dir, template_name), "w", encoding="utf-8") as f:
                        if is_recurring:
                            if is_child:
                                f.write("""
                                <!DOCTYPE html>
                                <html><head><meta charset=\"UTF-8\"><title>循环子预约取消 / Recurring Child Reservation Cancelled</title></head><body>
                                <h2>循环预约子预约取消 / Recurring Child Reservation Cancelled</h2>
                                <p style='color:#d9534f;font-weight:bold;'>您本次取消的是循环预约中的某一次子预约（见下方详细信息）<br>
                                This cancellation is for a single occurrence of your recurring reservation (see details below)</p>
                                <h3>父循环预约信息 / Parent Recurring Reservation</h3>
                                <table border=1 cellpadding=6>
                                    <tr><th>循环预约编号 / Recurring Code</th><td>{{ parent.reservation_code }}</td></tr>
                                    <tr><th>设备名称 / Equipment Name</th><td>{{ parent.equipment_name }}</td></tr>
                                    <tr><th>预约周期 / Pattern</th><td>{{ parent.pattern_type }}</td></tr>
                                    <tr><th>开始日期 / Start Date</th><td>{{ parent.start_datetime }}</td></tr>
                                    <tr><th>结束日期 / End Date</th><td>{{ parent.end_datetime }}</td></tr>
                                </table>
                                <h3>本次子预约信息 / This Occurrence</h3>
                                <table border=1 cellpadding=6>
                                    <tr><th>预约编号 / Reservation Code</th><td>{{ reservation.reservation_code }}</td></tr>
                                    <tr><th>设备名称 / Equipment Name</th><td>{{ reservation.equipment_name }}</td></tr>
                                    <tr><th>开始时间 / Start Time</th><td>{{ reservation.start_datetime }}</td></tr>
                                    <tr><th>结束时间 / End Time</th><td>{{ reservation.end_datetime }}</td></tr>
                                    <tr><th>状态 / Status</th><td>{{ reservation.status }}</td></tr>
                                </table>
                                <p>如有任何问题，请联系管理员。<br>If you have any questions, please contact the administrator.</p>
                                </body></html>
                                """)
                            else:
                                f.write("""
                                <!DOCTYPE html>
                                <html><head><meta charset=\"UTF-8\"><title>循环预约取消 / Recurring Reservation Cancelled</title></head><body>
                                <h2>循环预约取消 / Recurring Reservation Cancelled</h2>
                                <p>尊敬的 {{ reservation.user_name }}，您的循环设备预约已取消。<br>
                                Dear {{ reservation.user_name }}, your recurring equipment reservation has been cancelled.</p>
                                <table border=1 cellpadding=6>
                                    <tr><th>循环预约编号 / Recurring Code</th><td>{{ reservation.reservation_code }}</td></tr>
                                    <tr><th>设备名称 / Equipment Name</th><td>{{ reservation.equipment_name }}</td></tr>
                                    <tr><th>预约周期 / Pattern</th><td>{{ reservation.pattern_type }}</td></tr>
                                    <tr><th>开始日期 / Start Date</th><td>{{ reservation.start_datetime }}</td></tr>
                                    <tr><th>结束日期 / End Date</th><td>{{ reservation.end_datetime }}</td></tr>
                                    <tr><th>状态 / Status</th><td>{{ reservation.status }}</td></tr>
                                </table>
                                <p>如有任何问题，请联系管理员。<br>If you have any questions, please contact the administrator.</p>
                                </body></html>
                                """)
                        else:
                            f.write("""
                            <!DOCTYPE html>
                            <html><head><meta charset=\"UTF-8\"><title>单次预约取消 / Single Reservation Cancelled</title></head><body>
                            <h2>单次预约取消 / Single Reservation Cancelled</h2>
                            <p>尊敬的 {{ reservation.user_name }}，您的设备预约已取消。<br>
                            Dear {{ reservation.user_name }}, your equipment reservation has been cancelled.</p>
                            <table border=1 cellpadding=6>
                                <tr><th>预约编号 / Reservation Code</th><td>{{ reservation.reservation_code }}</td></tr>
                                <tr><th>设备名称 / Equipment Name</th><td>{{ reservation.equipment_name }}</td></tr>
                                <tr><th>开始时间 / Start Time</th><td>{{ reservation.start_datetime }}</td></tr>
                                <tr><th>结束时间 / End Time</th><td>{{ reservation.end_datetime }}</td></tr>
                                <tr><th>状态 / Status</th><td>{{ reservation.status }}</td></tr>
                            </table>
                            <p>如有任何问题，请联系管理员。<br>If you have any questions, please contact the administrator.</p>
                            </body></html>
                            """)
            template = env.get_template(template_name)
            html_content = template.render(reservation=reservation_data, parent=parent_info)
            if is_recurring and is_child:
                subject = "循环预约子预约取消 / Recurring Child Reservation Cancelled"
            elif is_recurring:
                subject = "循环预约取消 / Recurring Reservation Cancelled"
            else:
                subject = "单次预约取消 / Single Reservation Cancelled"
        else:
            # 这里增加debug log
            print("DEBUG: 渲染前模板内容:", repr(html_content))
            print("DEBUG: 渲染变量 reservation:", reservation_data)
            print("DEBUG: 渲染变量 parent:", parent_info)
            template = env.from_string(html_content)
            html_content = template.render(reservation=reservation_data, parent=parent_info)
            print("DEBUG: 渲染后邮件内容:", html_content)
        result = await send_email(
            to_email,
            subject,
            html_content,
            db=db,
            event_type=template_key,
            reservation_code=reservation_data.get("reservation_code"),
            reservation_number=reservation_data.get("reservation_number")
        )
        logger.info(f"[邮件发送结果] 类型: {'循环子预约取消' if is_recurring and is_child else ('循环预约取消' if is_recurring else '单次预约取消')}, 收件人: {to_email}, 结果: {'成功' if result else '失败'}")
        return result
    except Exception as e:
        logger.error(f"发送预定取消邮件失败: {e}")
        return False

async def send_reservation_reminder(to_email, reservation_data, lang="zh_CN", db: Session = None):
    """
    发送预定提醒邮件
    Send reservation reminder email
    """
    try:
        # 修复：将None值转为''，避免模板渲染为空
        reservation_data = {k: (v if v is not None else "") for k, v in reservation_data.items()}
        template_key = "reservation_reminder"
        subject = None
        html_content = None
        if db:
            subject, html_content = await get_email_template(template_key, lang, db)
        if not html_content:
            template_name = f"reservation_reminder_{lang}.html"
            if not os.path.exists(os.path.join(templates_dir, template_name)):
                template_name = "reservation_reminder.html"
                if not os.path.exists(os.path.join(templates_dir, template_name)):
                    with open(os.path.join(templates_dir, template_name), "w", encoding="utf-8") as f:
                        f.write("""
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <meta charset=\"UTF-8\">
                            <title>设备预定提醒 / Reservation Reminder</title>
                            <style>
                                body { font-family: Arial, sans-serif; line-height: 1.6; }
                                .container { width: 100%; max-width: 600px; margin: 0 auto; }
                                .header { background-color: #FF9800; color: white; padding: 10px; text-align: center; }
                                .content { padding: 20px; }
                                .footer { background-color: #f1f1f1; padding: 10px; text-align: center; font-size: 12px; }
                                table { width: 100%; border-collapse: collapse; }
                                table, th, td { border: 1px solid #ddd; }
                                th, td { padding: 10px; text-align: left; }
                                th { background-color: #f2f2f2; }
                            </style>
                        </head>
                        <body>
                            <div class=\"container\">
                                <div class=\"header\">
                                    <h1>设备预定提醒 / Reservation Reminder</h1>
                                </div>
                                <div class=\"content\">
                                    <p>尊敬的 {{ reservation.user_name }}，您的设备预约即将开始。<br>
                                    Dear {{ reservation.user_name }}, your equipment reservation will start soon.</p>
                                    <table>
                                        <tr><th>预定编号 / Reservation Code</th><td>{{ reservation.reservation_code }}</td></tr>
                                        <tr><th>设备名称 / Equipment Name</th><td>{{ reservation.equipment_name }}</td></tr>
                                        <tr><th>开始时间 / Start Time</th><td>{{ reservation.start_datetime }}</td></tr>
                                        <tr><th>结束时间 / End Time</th><td>{{ reservation.end_datetime }}</td></tr>
                                        <tr><th>状态 / Status</th><td>{{ reservation.status }}</td></tr>
                                    </table>
                                    <p>您可以使用以下二维码查询您的预定详情：<br>
                                    You can use the following QR code to check your reservation details:</p>
                                    {% if reservation.qrcode_url %}
                                    <p style=\"text-align: center;\">
                                        <img src=\"{{ reservation.qrcode_url }}\" alt=\"预定二维码\" style=\"max-width: 200px;\">
                                    </p>
                                    {% endif %}
                                </div>
                            </div>
                        </body>
                        </html>
                        """)
            template = env.get_template(template_name)
            html_content = template.render(
                reservation=reservation_data,
                site_url=reservation_data.get("site_url", ""),
                current_year=datetime.now().year
            )
            subject = "设备预定提醒 / Reservation Reminder"
        else:
            template = env.from_string(html_content)
            html_content = template.render(
                reservation=reservation_data,
                site_url=reservation_data.get("site_url", ""),
                current_year=datetime.now().year
            )
        return await send_email(
            to_email,
            subject,
            html_content,
            db=db,
            event_type="reservation_reminder",
            reservation_code=reservation_data.get("reservation_code"),
            reservation_number=reservation_data.get("reservation_number")
        )
    except Exception as e:
        logger.error(f"发送预定提醒邮件失败: {e}")
        return False

async def get_email_template(template_key: str, lang: str = "zh_CN", db: Session = None):
    """
    从数据库获取邮件模板，如果找不到则使用默认模板
    Get email template from database, use default template if not found
    """
    if not db:
        return None, None

    try:
        # 先查找指定语言的模板
        template = db.query(EmailTemplate).filter(
            EmailTemplate.template_key == template_key,
            EmailTemplate.language == lang
        ).first()

        # 如果找不到指定语言的模板，尝试查找默认语言(zh_CN)的模板
        if not template and lang != "zh_CN":
            template = db.query(EmailTemplate).filter(
                EmailTemplate.template_key == template_key,
                EmailTemplate.language == "zh_CN"
            ).first()

        # 如果找到了模板，返回内容
        if template:
            return template.subject, template.content_html

        return None, None
    except Exception as e:
        logger.error(f"获取邮件模板失败: {e}")
        return None, None
