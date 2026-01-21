"""
食材模型
"""
from django.db import models
from django.db.models import Index
from common.models import BaseModel


class Ingredient(BaseModel):
    """食材"""
    CATEGORY_CHOICES = [
        ("meat", "肉类"),
        ("vegetable", "蔬菜"),
        ("seafood", "海鲜"),
        ("egg_dairy", "蛋奶"),
        ("grain", "谷物"),
        ("seasoning", "调料"),
        ("other", "其他"),
    ]

    name = models.CharField("名称", max_length=50, unique=True)
    category = models.CharField(
        "分类",
        max_length=30,
        choices=CATEGORY_CHOICES,
        default="other"
    )
    calories = models.DecimalField(
        "热量(kcal/100g)",
        max_digits=7,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="后续通过 DeepSeek API 自动填充"
    )
    protein = models.DecimalField(
        "蛋白质(g/100g)",
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True
    )
    fat = models.DecimalField(
        "脂肪(g/100g)",
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True
    )
    carbs = models.DecimalField(
        "碳水(g/100g)",
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "食材"
        verbose_name_plural = verbose_name
        ordering = ["category", "name"]
        indexes = [
            Index(fields=["category"], name="ing_category_idx"),
            Index(fields=["name"], name="ing_name_idx"),
        ]

    def __str__(self) -> str:
        return self.name
