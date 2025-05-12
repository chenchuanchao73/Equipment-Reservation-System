import os
import sys

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from backend.models.email import EmailTemplate, Base
from config import BASE_DIR

# 数据库路径
DB_PATH = os.path.join(BASE_DIR, 'equipment_reservation.db')
engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)
session = Session()

def upsert_template(template_key, name, subject, content_html, language="zh_CN"):
    tpl = session.query(EmailTemplate).filter_by(template_key=template_key, language=language).first()
    if tpl:
        tpl.name = name
        tpl.subject = subject
        tpl.content_html = content_html
    else:
        tpl = EmailTemplate(
            name=name,
            template_key=template_key,
            subject=subject,
            content_html=content_html,
            language=language
        )
        session.add(tpl)
    session.commit()

# 模板内容
single_created_html = '''
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>单次预约创建 / Single Reservation Created</title></head><body>
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
'''

recurring_created_html = '''
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>循环预约创建成功 / Recurring Reservation Created</title></head><body>
<h2>循环预约创建成功 / Recurring Reservation Created</h2>
<p>尊敬的 {{ reservation.user_name }}，您的循环设备预约已成功创建。<br>
Dear {{ reservation.user_name }}, your recurring equipment reservation has been created successfully.</p>
<table border="1" cellpadding="6" style="border-collapse:collapse;">
<tr><th>预约编号 / Reservation Code</th><td>{{ reservation.reservation_code }}</td></tr>
<tr><th>设备名称 / Equipment Name</th><td>{{ reservation.equipment_name }}</td></tr>
<tr><th>预约时间范围 / Reservation Date Range</th><td>{{ reservation.start_date }} ~ {{ reservation.end_date }}</td></tr>
<tr><th>重复规则 / Recurrence Rule</th><td>{{ reservation.recurrence_rule }}</td></tr>
<tr><th>每天预约时间 / Time Each Day</th><td>{{ reservation.start_time }} ~ {{ reservation.end_time }}</td></tr>
<tr><th>状态 / Status</th><td>{{ reservation.status }}</td></tr>
</table>
<p>如有任何问题，请联系管理员。<br>
If you have any questions, please contact the administrator.</p>
</body></html>
'''

single_cancelled_html = '''
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>单次预约取消 / Single Reservation Cancelled</title></head><body>
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
'''

recurring_cancelled_html = '''
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>循环子预约取消 / Recurring Child Reservation Cancelled</title></head><body>
<h2>循环预约子预约取消 / Recurring Child Reservation Cancelled</h2>
<p style='color:#d9534f;font-weight:bold;'>您本次取消的是循环预约中的某一次子预约（见下方详细信息）<br>
This cancellation is for a single occurrence of your recurring reservation (see details below)</p>
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
'''

recurring_all_cancelled_html = '''
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>循环预约已取消 / Recurring Reservation Cancelled</title></head><body>
<h2>循环预约已取消 / Recurring Reservation Cancelled</h2>
<p style='color:#d9534f;font-weight:bold;'>重要通知：您的整个循环预约已被取消，包括所有未来的子预约！<br>
Important Notice: Your entire recurring reservation has been cancelled, including all future occurrences!</p>
<table border=1 cellpadding=6>
    <tr><th>预约编号 / Reservation Code</th><td>{{ reservation.reservation_code }}</td></tr>
    <tr><th>设备名称 / Equipment Name</th><td>{{ reservation.equipment_name }}</td></tr>
    <tr><th>循环模式 / Recurring Pattern</th><td>{{ reservation.pattern_type }}</td></tr>
    <tr><th>开始日期 / Start Date</th><td>{{ reservation.start_date }}</td></tr>
    <tr><th>结束日期 / End Date</th><td>{{ reservation.end_date }}</td></tr>
    <tr><th>状态 / Status</th><td>{{ reservation.status }}</td></tr>
</table>
<p>此循环预约下的所有子预约都已被取消。如需重新预约，请重新创建预约。<br>
All child reservations under this recurring reservation have been cancelled. If you need to make a new reservation, please create a new one.</p>
<p>如有任何问题，请联系管理员。<br>If you have any questions, please contact the administrator.</p>
</body></html>
'''

upsert_template('reservation_single_created', '单次预约创建', '单次预约创建成功 / Single Reservation Created', single_created_html)
upsert_template('reservation_recurring_created', '循环预约创建', '循环预约创建成功 / Recurring Reservation Created', recurring_created_html)
upsert_template('reservation_single_cancelled', '单次预约取消', '单次预约取消 / Single Reservation Cancelled', single_cancelled_html)
upsert_template('reservation_recurring_cancelled', '循环预约子预约取消', '循环预约子预约取消 / Recurring Child Reservation Cancelled', recurring_cancelled_html)
upsert_template('reservation_recurring_all_cancelled', '循环预约取消', '循环预约已取消 / Recurring Reservation Cancelled', recurring_all_cancelled_html)

print('邮件模板已同步到数据库！')