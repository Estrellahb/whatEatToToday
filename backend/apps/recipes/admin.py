from django.contrib import admin
from .models import Recipe, RecipeIngredient


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ["title", "difficulty", "duration", "meal_type", "servings", "created_at"]
    list_filter = ["difficulty", "meal_type", "created_at"]
    search_fields = ["title"]
    fieldsets = (
        ("基本信息", {
            "fields": ("title", "meal_type", "difficulty", "duration", "servings")
        }),
        ("内容", {
            "fields": ("cover_url", "source_url", "steps", "tools", "tips")
        }),
        ("时间", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    readonly_fields = ["created_at", "updated_at"]
    inlines = [RecipeIngredientInline]
