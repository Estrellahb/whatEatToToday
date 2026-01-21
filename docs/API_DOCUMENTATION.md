# API 文档

## 基础信息

- **Base URL**: `http://localhost:8000/api/v1/`
- **Content-Type**: `application/json`

## Recipes API

### 1. 获取食谱列表

**GET** `/api/v1/recipes/`

**查询参数：**
- `meal_type`: 餐段类型 (breakfast/lunch/dinner)
- `difficulty`: 难度 (1-5)
- `search`: 搜索关键词（搜索标题）
- `ordering`: 排序字段 (created_at, difficulty, duration)
- `page`: 页码
- `page_size`: 每页数量（默认 20，最大 100）

**示例：**
```bash
GET /api/v1/recipes/?meal_type=lunch&difficulty=3&search=炒
GET /api/v1/recipes/?ordering=-created_at&page=1&page_size=10
```

**响应示例：**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/v1/recipes/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "西红柿炒鸡蛋",
      "difficulty": 2,
      "difficulty_display": "2星",
      "duration": 15,
      "cover_url": null,
      "meal_type": "lunch",
      "meal_type_display": "午餐",
      "servings": 2,
      "created_at": "2026-01-20T10:00:00Z"
    }
  ]
}
```

---

### 2. 获取食谱详情

**GET** `/api/v1/recipes/{id}/`

**响应示例：**
```json
{
  "id": 1,
  "title": "西红柿炒鸡蛋",
  "difficulty": 2,
  "difficulty_display": "2星",
  "duration": 15,
  "cover_url": null,
  "meal_type": "lunch",
  "meal_type_display": "午餐",
  "servings": 2,
  "steps": [
    {"step": 1, "description": "打散鸡蛋"},
    {"step": 2, "description": "切西红柿"}
  ],
  "tools": ["锅", "铲子"],
  "tips": "注意火候",
  "source_url": "...",
  "ingredients": [
    {
      "ingredient_id": 1,
      "ingredient_name": "鸡蛋",
      "ingredient_category": "egg_dairy",
      "amount": "3个"
    }
  ],
  "created_at": "2026-01-20T10:00:00Z"
}
```

---

### 3. 获取推荐食谱

**GET** `/api/v1/recipes/recommend/`

**查询参数：**
- `meal_type`: 餐段类型 (breakfast/lunch/dinner)，可选
- `count`: 返回数量，默认 2

**示例：**
```bash
GET /api/v1/recipes/recommend/?meal_type=lunch&count=2
```

**响应示例：**
```json
[
  {
    "id": 1,
    "title": "西红柿炒鸡蛋",
    ...
  },
  {
    "id": 2,
    "title": "青椒肉丝",
    ...
  }
]
```

---

## Ingredients API

### 1. 获取食材列表

**GET** `/api/v1/ingredients/`

**查询参数：**
- `category`: 分类 (meat/vegetable/seafood/egg_dairy/grain/seasoning/other)
- `search`: 搜索关键词（搜索名称）
- `ordering`: 排序字段 (name, category, created_at)
- `page`: 页码
- `page_size`: 每页数量

**示例：**
```bash
GET /api/v1/ingredients/?category=vegetable&search=番茄
```

**响应示例：**
```json
{
  "count": 50,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "西红柿",
      "category": "vegetable",
      "category_display": "蔬菜",
      "calories": 18.0,
      "protein": 0.9,
      "fat": 0.2,
      "carbs": 3.9,
      "created_at": "2026-01-20T10:00:00Z"
    }
  ]
}
```

---

### 2. 获取食材详情

**GET** `/api/v1/ingredients/{id}/`

**响应示例：**
```json
{
  "id": 1,
  "name": "西红柿",
  "category": "vegetable",
  "category_display": "蔬菜",
  "calories": 18.0,
  "protein": 0.9,
  "fat": 0.2,
  "carbs": 3.9,
  "created_at": "2026-01-20T10:00:00Z"
}
```

---

## 错误响应

所有 API 错误统一格式：

```json
{
  "detail": "错误信息"
}
```

常见状态码：
- `200`: 成功
- `400`: 请求参数错误
- `404`: 资源不存在
- `500`: 服务器错误
