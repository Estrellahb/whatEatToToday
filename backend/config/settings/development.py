"""
开发环境配置
"""
from .base import *

DEBUG = True

ALLOWED_HOSTS = ["*"]

# CORS 配置 - 开发环境允许所有来源
CORS_ALLOW_ALL_ORIGINS = True

# 数据库 - 开发环境使用 SQLite
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# 开发环境显示 Browsable API
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]
