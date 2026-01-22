"""
将解析后的食谱数据导入 Django 数据库
"""
import sys
import os
from pathlib import Path
from typing import Optional

# 添加项目路径
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "backend"))

# 设置 Django 环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

import django
django.setup()

from django.db import transaction
from apps.recipes.models import Recipe, RecipeIngredient
from apps.ingredients.models import Ingredient
from parse_markdown import parse_all_recipes, infer_category




def get_or_create_ingredient(name: str) -> Ingredient:
    """获取或创建食材"""
    name = name.strip()
    category = infer_category(name)
    
    ingredient, was_created = Ingredient.objects.get_or_create(
        name=name,
        defaults={"category": category}
    )
    
    if was_created:
        print(f"  新建食材: {name} ({category})")
    
    return ingredient


def estimate_duration(steps: list[dict], difficulty: int) -> int:
    """估算烹饪时间"""
    # 基础时间：每步骤约 5 分钟
    base_time = len(steps) * 5
    
    # 难度修正
    difficulty_factor = {1: 0.5, 2: 0.8, 3: 1.0, 4: 1.3, 5: 1.5}
    factor = difficulty_factor.get(difficulty, 1.0)
    
    duration = int(base_time * factor)
    
    # 限制范围
    return max(10, min(duration, 120))


@transaction.atomic
def import_recipe(recipe_data: dict) -> Optional[Recipe]:
    """导入单个食谱"""
    title = recipe_data.get("title", "").strip()
    if not title:
        return None
    
    # 检查是否已存在
    if Recipe.objects.filter(title=title).exists():
        print(f"跳过已存在: {title}")
        return None
    
    difficulty = recipe_data.get("difficulty", 3)
    steps = recipe_data.get("steps", [])
    meal_types = recipe_data.get("meal_types", ["lunch"])
    duration = estimate_duration(steps, difficulty)
    
    # 创建食谱
    recipe = Recipe.objects.create(
        title=title,
        difficulty=difficulty,
        duration=duration,
        meal_types=meal_types,
        dish_type=recipe_data.get("dish_type"),
        steps=steps,
        tips=recipe_data.get("tips", ""),
        cover_url=recipe_data.get("cover_image"),
        source_url=recipe_data.get("source_file"),
    )
    
    # 创建食材关联
    for ing_data in recipe_data.get("ingredients", []):
        name = ing_data.get("name", "").strip()
        amount = ing_data.get("amount", "适量")
        
        if not name:
            continue
        
        ingredient = get_or_create_ingredient(name)
        RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            amount=amount
        )
    
    return recipe


def import_all_recipes():
    """导入所有食谱"""
    SOURCE_DIR = BASE_DIR / "recipes_data" / "dishes"
    STARSYSTEM_DIR = BASE_DIR / "recipes_data" / "starsystem"
    
    if not SOURCE_DIR.exists():
        print(f"错误: 源目录不存在 {SOURCE_DIR}")
        return
    
    print("开始解析 Markdown 文件...")
    recipes_data = parse_all_recipes(SOURCE_DIR, STARSYSTEM_DIR)
    
    print(f"\n开始导入 {len(recipes_data)} 个食谱到数据库...")
    
    imported = 0
    skipped = 0
    
    for recipe_data in recipes_data:
        try:
            recipe = import_recipe(recipe_data)
            if recipe:
                imported += 1
                print(f"已导入: {recipe.title} ({recipe.meal_types}, {recipe.difficulty}星)")
            else:
                skipped += 1
        except Exception as e:
            print(f"导入失败 {recipe_data.get('title', 'Unknown')}: {e}")
            skipped += 1
    
    print(f"\n导入完成: 新增 {imported} 个，跳过 {skipped} 个")
    
    # 统计信息
    print("\n=== 统计信息 ===")
    print(f"食谱总数: {Recipe.objects.count()}")
    print(f"食材总数: {Ingredient.objects.count()}")
    
    print("\n按餐段统计:")
    for meal_type, label in Recipe.MEAL_TYPE_OPTIONS.items():
        # SQLite 不支持 JSONField contains，使用字符串匹配
        count = Recipe.objects.filter(meal_types__icontains=f'"{meal_type}"').count()
        print(f"  {label}: {count}")
    
    print("\n按难度统计:")
    for i in range(1, 6):
        count = Recipe.objects.filter(difficulty=i).count()
        print(f"  {i}星: {count}")


def update_dish_type():
    """更新现有食谱的 dish_type 字段"""
    SOURCE_DIR = BASE_DIR / "recipes_data" / "dishes"
    STARSYSTEM_DIR = BASE_DIR / "recipes_data" / "starsystem"
    
    print("开始解析 Markdown 文件...")
    recipes_data = parse_all_recipes(SOURCE_DIR, STARSYSTEM_DIR)
    
    # 构建 title -> dish_type 映射
    title_to_dish_type = {r["title"]: r["dish_type"] for r in recipes_data}
    
    print(f"\n开始更新 {len(title_to_dish_type)} 个食谱的 dish_type...")
    
    updated = 0
    for recipe in Recipe.objects.all():
        dish_type = title_to_dish_type.get(recipe.title)
        if dish_type and recipe.dish_type != dish_type:
            recipe.dish_type = dish_type
            recipe.save(update_fields=["dish_type"])
            updated += 1
            print(f"已更新: {recipe.title} -> {dish_type}")
    
    print(f"\n更新完成: {updated} 个食谱")
    
    # 统计
    print("\n按菜品类型统计:")
    for dish_type, label in Recipe.DISH_TYPE_OPTIONS.items():
        count = Recipe.objects.filter(dish_type=dish_type).count()
        print(f"  {label}: {count}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--update-dish-type":
        update_dish_type()
    else:
        import_all_recipes()
