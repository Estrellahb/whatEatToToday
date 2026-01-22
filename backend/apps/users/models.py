"""
用户模型
"""
from django.db import models
from common.models import BaseModel


class User(BaseModel):
    """用户"""
    device_id = models.CharField("设备标识", max_length=64, unique=True)
    username = models.CharField("用户名", max_length=50, blank=True, null=True)
    liked_ingredients = models.JSONField(
        "喜欢的食材",
        default=list,
        blank=True,
        help_text="食材 ID 列表"
    )
    disliked_ingredients = models.JSONField(
        "不喜欢的食材",
        default=list,
        blank=True,
        help_text="食材 ID 列表"
    )
    favorite_recipes = models.JSONField(
        "收藏的食谱",
        default=list,
        blank=True,
        help_text="食谱 ID 列表"
    )
    disliked_recipes = models.JSONField(
        "不喜欢的食谱",
        default=list,
        blank=True,
        help_text="食谱 ID 列表"
    )
    cooked_recipes = models.JSONField(
        "已制作食谱",
        default=dict,
        blank=True,
        help_text="格式：{recipe_id: count}，如 {'1': 3, '25': 1}"
    )
    preferences = models.JSONField("其他偏好设置", default=dict, blank=True)

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return self.username or self.device_id
