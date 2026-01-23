"""
生成 React Native 图片映射文件
扫描 assets/images 目录，生成所有图片的 require 映射
"""
import os
import json
from pathlib import Path

def generate_image_map():
    """生成图片映射表"""
    frontend_dir = Path(__file__).parent.parent / 'frontend'
    images_dir = frontend_dir / 'assets' / 'images'
    
    if not images_dir.exists():
        print(f"图片目录不存在: {images_dir}")
        return
    
    image_map = {}
    
    # 遍历所有子目录
    for dish_type_dir in images_dir.iterdir():
        if not dish_type_dir.is_dir() or dish_type_dir.name == '__pycache__':
            continue
        
        dish_type = dish_type_dir.name
        
        # 遍历每个菜品目录
        for recipe_dir in dish_type_dir.iterdir():
            if not recipe_dir.is_dir():
                continue
            
            recipe_name = recipe_dir.name
            
            # 查找图片文件
            image_files = list(recipe_dir.glob('*.webp'))
            if not image_files:
                continue
            
            # 优先使用 _01.webp，否则使用第一个找到的图片
            target_image = None
            for img in image_files:
                if img.stem.endswith('_01'):
                    target_image = img
                    break
            
            if not target_image:
                target_image = image_files[0]
            
            # 构建相对路径（从 assets/images 开始）
            rel_path = target_image.relative_to(images_dir)
            # 转换为正斜杠路径
            path_str = str(rel_path).replace('\\', '/')
            
            # 构建映射键
            key = f"{dish_type}|{recipe_name}"
            image_map[key] = path_str
    
    # 生成 TypeScript 文件内容
    ts_content = """// 自动生成的图片映射文件
// 请勿手动编辑此文件，使用 scripts/generate_image_map.py 重新生成

import { ImageSourcePropType } from 'react-native';

const defaultImage = require('@/assets/images/default.png');

// 图片映射表
const imageMap: Record<string, ImageSourcePropType> = {
"""
    
    # 按 key 排序
    for key in sorted(image_map.keys()):
        path = image_map[key]
        ts_content += f"  '{key}': require('@/assets/images/{path}'),\n"
    
    ts_content += """};

/**
 * 根据菜名和菜品类型获取图片源
 */
export function getRecipeImageSource(title: string, dishType?: string | null): ImageSourcePropType {
  if (!dishType || !title) {
    return defaultImage;
  }

  const key = `${dishType}|${title}`;
  
  if (imageMap[key]) {
    return imageMap[key];
  }

  return defaultImage;
}
"""
    
    # 写入文件
    output_file = frontend_dir / 'utils' / 'recipeImages.ts'
    output_file.write_text(ts_content, encoding='utf-8')
    
    print(f"已生成图片映射文件: {output_file}")
    print(f"共映射 {len(image_map)} 张图片")

if __name__ == '__main__':
    generate_image_map()
