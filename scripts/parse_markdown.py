"""
解析 HowToCook Markdown 文件为结构化数据
"""
import re
from pathlib import Path
from typing import Optional


# 目录 → meal_types 映射（支持多值）
DIRECTORY_MEAL_TYPES_MAP = {
    "breakfast": ["breakfast"],
    "meat_dish": ["lunch", "dinner"],
    "vegetable_dish": ["lunch", "dinner"],
    "soup": ["lunch", "dinner"],
    "staple": ["lunch", "dinner"],
    "aquatic": ["lunch", "dinner"],
    "semi-finished": ["lunch", "dinner"],
    "dessert": ["dessert"],
    "drink": ["drink"],
    "condiment": None,         # 跳过调料
    "template": None,          # 跳过模板
}

# 食材分类关键词
CATEGORY_KEYWORDS = {
    "meat": ["肉", "鸡", "鸭", "牛", "猪", "羊", "排骨", "腊肠", "培根", "火腿", "香肠"],
    "seafood": ["虾", "鱼", "蟹", "贝", "海参", "蛤", "蚝", "鳝", "鳊", "鲈", "鳜"],
    "vegetable": ["菜", "萝卜", "土豆", "茄子", "瓜", "豆", "葱", "姜", "蒜", "椒", "笋", "藕", "芹"],
    "egg_dairy": ["蛋", "奶", "芝士", "奶酪", "黄油", "牛奶"],
    "grain": ["米", "面", "粉", "麦", "饭", "馒头", "吐司", "面包"],
    "seasoning": ["盐", "酱油", "生抽", "老抽", "醋", "糖", "油", "料酒", "味精", "鸡精", 
                  "胡椒", "花椒", "辣椒", "孜然", "五香", "香料", "酱", "蚝油", "豆瓣"],
}


def count_stars(text: str) -> int:
    """统计难度星级"""
    star_match = re.search(r"[★☆]+", text)
    if star_match:
        return star_match.group().count("★")
    return 3  # 默认 3 星


def infer_category(ingredient_name: str) -> str:
    """推断食材分类"""
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in ingredient_name:
                return category
    return "other"


def parse_ingredients_with_amount(text: str) -> list[dict]:
    """
    解析带用量的食材列表
    返回: [{"name": "鸡翅", "amount": "10只"}, ...]
    """
    ingredients = []
    for line in text.split("\n"):
        line = line.strip()
        if not line or not (line.startswith("-") or line.startswith("*")):
            continue
        
        item = line.lstrip("-* ").strip()
        if not item:
            continue
        
        # 尝试分离名称和用量
        # 常见格式: "鸡翅 10只", "盐 2克", "生抽 15ml"
        match = re.match(r"^(.+?)\s+(\d+[\s\S]*?)$", item)
        if match:
            name = match.group(1).strip()
            amount = match.group(2).strip()
        else:
            name = item
            amount = "适量"
        
        ingredients.append({"name": name, "amount": amount})
    
    return ingredients


def parse_ingredients_base(text: str) -> list[str]:
    """解析基础食材列表（仅名称）"""
    ingredients = []
    for line in text.split("\n"):
        line = line.strip()
        if not line or not (line.startswith("-") or line.startswith("*")):
            continue
        
        item = line.lstrip("-* ").strip()
        if item:
            ingredients.append(item)
    
    return ingredients


def parse_steps(text: str) -> list[dict]:
    """解析操作步骤"""
    steps = []
    step_num = 1
    
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        
        # 匹配列表项或数字开头
        if line.startswith("-") or line.startswith("*"):
            content = line.lstrip("-* ").strip()
            # 跳过子步骤（缩进的项）
            if content and not line.startswith("  "):
                steps.append({"step": step_num, "description": content})
                step_num += 1
        elif re.match(r"^\d+[\.、]", line):
            content = re.sub(r"^\d+[\.、]\s*", "", line).strip()
            if content:
                steps.append({"step": step_num, "description": content})
                step_num += 1
    
    return steps


def find_cover_image(md_file: Path) -> Optional[str]:
    """
    查找封面图片
    优先级：
    1. 同名图片 (如 xxx.jpg)
    2. 名称包含菜名或"成品"的图片
    3. 目录下第一张图片
    4. 无图返回 None（前端使用默认占位图）
    """
    parent = md_file.parent
    stem = md_file.stem
    
    extensions = [".jpg", ".jpeg", ".png", ".webp"]
    
    # 1. 精确同名图片
    for ext in extensions:
        img_path = parent / f"{stem}{ext}"
        if img_path.exists():
            return str(img_path.relative_to(parent.parent.parent))
    
    # 2. 名称包含菜名或"成品"的图片
    for ext in ["*.jpg", "*.jpeg", "*.png", "*.webp"]:
        for img in parent.glob(ext):
            if stem in img.stem or "成品" in img.stem:
                return str(img.relative_to(parent.parent.parent))
    
    # 3. 目录下任意第一张图片
    for ext in ["*.jpg", "*.jpeg", "*.png", "*.webp"]:
        images = list(parent.glob(ext))
        if images:
            return str(images[0].relative_to(parent.parent.parent))
    
    return None  # 无图，前端用默认占位


