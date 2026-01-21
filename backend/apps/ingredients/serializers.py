from rest_framework import serializers
from .models import Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    """食材序列化器"""
    category_display = serializers.CharField(source="get_category_display", read_only=True)

    class Meta:
        model = Ingredient
        fields = [
            "id",
            "name",
            "category",
            "category_display",
            "calories",
            "protein",
            "fat",
            "carbs",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
