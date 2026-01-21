"""
解析 HowToCook Markdown 文件为 JSON 格式
"""
import os
import json
import re
from pathlib import Path


def parse_markdown_file(file_path: Path) -> dict:
    """
    解析单个 Markdown 文件
    
    Returns:
        包含食谱信息的字典
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 提取标题（第一个 # 开头的行）
    title_match = re.search(r"^# (.+)$", content, re.MULTILINE)
    title = title_match.group(1) if title_match else file_path.stem
    
    # 提取必备原料
    ingredients_pattern = r"## 必备原料和工具\s*\n(.*?)(?=\n##|\Z)"
    ingredients_match = re.search(ingredients_pattern, content, re.DOTALL)
    ingredients = []
    if ingredients_match:
        ingredients_text = ingredients_match.group(1)
        # 解析列表项
        for line in ingredients_text.split("\n"):
            line = line.strip()
            if line.startswith("-") or line.startswith("*"):
                ingredient = line.lstrip("- *").strip()
                if ingredient:
                    ingredients.append(ingredient)
    
    # 提取操作步骤
    steps_pattern = r"## 操作\s*\n(.*?)(?=\n##|\Z)"
    steps_match = re.search(steps_pattern, content, re.DOTALL)
    steps = []
    if steps_match:
        steps_text = steps_match.group(1)
        step_num = 1
        for line in steps_text.split("\n"):
            line = line.strip()
            if re.match(r"^\d+\.", line):
                step_content = re.sub(r"^\d+\.\s*", "", line)
                steps.append({
                    "step": step_num,
                    "description": step_content
                })
                step_num += 1
    
    return {
        "title": title,
        "source_file": str(file_path),
        "ingredients": ingredients,
        "steps": steps,
    }


def parse_all_recipes(source_dir: Path, output_file: Path):
    """解析所有 Markdown 文件"""
    recipes = []
    
    for md_file in source_dir.rglob("*.md"):
        if md_file.name == "README.md":
            continue
        
        try:
            recipe = parse_markdown_file(md_file)
            recipes.append(recipe)
            print(f"已解析: {recipe['title']}")
        except Exception as e:
            print(f"解析失败 {md_file}: {e}")
    
    # 保存为 JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(recipes, f, ensure_ascii=False, indent=2)
    
    print(f"\n共解析 {len(recipes)} 个食谱，已保存到 {output_file}")


if __name__ == "__main__":
    # 配置路径
    BASE_DIR = Path(__file__).parent.parent
    
    # 优先使用 recipes_data，其次 data/howtocook
    if (BASE_DIR / "recipes_data" / "dishes").exists():
        SOURCE_DIR = BASE_DIR / "recipes_data" / "dishes"
    elif (BASE_DIR / "data" / "howtocook" / "dishes").exists():
        SOURCE_DIR = BASE_DIR / "data" / "howtocook" / "dishes"
    else:
        SOURCE_DIR = BASE_DIR / "recipes_data" / "dishes"
    
    OUTPUT_FILE = BASE_DIR / "data" / "recipes.json"
    
    if not SOURCE_DIR.exists():
        print(f"错误: 源目录不存在 {SOURCE_DIR}")
        print("请先执行: git clone https://github.com/Anduin2017/HowToCook.git recipes_data")
        print("或: git clone https://github.com/Anduin2017/HowToCook.git data/howtocook")
        exit(1)
    
    parse_all_recipes(SOURCE_DIR, OUTPUT_FILE)
