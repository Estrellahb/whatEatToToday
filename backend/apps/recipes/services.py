"""
食谱业务逻辑
"""
import logging
from typing import Optional, List
from django.db.models import QuerySet
from .models import Recipe, RecipeIngredient

logger = logging.getLogger(__name__)


class RecipeService:
    """食谱服务"""

    @staticmethod
    def get_recommendations(
        meal_type: Optional[str] = None,
        count: int = 2
    ) -> QuerySet[Recipe]:
        """
        获取推荐食谱（MVP 版本：随机抽取）
        
        Args:
            meal_type: 餐段类型 breakfast/lunch/dinner
            count: 返回数量
        
        Returns:
            食谱查询集
        """
        queryset = Recipe.objects.all()
        
        if meal_type:
            queryset = queryset.filter(meal_type=meal_type)
        
        result = queryset.order_by("?")[:count]
        logger.info(f"获取推荐食谱: meal_type={meal_type}, count={count}, 实际返回={result.count()}")
        
        return result

    @staticmethod
    def search_by_ingredients(ingredient_ids: List[int]) -> QuerySet[Recipe]:
        """
        根据食材 ID 列表搜索食谱（预留接口，后续实现）
        
        Args:
            ingredient_ids: 食材 ID 列表
        
        Returns:
            食谱查询集
        """
        # TODO: 实现反向检索逻辑
        # 查找包含这些食材的食谱
        recipes = Recipe.objects.filter(
            recipe_ingredients__ingredient_id__in=ingredient_ids
        ).distinct()
        
        logger.info(f"根据食材搜索: ingredient_ids={ingredient_ids}, 结果数量={recipes.count()}")
        return recipes
