from django.contrib import admin
from .models import Ingredient


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "calories", "protein", "fat", "carbs"]
    list_filter = ["category"]
    search_fields = ["name"]
