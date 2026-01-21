"""
Django settings package.
默认加载 development 配置，生产环境设置 DJANGO_SETTINGS_MODULE=config.settings.production
"""
import os

env = os.environ.get('DJANGO_ENV', 'development')

if env == 'production':
    from .production import *
else:
    from .development import *
