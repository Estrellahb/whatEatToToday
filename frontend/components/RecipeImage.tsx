import React from 'react';
import { Image, ImageStyle, StyleProp, StyleSheet } from 'react-native';
import { getRecipeImageSource } from '@/utils/recipeImages';

interface RecipeImageProps {
  title: string;
  dishType?: string | null;
  style?: StyleProp<ImageStyle>;
  resizeMode?: 'cover' | 'contain' | 'stretch' | 'repeat' | 'center';
}

/**
 * 食谱图片组件
 * 根据菜名和菜品类型自动查找对应的图片
 * 
 * 图片查找规则：
 * 1. 优先查找 assets/images/{dish_type}/{title}/{title}_01.webp
 * 2. 其次查找 assets/images/{dish_type}/{title}/{title}.webp
 * 3. 如果都不存在，显示默认图片 assets/images/default.png
 */
export default function RecipeImage({ title, dishType, style, resizeMode = 'cover' }: RecipeImageProps) {
  const imageSource = getRecipeImageSource(title, dishType);

  return (
    <Image
      source={imageSource}
      style={[styles.defaultImage, style]}
      resizeMode={resizeMode}
    />
  );
}

const styles = StyleSheet.create({
  defaultImage: {
    width: 100,
    // aspectRatio: 3 / 2,
    height: 115,
  },
});
