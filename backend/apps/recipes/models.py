"""
食谱模型
"""
from django.db import models
from django.db.models import Index
from common.models import BaseModel


class Recipe(BaseModel):
    """食谱"""
    MEAL_TYPE_CHOICES = [
        ("breakfast", "早餐"),
        ("lunch", "午餐"),
        ("dinner", "晚餐"),
    ]

    title = models.CharField("菜名", max_length=100)
    difficulty = models.PositiveSmallIntegerField(
        "难度",
        choices=[(i, f"{i}星") for i in range(1, 6)],
        default=3
    )
    duration = models.PositiveIntegerField("耗时(分钟)", default=30)
    cover_url = models.URLField("封面图", blank=True, null=True)
    source_url = models.URLField("来源链接", blank=True, null=True)
    meal_type = models.CharField(
        "餐段",
        max_length=20,
        choices=MEAL_TYPE_CHOICES,
        default="lunch"
    )
    steps = models.JSONField(
        "烹饪步骤",
        default=list,
        help_text="格式：[{'step': 1, 'description': '...'}, ...]"
    )
    tools = models.JSONField(
        "所需工具",
        default=list,
        blank=True,
        help_text="工具列表数组，如：['锅', '铲子', '碗']"
    )
    servings = models.PositiveSmallIntegerField(
        "每份可供几人食",
        blank=True,
        null=True
    )
    tips = models.TextField("附加提示", blank=True)

    class Meta:
        verbose_name = "食谱"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
        indexes = [
            Index(fields=["meal_type"], name="recipe_meal_idx"),
            Index(fields=["difficulty"], name="recipe_diff_idx"),
            Index(fields=["created_at"], name="recipe_created_idx"),
        ]

    def __str__(self) -> str:
        return self.title


class RecipeIngredient(BaseModel):
    """食谱-食材关联"""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="食谱"
    )
    ingredient = models.ForeignKey(
        "ingredients.Ingredient",
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
        verbose_name="食材"
    )
    amount = models.CharField("用量", max_length=30, default="适量")

    class Meta:
        verbose_name = "食谱食材"
        verbose_name_plural = verbose_name
        unique_together = [["recipe", "ingredient"]]
        indexes = [
            Index(fields=["recipe"], name="rec_ing_recipe_idx"),
            Index(fields=["ingredient"], name="rec_ing_ing_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.recipe.title} - {self.ingredient.name}"