def parse_markdown_file(file_path: Path) -> Optional[dict]:
    """
    解析单个 Markdown 文件
    
    Returns:
        包含食谱信息的字典，或 None（跳过）
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 确定 dish_type 和 meal_types
    parent_dir = file_path.parent.name
    # 处理有子目录的情况 (如 meat_dish/可乐鸡翅/可乐鸡翅.md)
    if parent_dir not in DIRECTORY_MEAL_TYPES_MAP:
        parent_dir = file_path.parent.parent.name
    
    dish_type = parent_dir  # 保存菜品类型
    meal_types = DIRECTORY_MEAL_TYPES_MAP.get(parent_dir)
    if meal_types is None:
        return None  # 跳过 condiment/template
    
    # 提取标题
    title_match = re.search(r"^#\s+(.+?)(?:的做法)?$", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else file_path.stem
    title = title.replace("的做法", "").strip()
    
    # 提取难度
    difficulty_match = re.search(r"预估烹饪难度[：:]\s*([★☆]+)", content)
    difficulty = count_stars(difficulty_match.group(1)) if difficulty_match else 3
    
    # 提取必备原料
    ingredients_base_pattern = r"##\s*必备原料和工具\s*\n(.*?)(?=\n##|\Z)"
    ingredients_base_match = re.search(ingredients_base_pattern, content, re.DOTALL)
    ingredients_base = []
    if ingredients_base_match:
        ingredients_base = parse_ingredients_base(ingredients_base_match.group(1))
    
    # 提取计算（带用量）
    calc_pattern = r"##\s*计算\s*\n(.*?)(?=\n##|\Z)"
    calc_match = re.search(calc_pattern, content, re.DOTALL)
    ingredients_with_amount = []
    if calc_match:
        ingredients_with_amount = parse_ingredients_with_amount(calc_match.group(1))
    
    # 合并食材：优先使用带用量的，补充基础列表
    ingredient_names_with_amount = {i["name"] for i in ingredients_with_amount}
    for name in ingredients_base:
        if name not in ingredient_names_with_amount:
            ingredients_with_amount.append({"name": name, "amount": "适量"})
    
    # 提取操作步骤
    steps_pattern = r"##\s*操作\s*\n(.*?)(?=\n##|\Z)"
    steps_match = re.search(steps_pattern, content, re.DOTALL)
    steps = []
    if steps_match:
        steps = parse_steps(steps_match.group(1))
    
    # 提取附加内容
    tips_pattern = r"##\s*附加内容\s*\n(.*?)(?=\n##|\Z)"
    tips_match = re.search(tips_pattern, content, re.DOTALL)
    tips = ""
    if tips_match:
        tips = tips_match.group(1).strip()
        # 移除末尾的 Issue/PR 提示
        tips = re.sub(r"如果您遵循本指南.*$", "", tips, flags=re.DOTALL).strip()
    
    # 查找封面图
    cover_image = find_cover_image(file_path)
    
    return {
        "title": title,
        "difficulty": difficulty,
        "dish_type": dish_type,
        "meal_types": meal_types,
        "source_file": str(file_path),
        "cover_image": cover_image,
        "ingredients": ingredients_with_amount,
        "steps": steps,
        "tips": tips,
    }


def build_difficulty_map(starsystem_dir: Path) -> dict[str, int]:
    """
    从 starsystem 目录构建难度映射
    返回: {"dishes/meat_dish/可乐鸡翅.md": 3, ...}
    """
    difficulty_map = {}
    
    for star_file in starsystem_dir.glob("*Star.md"):
        # 从文件名提取难度 (1Star.md -> 1)
        star_match = re.match(r"(\d+)Star\.md", star_file.name)
        if not star_match:
            continue
        difficulty = int(star_match.group(1))
        difficulty = min(difficulty, 5)  # 限制最大 5 星
        
        with open(star_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 提取所有菜谱路径
        for match in re.finditer(r"\[.+?\]\(\.\./(dishes/.+?\.md)\)", content):
            path = match.group(1)
            difficulty_map[path] = difficulty
    
    return difficulty_map


def parse_all_recipes(source_dir: Path, starsystem_dir: Path) -> list[dict]:
    """解析所有 Markdown 文件"""
    # 构建难度映射
    difficulty_map = build_difficulty_map(starsystem_dir)
    print(f"从 starsystem 加载 {len(difficulty_map)} 个难度映射")
    
    recipes = []
    skipped = 0
    
    for md_file in source_dir.rglob("*.md"):
        if md_file.name == "README.md":
            continue
        
        try:
            recipe = parse_markdown_file(md_file)
            if recipe is None:
                skipped += 1
                continue
            
            # 使用 starsystem 难度（如果有）
            relative_path = f"dishes/{md_file.relative_to(source_dir)}"
            relative_path = relative_path.replace("\\", "/")
            if relative_path in difficulty_map:
                recipe["difficulty"] = difficulty_map[relative_path]
            
            recipes.append(recipe)
            print(f"已解析: {recipe['title']} (难度: {recipe['difficulty']}星, 类型: {recipe['meal_types']})")
        except Exception as e:
            print(f"解析失败 {md_file}: {e}")
    
    print(f"\n共解析 {len(recipes)} 个食谱，跳过 {skipped} 个")
    return recipes


if __name__ == "__main__":
    import json
    
    BASE_DIR = Path(__file__).parent.parent
    SOURCE_DIR = BASE_DIR / "recipes_data" / "dishes"
    STARSYSTEM_DIR = BASE_DIR / "recipes_data" / "starsystem"
    OUTPUT_FILE = BASE_DIR / "data" / "recipes.json"
    
    if not SOURCE_DIR.exists():
        print(f"错误: 源目录不存在 {SOURCE_DIR}")
        exit(1)
    
    # 确保输出目录存在
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    recipes = parse_all_recipes(SOURCE_DIR, STARSYSTEM_DIR)
    
    # 保存为 JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(recipes, f, ensure_ascii=False, indent=2)
    
    print(f"已保存到 {OUTPUT_FILE}")
