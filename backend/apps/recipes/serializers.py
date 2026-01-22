from rest_framework import serializers
from .models import Recipe, RecipeIngredient


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """食谱-食材关联序列化器"""
    ingredient_name = serializers.CharField(source="ingredient.name", read_only=True)
    ingredient_id = serializers.IntegerField(source="ingredient.id", read_only=True)
    ingredient_category = serializers.CharField(source="ingredient.category", read_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ["ingredient_id", "ingredient_name", "ingredient_category", "amount"]


class RecipeSerializer(serializers.ModelSerializer):
    """食谱列表序列化器"""
    difficulty_display = serializers.CharField(source="get_difficulty_display", read_only=True)
    meal_types_display = serializers.ListField(source="get_meal_types_display", read_only=True)
    dish_type_display = serializers.CharField(source="get_dish_type_display", read_only=True)

    class Meta:
        model = Recipe
        fields = [
            "id",
            "title",
            "difficulty",
            "difficulty_display",
            "duration",
            "cover_url",
            "meal_types",
            "meal_types_display",
            "dish_type",
            "dish_type_display",
            "servings",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class RecipeDetailSerializer(RecipeSerializer):
    """食谱详情序列化器"""
    ingredients = RecipeIngredientSerializer(
        source="recipe_ingredients",
        many=True,
        read_only=True
    )

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + [
            "steps",
            "tools",
            "tips",
            "source_url",
            "ingredients",
        ]
