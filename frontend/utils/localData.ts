import dataJson from '@/data.json';

// Django dumpdata 格式的数据类型
interface DumpDataItem {
  model: string;
  pk: number;
  fields: {
    created_at: string;
    updated_at: string;
    title: string;
    difficulty: number;
    duration: number;
    meal_types: string[];
    steps: Array<{ step: number; description: string }>;
    tools: string[];
    servings?: number | null;
    tips?: string;
    dish_type?: string | null;
  };
}

// 食材关联数据类型
interface DumpDataIngredient {
  model: string;
  pk: number;
  fields: {
    recipe: number;
    ingredient: number;
    amount: string;
    created_at: string;
    updated_at: string;
  };
}

// 食材数据类型
interface DumpDataIngredientDetail {
  model: string;
  pk: number;
  fields: {
    name: string;
    category: string;
    created_at: string;
    updated_at: string;
  };
}

// 转换后的食谱类型
export interface Recipe {
  id: number;
  title: string;
  difficulty: number;
  difficulty_display: string;
  duration: number;
  meal_types: string[];
  meal_types_display: string[];
  dish_type: string | null;
  dish_type_display: string | null;
  servings: number | null;
  created_at: string;
  steps?: Array<{ step: number; description: string }>;
  tools?: string[];
  tips?: string;
  ingredients?: Array<{
    ingredient_id: number;
    ingredient_name: string;
    ingredient_category: string;
    amount: string;
  }>;
}

// 餐段类型映射
const MEAL_TYPE_OPTIONS: Record<string, string> = {
  breakfast: '早餐',
  lunch: '午餐',
  dinner: '晚餐',
  dessert: '甜点',
  drink: '饮品',
};

// 菜品类型映射
const DISH_TYPE_OPTIONS: Record<string, string> = {
  aquatic: '水产',
  breakfast: '早餐',
  condiment: '调味品',
  dessert: '甜点',
  drink: '饮品',
  meat_dish: '肉菜',
  'semi-finished': '半成品',
  soup: '汤类',
  staple: '主食',
  vegetable_dish: '素菜',
};

// 难度显示映射
const DIFFICULTY_DISPLAY: Record<number, string> = {
  1: '1星',
  2: '2星',
  3: '3星',
  4: '4星',
  5: '5星',
};

// 加载并转换数据
let recipesCache: Recipe[] | null = null;
let ingredientsCache: Map<number, DumpDataIngredientDetail> | null = null;
let recipeIngredientsCache: Map<number, DumpDataIngredient[]> | null = null;

function loadData() {
  if (recipesCache) {
    return { recipes: recipesCache, ingredients: ingredientsCache, recipeIngredients: recipeIngredientsCache };
  }

  const data = dataJson as (DumpDataItem | DumpDataIngredient | DumpDataIngredientDetail)[];

  // 提取食谱数据
  const recipeData = data.filter((item): item is DumpDataItem => item.model === 'recipes.recipe');
  
  // 提取食材数据
  const ingredientData = data.filter(
    (item): item is DumpDataIngredientDetail => item.model === 'ingredients.ingredient'
  );
  ingredientsCache = new Map(ingredientData.map((item) => [item.pk, item]));

  // 提取食谱-食材关联数据
  const recipeIngredientData = data.filter(
    (item): item is DumpDataIngredient => item.model === 'recipes.recipeingredient'
  );
  recipeIngredientsCache = new Map<number, DumpDataIngredient[]>();
  recipeIngredientData.forEach((item) => {
    const recipeId = item.fields.recipe;
    if (!recipeIngredientsCache!.has(recipeId)) {
      recipeIngredientsCache!.set(recipeId, []);
    }
    recipeIngredientsCache!.get(recipeId)!.push(item);
  });

  // 转换食谱数据
  recipesCache = recipeData.map((item) => {
    const recipe: Recipe = {
      id: item.pk,
      title: item.fields.title,
      difficulty: item.fields.difficulty,
      difficulty_display: DIFFICULTY_DISPLAY[item.fields.difficulty] || `${item.fields.difficulty}星`,
      duration: item.fields.duration,
      meal_types: item.fields.meal_types,
      meal_types_display: item.fields.meal_types.map((mt) => MEAL_TYPE_OPTIONS[mt] || mt),
      dish_type: item.fields.dish_type,
      dish_type_display: item.fields.dish_type ? DISH_TYPE_OPTIONS[item.fields.dish_type] || null : null,
      servings: item.fields.servings ?? null,
      created_at: item.fields.created_at,
    };
    return recipe;
  });

  return { recipes: recipesCache, ingredients: ingredientsCache, recipeIngredients: recipeIngredientsCache };
}

/**
 * 获取所有食谱
 */
export function getAllRecipes(): Recipe[] {
  const { recipes } = loadData();
  return recipes;
}

/**
 * 根据 ID 获取食谱详情
 */
export function getRecipeById(id: number): Recipe | null {
  const { recipes, ingredients, recipeIngredients } = loadData();
  const recipe = recipes.find((r) => r.id === id);
  if (!recipe) {
    return null;
  }

  // 获取完整的食谱详情（包含步骤、工具、提示、食材）
  const recipeData = (dataJson as DumpDataItem[]).find(
    (item): item is DumpDataItem => item.model === 'recipes.recipe' && item.pk === id
  );

  if (!recipeData) {
    return recipe;
  }

  const fullRecipe: Recipe = {
    ...recipe,
    steps: recipeData.fields.steps,
    tools: recipeData.fields.tools,
    tips: recipeData.fields.tips,
  };

  // 添加食材信息
  const ingredientRelations = recipeIngredients?.get(id) || [];
  fullRecipe.ingredients = ingredientRelations.map((rel) => {
    const ingredient = ingredients?.get(rel.fields.ingredient);
    return {
      ingredient_id: rel.fields.ingredient,
      ingredient_name: ingredient?.fields.name || '',
      ingredient_category: ingredient?.fields.category || '',
      amount: rel.fields.amount,
    };
  });

  return fullRecipe;
}

/**
 * 搜索食谱
 */
export function searchRecipes(
  keyword: string,
  page: number = 1,
  pageSize: number = 20
): { count: number; next: string | null; previous: string | null; results: Recipe[] } {
  const recipes = getAllRecipes();

  if (!keyword.trim()) {
    return {
      count: 0,
      next: null,
      previous: null,
      results: [],
    };
  }

  // 过滤：标题包含关键词
  const filtered = recipes.filter((recipe) =>
    recipe.title.toLowerCase().includes(keyword.toLowerCase().trim())
  );

  // 排序：按创建时间倒序
  const sorted = filtered.sort((a, b) => {
    return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
  });

  // 分页
  const start = (page - 1) * pageSize;
  const end = start + pageSize;
  const paginated = sorted.slice(start, end);

  return {
    count: sorted.length,
    next: end < sorted.length ? `page=${page + 1}` : null,
    previous: page > 1 ? `page=${page - 1}` : null,
    results: paginated,
  };
}

/**
 * 获取推荐食谱（随机抽取）
 */
export function getRecommendations(mealType?: string | null, count: number = 2): Recipe[] {
  const recipes = getAllRecipes();

  // 过滤：按餐段类型
  let filtered = recipes;
  if (mealType) {
    filtered = recipes.filter((recipe) => recipe.meal_types.includes(mealType));
  }

  // 随机排序并取前 count 个
  const shuffled = [...filtered].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, count);
}

/**
 * 根据 ID 列表获取食谱
 */
export function getRecipesByIds(ids: number[]): Recipe[] {
  const recipes = getAllRecipes();
  return recipes.filter((recipe) => ids.includes(recipe.id));
}
