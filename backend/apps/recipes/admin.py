from django.contrib import admin
from .models import Recipe, RecipeIngredient


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ["title", "difficulty", "duration", "get_meal_types_str", "servings", "created_at"]
    list_filter = ["difficulty", "created_at"]
    search_fields = ["title"]
    fieldsets = (
        ("基本信息", {
            "fields": ("title", "meal_types", "difficulty", "duration", "servings")
        }),
        ("内容", {
            "fields": ("steps", "tools", "tips")
        }),
        ("时间", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    readonly_fields = ["created_at", "updated_at"]
    inlines = [RecipeIngredientInline]

    @admin.display(description="适用餐段")
    def get_meal_types_str(self, obj):
        return ", ".join(obj.get_meal_types_display())
