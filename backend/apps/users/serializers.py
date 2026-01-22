"""
用户序列化器
"""
from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""

    class Meta:
        model = User
        fields = [
            "id",
            "device_id",
            "username",
            "liked_ingredients",
            "disliked_ingredients",
            "favorite_recipes",
            "disliked_recipes",
            "cooked_recipes",
            "preferences",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class UserUpdateSerializer(serializers.ModelSerializer):
    """用户更新序列化器"""

    class Meta:
        model = User
        fields = [
            "username",
            "liked_ingredients",
            "disliked_ingredients",
            "favorite_recipes",
            "disliked_recipes",
            "cooked_recipes",
            "preferences",
        ]
