"""
将所有处理后的 webp 图片复制到根目录的 images 文件夹中
"""
from pathlib import Path
import shutil


def copy_all_images_to_root(base_dir: Path):
    """复制所有 webp 图片到根目录的 images 文件夹"""
    dishes_dir = base_dir / "recipes_data" / "dishes"
    template_dir = dishes_dir / "template"
    output_dir = base_dir / "images"
    
    if not dishes_dir.exists():
        print(f"错误: 目录不存在 {dishes_dir}")
        return
    
    # 创建输出目录
    output_dir.mkdir(exist_ok=True)
    print(f"目标目录: {output_dir}\n")
    
    # 收集所有 webp 图片
    all_images = []
    for webp_file in dishes_dir.rglob("*.webp"):
        # 跳过 template 目录
        if template_dir in webp_file.parents:
            continue
        all_images.append(webp_file)
    
    print(f"找到 {len(all_images)} 张图片\n")
    
    # 复制图片
    copied_count = 0
    skipped_count = 0
    
    for image_path in all_images:
        # 构建目标路径：保持相对路径结构
        relative_path = image_path.relative_to(dishes_dir)
        target_path = output_dir / relative_path
        
        # 确保目标目录存在
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 如果目标文件已存在且大小相同，跳过
        if target_path.exists():
            if target_path.stat().st_size == image_path.stat().st_size:
                skipped_count += 1
                continue
        
        try:
            shutil.copy2(image_path, target_path)
            copied_count += 1
            if copied_count % 50 == 0:
                print(f"已复制 {copied_count} 张...")
        except Exception as e:
            print(f"复制失败 {image_path.name}: {e}")
    
    print(f"\n完成！")
    print(f"  复制: {copied_count} 张")
    print(f"  跳过: {skipped_count} 张")
    print(f"  总计: {len(all_images)} 张")


if __name__ == "__main__":
    BASE_DIR = Path(__file__).parent.parent
    copy_all_images_to_root(BASE_DIR)
