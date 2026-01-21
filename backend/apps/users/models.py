"""
用户模型（预留）
"""
from django.db import models
from common.models import BaseModel


class User(BaseModel):
    """用户（预留，MVP 阶段不使用）"""
    device_id = models.CharField("设备标识", max_length=64, unique=True)
    preferences = models.JSONField("偏好设置", default=dict, blank=True)

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return self.device_id
