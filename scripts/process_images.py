"""
处理 dishes 文件夹中的图片：
1. 转换为 webp 格式
2. 压缩到 200kb 以下
3. 检查并规范化图片命名
"""
import os
from pathlib import Path
from PIL import Image
import shutil


def get_image_files(folder: Path) -> list[Path]:
    """获取文件夹中的所有图片文件"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.webp', '.JPG', '.JPEG', '.PNG', '.WEBP'}
    images = []
    for file in folder.iterdir():
        if file.is_file() and file.suffix in image_extensions:
            images.append(file)
    return sorted(images)


def compress_image_to_webp(image_path: Path, output_path: Path, max_size_kb: int = 200) -> bool:
    """
    将图片转换为 webp 格式并压缩到指定大小以下
    返回是否成功
    """
    try:
        # 打开图片
        with Image.open(image_path) as img:
            # 如果是 RGBA 模式，转换为 RGB（webp 支持透明度，但为了兼容性可以转换）
            if img.mode in ('RGBA', 'LA', 'P'):
                # 创建白色背景
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 初始质量
            quality = 85
            min_quality = 30
            
            # 尝试压缩到目标大小
            while quality >= min_quality:
                # 保存为 webp
                img.save(output_path, 'WEBP', quality=quality, method=6)
                
                # 检查文件大小
                file_size_kb = output_path.stat().st_size / 1024
                if file_size_kb <= max_size_kb:
                    return True
                
                # 如果还是太大，降低质量
                quality -= 10
            
            # 如果质量降到最低还是太大，尝试缩小尺寸
            if file_size_kb > max_size_kb:
                scale_factor = 0.9
                while scale_factor >= 0.5:
                    new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
                    resized_img = img.resize(new_size, Image.Resampling.LANCZOS)
                    resized_img.save(output_path, 'WEBP', quality=min_quality, method=6)
                    
                    file_size_kb = output_path.stat().st_size / 1024
                    if file_size_kb <= max_size_kb:
                        return True
                    
                    scale_factor -= 0.1
                
                # 最后尝试：使用最低质量和最小尺寸
                final_size = (int(img.width * 0.5), int(img.height * 0.5))
                final_img = img.resize(final_size, Image.Resampling.LANCZOS)
                final_img.save(output_path, 'WEBP', quality=min_quality, method=6)
            
            return True
    except Exception as e:
        print(f"  错误: 处理图片失败 {image_path}: {e}")
        return False


def process_folder(folder_path: Path, base_dir: Path):
    """处理单个文件夹中的图片"""
    folder_name = folder_path.name
    
    # 获取所有图片
    images = get_image_files(folder_path)
    if not images:
        return
    
    # 检查是否有与文件夹名一致的图片
    matching_images = [img for img in images if img.stem == folder_name]
    
    # 判断命名规则
    # 如果只有一张图片且与文件夹名一致，保留原名
    # 否则重命名为"文件夹名_01.webp"格式
    if len(images) == 1 and len(matching_images) == 1:
        # 单张图片且命名一致，保留原名
        rename_needed = False
    else:
        # 多张图片或命名不一致，需要重命名为"文件夹名_01.webp"格式
        rename_needed = True
    
    # 处理每张图片
    processed_count = 0
    for idx, image_path in enumerate(images, start=1):
        # 确定输出文件名
        if rename_needed:
            output_name = f"{folder_name}_{idx:02d}.webp"
        else:
            # 单张且命名一致，保持原名
            output_name = f"{folder_name}.webp"
        
        output_path = folder_path / output_name
        
        # 如果已经是 webp 且命名正确且大小合适，跳过
        if (image_path.suffix.lower() == '.webp' and 
            image_path.stem == output_path.stem and
            image_path.stat().st_size / 1024 <= 200):
            print(f"  跳过: {image_path.name} (已是 webp 且符合要求)")
            continue
        
        # 转换并压缩
        print(f"  处理: {image_path.name} -> {output_name}")
        if compress_image_to_webp(image_path, output_path, max_size_kb=200):
            processed_count += 1
            
            # 如果原文件不是 webp 或命名不同，删除原文件
            if image_path != output_path:
                try:
                    image_path.unlink()
                    print(f"    已删除原文件: {image_path.name}")
                except Exception as e:
                    print(f"    警告: 删除原文件失败 {image_path.name}: {e}")
        else:
            print(f"    失败: {image_path.name}")
    
    if processed_count > 0:
        print(f"[OK] {folder_name}: 处理了 {processed_count} 张图片")


def process_all_images(base_dir: Path):
    """处理所有文件夹中的图片"""
    dishes_dir = base_dir / "recipes_data" / "dishes"
    template_dir = dishes_dir / "template"
    
    if not dishes_dir.exists():
        print(f"错误: 目录不存在 {dishes_dir}")
        return
    
    print(f"开始处理图片，源目录: {dishes_dir}")
    print(f"跳过模板目录: {template_dir}\n")
    
    # 遍历所有子文件夹
    processed_folders = 0
    for category_folder in dishes_dir.iterdir():
        if not category_folder.is_dir() or category_folder == template_dir:
            continue
        
        print(f"处理分类: {category_folder.name}")
        
        # 处理分类文件夹下的所有子文件夹
        for item in category_folder.iterdir():
            if item.is_dir():
                # 子文件夹（如 aquatic/葱油桂鱼/）
                process_folder(item, base_dir)
                processed_folders += 1
            elif item.is_file() and item.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp'}:
                # 分类文件夹下的直接图片文件
                # 这种情况应该很少，但也要处理
                folder_name = category_folder.name
                output_name = f"{folder_name}.webp"
                output_path = category_folder / output_name
                
                print(f"  处理: {item.name} -> {output_name}")
                if compress_image_to_webp(item, output_path, max_size_kb=200):
                    if item != output_path:
                        item.unlink()
                    processed_folders += 1
        
        print()
    
    print(f"完成！共处理 {processed_folders} 个文件夹")


if __name__ == "__main__":
    BASE_DIR = Path(__file__).parent.parent
    process_all_images(BASE_DIR)
