"""
物品预定系统全局配置文件
Equipment Reservation System global configuration
"""
import os
from pathlib import Path

# 项目根目录 / Project root directory
BASE_DIR = Path(__file__).resolve().parent

# 数据库设置 / Database settings
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'equipment_reservation.db')}"

# 语言设置 / Language settings
DEFAULT_LANGUAGE = "zh_CN"  # 默认语言 / Default language
SUPPORTED_LANGUAGES = ["zh_CN", "en"]  # 支持的语言 / Supported languages

# 应用设置 / Application settings
APP_NAME = {
    "zh_CN": "设备预定系统",
    "en": "Equipment Reservation System"
}
APP_DESCRIPTION = {
    "zh_CN": "学校IT部门设备预定系统",
    "en": "School IT Department Equipment Reservation System"
}

# 管理员密码 (请在生产环境中修改) / Admin password (please change in production)
ADMIN_PASSWORD = "admin123"

# 预定码长度 / Reservation code length
RESERVATION_CODE_LENGTH = 8

# 日志设置 / Logging settings
LOG_FILE = os.path.join(BASE_DIR, "logs", "app.log")
LOG_LEVEL = "INFO"

# 静态文件 / Static files
STATIC_URL = "/static/"
STATIC_DIR = os.path.join(BASE_DIR, "backend", "static")

# 模板文件 / Template files
TEMPLATES_DIR = os.path.join(BASE_DIR, "backend", "templates")

# 邮件设置 / Email settings
EMAIL_SENDER = "your_email@example.com"  # 发件人邮箱 / Sender email
EMAIL_PASSWORD = "your_email_password"   # 邮箱密码 / Email password
EMAIL_SMTP_SERVER = "smtp.example.com"   # SMTP服务器 / SMTP server
EMAIL_SMTP_PORT = 587                    # SMTP端口 / SMTP port

# JWT设置 / JWT settings
SECRET_KEY = "your-secret-key-here"  # 密钥 (请在生产环境中修改) / Secret key (please change in production)
ALGORITHM = "HS256"                  # 算法 / Algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 30     # 访问令牌过期时间 (分钟) / Access token expire time (minutes)

# Unsplash API设置 / Unsplash API settings
UNSPLASH_ACCESS_KEY = "your-unsplash-access-key"  # Unsplash访问密钥 / Unsplash access key
