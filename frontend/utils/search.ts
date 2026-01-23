const API_BASE_URL = 'http://localhost:8000/api/v1';

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
  if (!keyword.trim()) {
    return {
      count: 0,
      next: null,
      previous: null,
      results: [],
    };
  }

  try {
    const params = new URLSearchParams({
      search: keyword.trim(),
      page: page.toString(),
      page_size: pageSize.toString(),
    });

    const response = await fetch(`${API_BASE_URL}/recipes/?${params.toString()}`);
    
    if (!response.ok) {
      throw new Error(`搜索失败: ${response.status}`);
    }

    const data = (await response.json()) as SearchResult;
    return data;
  } catch (error) {
    throw new Error(
      error instanceof Error ? error.message : '搜索请求失败'
    );
  }
};

/**
 * 获取封面图 URL
 */
export const getCoverUrl = (coverUrl?: string | null, baseUrl: string = 'http://localhost:8000') => {
  if (!coverUrl) {
    return 'https://images.unsplash.com/photo-1473093295043-cdd812d0e601?auto=format&fit=crop&w=800&q=80';
  }
  if (coverUrl.startsWith('http')) {
    return coverUrl;
  }
  return `${baseUrl}/${coverUrl}`;
};
