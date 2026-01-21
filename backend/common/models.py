"""
公共基础模型
"""
from django.db import models


class BaseModel(models.Model):
    """基础模型，包含通用字段"""
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        abstract = True
