"""
提取食谱数据并保存为JSON格式
"""
import re
import json
from pathlib import Path
from typing import Optional

# 目录名到中文meal_type的映射
DIRECTORY_MEAL_TYPE_MAP = {
    "aquatic": "水产",
    "breakfast": "早餐",
    "meat_dish": "荤菜",
    "vegetable_dish": "素菜",
    "soup": "汤品",
    "staple": "主食",
    "dessert": "甜品",
    "drink": "饮品",
    "condiment": "调料",
    "semi-finished": "半成品",
}


def count_stars(text: str) -> int:
    """统计难度星级"""
    star_match = re.search(r"[★☆]+", text)
    if star_match:
        return star_match.group().count("★")
    return 3  # 默认 3 星


def clean_text(text: str) -> str:
    """清理文本：移除图片链接和列表符号"""
    # 移除Markdown图片链接 ![alt text](image.jpg)
    text = re.sub(r"!\[.*?\]\([^)]+\)", "", text)
    # 移除行首的列表符号（- 或 *），但保留已编号的内容
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        # 如果行已经是编号格式（如 "1. "），跳过
        if re.match(r"^\s*\d+\.\s+", line):
            cleaned_lines.append(line)
        else:
            # 移除行首的 - 或 * 符号（保留缩进）
            line = re.sub(r"^(\s*)[-*]\s+", r"\1", line)
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines).strip()


def number_operations(text: str) -> str:
    """将operations字段中的-替换为序号 1. 2. 3."""
    lines = text.split("\n")
    numbered_lines = []
    step_num = 1
    
    for line in lines:
        stripped = line.lstrip()
        # 如果行首是-或*，替换为序号（只处理顶级列表项，即缩进小于等于2个空格）
        if stripped.startswith("-") or stripped.startswith("*"):
            indent_level = len(line) - len(stripped)
            # 只处理顶级列表项（缩进0-2个空格）
            if indent_level <= 2:
                content = stripped.lstrip("-* ").strip()
                numbered_lines.append(" " * indent_level + f"{step_num}. {content}")
                step_num += 1
            else:
                # 嵌套列表项，只移除-符号，不编号
                content = stripped.lstrip("-* ").strip()
                numbered_lines.append(" " * indent_level + content)
        else:
            numbered_lines.append(line)
    
    return "\n".join(numbered_lines)


def extract_section_content(content: str, section_title: str, clean: bool = True) -> str:
    """提取指定章节的内容"""
    pattern = rf"##\s*{re.escape(section_title)}\s*\n(.*?)(?=\n##|\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        text = match.group(1).strip()
        # 移除末尾的Issue/PR提示
        text = re.sub(r"如果您遵循本指南.*$", "", text, flags=re.DOTALL).strip()
        # 清理图片链接和列表符号
        if clean:
            text = clean_text(text)
        return text
    return ""


def extract_total_amount(content: str) -> str:
    """提取总量部分的内容（## 计算 中"总量："后面的内容）"""
    calc_pattern = r"##\s*计算\s*\n(.*?)(?=\n##|\Z)"
    calc_match = re.search(calc_pattern, content, re.DOTALL)
    if not calc_match:
        return ""
    
    calc_content = calc_match.group(1)
    # 查找"总量："后面的内容
    total_match = re.search(r"总量[：:]\s*\n(.*?)(?=\n##|\Z)", calc_content, re.DOTALL)
    if total_match:
        return total_match.group(1).strip()
    return ""


def extract_description(content: str) -> str:
    """提取描述（标题下面的第一段文字）"""
    # 跳过标题行
    lines = content.split("\n")
    description_lines = []
    found_title = False
    
    for line in lines:
        line = line.strip()
        # 跳过空行和标题
        if line.startswith("#"):
            found_title = True
            continue
        if not found_title:
            continue
        # 遇到下一个章节或难度行就停止
        if line.startswith("##") or "预估烹饪难度" in line:
            break
        if line:
            description_lines.append(line)
    
    return "\n".join(description_lines).strip()


def parse_markdown_file(file_path: Path, base_dir: Path) -> Optional[dict]:
    """解析单个Markdown文件"""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 确定上级目录名（处理有子目录的情况）
    parent_dir = file_path.parent.name
    if parent_dir not in DIRECTORY_MEAL_TYPE_MAP:
        parent_dir = file_path.parent.parent.name
    
    # 构建路径（如 aquatic\白灼虾）
    relative_path = file_path.relative_to(base_dir)
    # path格式：目录名\文件名（不含扩展名）
    # 如果文件在子目录中，使用子目录名；否则使用文件名
    if relative_path.parent.name != parent_dir:
        # 有子目录的情况，如 aquatic\白灼虾\白灼虾.md -> aquatic\白灼虾
        path_str = str(relative_path.parent).replace("/", "\\")
    else:
        # 直接在分类目录下的情况，如 aquatic\咖喱炒蟹.md -> aquatic\咖喱炒蟹
        path_str = f"{parent_dir}\\{file_path.stem}"
    
    # 获取meal_type
    meal_type = DIRECTORY_MEAL_TYPE_MAP.get(parent_dir, parent_dir)
    
    # 获取文件名（不含扩展名）
    meal_name = file_path.stem
    
    # 提取描述
    description = extract_description(content)
    # 清理描述中的图片链接
    description = re.sub(r"!\[.*?\]\([^)]+\)", "", description).strip()
    
    # 提取难度
    difficulty_match = re.search(r"预估烹饪难度[：:]\s*([★☆]+)", content)
    difficulty = count_stars(difficulty_match.group(1)) if difficulty_match else 3
    
    # 提取必备原料和工具
    ingredients_tools = extract_section_content(content, "必备原料和工具")
    
    # 提取总量
    total_amount = extract_total_amount(content)
    total_amount = clean_text(total_amount)
    
    # 提取操作
    operations = extract_section_content(content, "操作", clean=False)
    # 先清理图片，再编号操作步骤
    operations = re.sub(r"!\[.*?\]\([^)]+\)", "", operations)  # 只清理图片
    operations = number_operations(operations)
    operations = operations.strip()
    
    # 提取附加内容
    tips = extract_section_content(content, "附加内容")
    
    return {
        "meal_type": meal_type,
        "meal_name": meal_name,
        "description": description,
        "difficulty": difficulty,
        "ingredients_tools": ingredients_tools,
        "total_amount": total_amount,
        "operations": operations,
        "tips": tips,
    }


def extract_all_recipes(source_dir: Path, output_dir: Path):
    """提取所有食谱并保存为JSON"""
    recipes = []
    
    for md_file in source_dir.rglob("*.md"):
        if md_file.name == "README.md":
            continue
        
        try:
            recipe = parse_markdown_file(md_file, source_dir)
            if recipe:
                recipes.append(recipe)
                print(f"已提取: {recipe['meal_name']}")
        except Exception as e:
            print(f"提取失败 {md_file}: {e}")
    
    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 保存为JSON
    output_file = output_dir / "recipes.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(recipes, f, ensure_ascii=False, indent=2)
    
    print(f"\n共提取 {len(recipes)} 个食谱")
    print(f"已保存到 {output_file}")


if __name__ == "__main__":
    BASE_DIR = Path(__file__).parent.parent
    SOURCE_DIR = BASE_DIR / "recipes_data" / "dishes"
    OUTPUT_DIR = BASE_DIR / "data"
    
    if not SOURCE_DIR.exists():
        print(f"错误: 源目录不存在 {SOURCE_DIR}")
        exit(1)
    
    extract_all_recipes(SOURCE_DIR, OUTPUT_DIR)
