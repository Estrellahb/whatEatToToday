"""
食谱模型
"""
from django.db import models
from django.db.models import Index
from common.models import BaseModel


class Recipe(BaseModel):
    """食谱"""
    # 可选的餐段类型
    MEAL_TYPE_OPTIONS = {
        "breakfast": "早餐",
        "lunch": "午餐",
        "dinner": "晚餐",
        "dessert": "甜点",
        "drink": "饮品",
    }

    # 菜品类型选项
    DISH_TYPE_OPTIONS = {
        "aquatic": "水产",
        "breakfast": "早餐",
        "condiment": "调味品",
        "dessert": "甜点",
        "drink": "饮品",
        "meat_dish": "肉菜",
        "semi-finished": "半成品",
        "soup": "汤类",
        "staple": "主食",
        "vegetable_dish": "素菜",
    }

    title = models.CharField("菜名", max_length=100)
    difficulty = models.PositiveSmallIntegerField(
        "难度",
        choices=[(i, f"{i}星") for i in range(1, 6)],
        default=3
    )
    duration = models.PositiveIntegerField("耗时(分钟)", default=30)
    meal_types = models.JSONField(
        "适用餐段",
        default=list,
        help_text="可选值: breakfast, lunch, dinner, dessert, drink"
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
    dish_type = models.CharField(
        "菜品类型",
        max_length=20,
        choices=[(k, v) for k, v in DISH_TYPE_OPTIONS.items()],
        blank=True,
        null=True,
        help_text="菜品分类：aquatic/breakfast/condiment/dessert/drink/meat_dish/semi-finished/soup/staple/vegetable_dish"
    )

    class Meta:
        verbose_name = "食谱"
        verbose_name_plural = verbose_name
        ordering = ["-created_at"]
        indexes = [
            Index(fields=["difficulty"], name="recipe_diff_idx"),
            Index(fields=["created_at"], name="recipe_created_idx"),
        ]

    def __str__(self) -> str:
        return self.title

    def get_meal_types_display(self) -> list[str]:
        """获取餐段显示名称列表"""
        return [self.MEAL_TYPE_OPTIONS.get(mt, mt) for mt in self.meal_types]


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
