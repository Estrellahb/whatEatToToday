import { MMKV } from 'react-native-mmkv';

const storage = new MMKV({
  id: 'favorites-storage',
});

const FAVORITES_KEY = 'favorite_recipes';

export interface FavoriteRecipe {
  id: number;
  title: string;
  difficulty: number;
  difficulty_display?: string;
  cover_url?: string | null;
  meal_types_display?: string[];
  dish_type_display?: string;
  duration?: number;
  servings?: number | null;
}

/**
 * 获取所有收藏的食谱 ID
 */
export const getFavoriteIds = (): number[] => {
  const idsJson = storage.getString(FAVORITES_KEY);
  if (!idsJson) return [];
  try {
    return JSON.parse(idsJson);
  } catch {
    return [];
  }
};

/**
 * 检查食谱是否已收藏
 */
export const isFavorite = (recipeId: number): boolean => {
  const ids = getFavoriteIds();
  return ids.includes(recipeId);
};

/**
 * 添加收藏
 */
export const addFavorite = (recipeId: number): void => {
  const ids = getFavoriteIds();
  if (!ids.includes(recipeId)) {
    ids.push(recipeId);
    storage.set(FAVORITES_KEY, JSON.stringify(ids));
  }
};

/**
 * 移除收藏
 */
export const removeFavorite = (recipeId: number): void => {
  const ids = getFavoriteIds();
  const filtered = ids.filter((id) => id !== recipeId);
  storage.set(FAVORITES_KEY, JSON.stringify(filtered));
};

/**
 * 切换收藏状态
 */
export const toggleFavorite = (recipeId: number): boolean => {
  if (isFavorite(recipeId)) {
    removeFavorite(recipeId);
    return false;
  } else {
    addFavorite(recipeId);
    return true;
  }
};

/**
 * 获取收藏的食谱详情（需要传入完整的食谱数据）
 */
export const getFavoriteRecipes = (allRecipes: FavoriteRecipe[]): FavoriteRecipe[] => {
  const favoriteIds = getFavoriteIds();
  return allRecipes.filter((recipe) => favoriteIds.includes(recipe.id));
};

/**
 * 清空所有收藏
 */
export const clearAllFavorites = (): void => {
  storage.delete(FAVORITES_KEY);
};
