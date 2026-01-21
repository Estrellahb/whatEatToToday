"""
将 JSON 数据导入数据库
"""
import os
import sys
import json
from pathlib import Path
from decimal import Decimal

# 添加项目路径到 Python 路径
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "backend"))

# 设置 Django 环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

import django
django.setup()

from apps.recipes.models import Recipe, RecipeIngredient
from apps.ingredients.models import Ingredient


def get_or_create_ingredient(name: str) -> Ingredient:
    """获取或创建食材"""
    ingredient, created = Ingredient.objects.get_or_create(
        name=name.strip(),
        defaults={"category": "other"}
    )
    return ingredient


def import_recipes(json_file: Path):
    """导入食谱数据"""
    with open(json_file, "r", encoding="utf-8") as f:
        recipes_data = json.load(f)
    
    imported_count = 0
    skipped_count = 0
    
    for recipe_data in recipes_data:
        title = recipe_data.get("title", "").strip()
        if not title:
            skipped_count += 1
            continue
        
        # 检查是否已存在
        if Recipe.objects.filter(title=title).exists():
            print(f"跳过已存在: {title}")
            skipped_count += 1
            continue
        
        # 创建食谱
        recipe = Recipe.objects.create(
            title=title,
            difficulty=3,  # 默认难度
            duration=30,   # 默认耗时
            meal_type="lunch",  # 默认午餐
            steps=recipe_data.get("steps", []),
            source_url=recipe_data.get("source_file", ""),
        )
        
        # 创建食材关联
        for ingredient_name in recipe_data.get("ingredients", []):
            ingredient = get_or_create_ingredient(ingredient_name)
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                amount="适量"
            )
        
        imported_count += 1
        print(f"已导入: {title}")
    
    print(f"\n导入完成: 新增 {imported_count} 个，跳过 {skipped_count} 个")


if __name__ == "__main__":
    JSON_FILE = BASE_DIR / "data" / "recipes.json"
    
    if not JSON_FILE.exists():
        print(f"错误: JSON 文件不存在 {JSON_FILE}")
        print("请先执行: python scripts/parse_markdown.py")
        exit(1)
    
    import_recipes(JSON_FILE)
