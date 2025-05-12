"""
国际化支持
Internationalization support
"""
import os
import json
import logging
from typing import Callable, Dict, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# 设置日志
logger = logging.getLogger(__name__)

# 导入配置
from config import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES

# 全局变量
_current_locale = DEFAULT_LANGUAGE
_translations = {}

# 国际化中间件
class I18nMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        # 从Cookie中获取语言设置
        global _current_locale
        language = request.cookies.get("language", DEFAULT_LANGUAGE)

        # 如果语言不受支持，则使用默认语言
        if language not in SUPPORTED_LANGUAGES:
            language = DEFAULT_LANGUAGE

        # 设置当前语言
        _current_locale = language

        # 继续处理请求
        response = await call_next(request)
        return response

def setup_i18n():
    """设置国际化"""
    try:
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # 设置翻译文件目录
        translations_dir = os.path.join(current_dir, "translations")

        # 确保目录存在
        if not os.path.exists(translations_dir):
            os.makedirs(translations_dir)

        # 创建默认翻译文件（如果不存在）
        for lang in SUPPORTED_LANGUAGES:
            lang_file = os.path.join(translations_dir, f"{lang}.json")
            if not os.path.exists(lang_file):
                with open(lang_file, "w", encoding="utf-8") as f:
                    json.dump({
                        "welcome": "欢迎使用设备预定系统" if lang == "zh_CN" else "Welcome to Equipment Reservation System"
                    }, f, ensure_ascii=False, indent=4)

            # 加载翻译文件
            try:
                with open(lang_file, "r", encoding="utf-8") as f:
                    _translations[lang] = json.load(f)
            except Exception as e:
                logger.error(f"加载翻译文件失败 ({lang}): {e}")
                _translations[lang] = {}

        logger.info("国际化设置成功")
    except Exception as e:
        logger.error(f"国际化设置失败: {e}")
        # 不抛出异常，让应用继续运行
        pass

def get_locale() -> str:
    """获取当前语言"""
    return _current_locale

def translate(key: str, **kwargs) -> str:
    """翻译文本"""
    try:
        # 获取当前语言的翻译
        translations = _translations.get(_current_locale, {})

        # 获取翻译文本
        text = translations.get(key, key)

        # 替换参数
        for k, v in kwargs.items():
            text = text.replace(f"{{{k}}}", str(v))

        return text
    except Exception as e:
        logger.error(f"翻译失败: {e}")
        return key
