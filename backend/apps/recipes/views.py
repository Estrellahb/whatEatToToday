from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Recipe
from .serializers import RecipeSerializer, RecipeDetailSerializer
from .services import RecipeService


class RecipeViewSet(viewsets.ReadOnlyModelViewSet):
    """食谱视图集"""
    queryset = Recipe.objects.prefetch_related("recipe_ingredients__ingredient")
    serializer_class = RecipeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["difficulty"]
    search_fields = ["title"]
    ordering_fields = ["created_at", "difficulty", "duration"]
    ordering = ["-created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        # 支持 meal_type 参数筛选（SQLite 兼容）
        meal_type = self.request.query_params.get("meal_type")
        if meal_type:
            queryset = queryset.filter(meal_types__icontains=f'"{meal_type}"')
        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return RecipeDetailSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=["get"], url_path="recommend")
    def recommend(self, request):
        """
        获取推荐食谱
        GET /api/v1/recipes/recommend/?meal_type=lunch&count=2
        """
        meal_type = request.query_params.get("meal_type")
        count = int(request.query_params.get("count", 2))
        
        recipes = RecipeService.get_recommendations(meal_type=meal_type, count=count)
        serializer = self.get_serializer(recipes, many=True)
        return Response(serializer.data)
