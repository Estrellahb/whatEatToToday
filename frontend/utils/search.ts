import { searchRecipes as searchRecipesLocal, Recipe } from './localData';

export interface SearchRecipe {
  id: number;
  title: string;
  difficulty: number;
  difficulty_display?: string;
  cover_url?: string | null;
  meal_types_display?: string[];
  dish_type_display?: string;
  duration?: number;
}

export interface SearchResult {
  count: number;
  next: string | null;
  previous: string | null;
  results: SearchRecipe[];
}

/**
 * 搜索食谱
 * @param keyword 搜索关键词
 * @param page 页码（从1开始）
 * @param pageSize 每页数量
 * @returns 搜索结果
 */
export const searchRecipes = async (
  keyword: string,
  page: number = 1,
  pageSize: number = 20
): Promise<SearchResult> => {
  const result = searchRecipesLocal(keyword, page, pageSize);
  
  // 转换格式以匹配原有接口
  return {
    count: result.count,
    next: result.next,
    previous: result.previous,
    results: result.results.map((recipe: Recipe): SearchRecipe => ({
      id: recipe.id,
      title: recipe.title,
      difficulty: recipe.difficulty,
      difficulty_display: recipe.difficulty_display,
      cover_url: null,
      meal_types_display: recipe.meal_types_display,
      dish_type_display: recipe.dish_type_display || undefined,
      duration: recipe.duration,
    })),
  };
};

/**
 * 获取封面图 URL（已废弃，不再使用）
 */
export const getCoverUrl = (coverUrl?: string | null) => {
  if (!coverUrl) {
    return 'https://images.unsplash.com/photo-1473093295043-cdd812d0e601?auto=format&fit=crop&w=800&q=80';
  }
  if (coverUrl.startsWith('http')) {
    return coverUrl;
  }
  return coverUrl;
};
