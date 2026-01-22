# API 文档

## 基础信息

- **Base URL**: `http://localhost:8000/api/v1/`
- **Content-Type**: `application/json`

## 餐段类型说明

| 值 | 说明 |
|----|------|
| breakfast | 早餐 |
| lunch | 午餐 |
| dinner | 晚餐 |
| dessert | 甜点 |
| drink | 饮品 |

> 注意：一道菜可以同时属于多个餐段，如 `["lunch", "dinner"]` 表示午餐和晚餐都适用。

---

## Recipes API

### 1. 获取食谱列表

**GET** `/api/v1/recipes/`

**查询参数：**
- `meal_type`: 餐段类型 (breakfast/lunch/dinner/dessert/drink)
- `difficulty`: 难度 (1-5)
- `search`: 搜索关键词（搜索标题）
- `ordering`: 排序字段 (created_at, difficulty, duration)
- `page`: 页码
- `page_size`: 每页数量（默认 20，最大 100）

**示例：**
```bash
GET /api/v1/recipes/?meal_type=lunch&difficulty=3&search=炒
GET /api/v1/recipes/?meal_type=dessert
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
      "title": "可乐鸡翅",
      "difficulty": 3,
      "difficulty_display": "3星",
      "duration": 35,
      "cover_url": null,
      "meal_types": ["lunch", "dinner"],
      "meal_types_display": ["午餐", "晚餐"],
      "servings": 2,
      "created_at": "2026-01-21T10:00:00Z"
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
  "title": "可乐鸡翅",
  "difficulty": 3,
  "difficulty_display": "3星",
  "duration": 35,
  "cover_url": "meat_dish/可乐鸡翅/可乐鸡翅.jpg",
  "meal_types": ["lunch", "dinner"],
  "meal_types_display": ["午餐", "晚餐"],
  "servings": null,
  "steps": [
    {"step": 1, "description": "鸡翅入锅，倒入冷水淹没..."},
    {"step": 2, "description": "捞出鸡翅，可用刀将两边各划上两口改刀..."}
  ],
  "tools": [],
  "tips": "加入生姜爆香的同时能防止鸡翅粘锅...",
  "source_url": "D:\\whatToEatToday\\recipes_data\\dishes\\meat_dish\\可乐鸡翅.md",
  "ingredients": [
    {
      "ingredient_id": 1,
      "ingredient_name": "鸡翅中",
      "ingredient_category": "meat",
      "amount": "10 ～ 12 只"
    },
    {
      "ingredient_id": 2,
      "ingredient_name": "可乐",
      "ingredient_category": "other",
      "amount": "500ml"
    }
  ],
  "created_at": "2026-01-21T10:00:00Z"
}
```

---

### 3. 获取推荐食谱

**GET** `/api/v1/recipes/recommend/`

随机推荐指定餐段的食谱。

**查询参数：**
- `meal_type`: 餐段类型 (breakfast/lunch/dinner/dessert/drink)，可选
- `count`: 返回数量，默认 2

**示例：**
```bash
# 推荐午餐
GET /api/v1/recipes/recommend/?meal_type=lunch&count=3

# 推荐甜点
GET /api/v1/recipes/recommend/?meal_type=dessert&count=2

# 推荐饮品
GET /api/v1/recipes/recommend/?meal_type=drink&count=2

# 随机推荐（不限餐段）
GET /api/v1/recipes/recommend/?count=5
```

**响应示例：**
```json
[
  {
    "id": 15,
    "title": "红烧肉",
    "difficulty": 3,
    "difficulty_display": "3星",
    "duration": 45,
    "cover_url": "meat_dish/红烧肉/000.jpg",
    "meal_types": ["lunch", "dinner"],
    "meal_types_display": ["午餐", "晚餐"],
    "servings": null,
    "created_at": "2026-01-21T10:00:00Z"
  },
  {
    "id": 28,
    "title": "青椒肉丝",
    "difficulty": 2,
    "difficulty_display": "2星",
    "duration": 20,
    "cover_url": null,
    "meal_types": ["lunch", "dinner"],
    "meal_types_display": ["午餐", "晚餐"],
    "servings": null,
    "created_at": "2026-01-21T10:00:00Z"
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

**食材分类说明：**
| 值 | 说明 |
|----|------|
| meat | 肉类 |
| vegetable | 蔬菜 |
| seafood | 海鲜 |
| egg_dairy | 蛋奶 |
| grain | 谷物 |
| seasoning | 调料 |
| other | 其他 |

**示例：**
```bash
GET /api/v1/ingredients/?category=vegetable&search=番茄
GET /api/v1/ingredients/?category=meat
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
      "calories": null,
      "protein": null,
      "fat": null,
      "carbs": null,
      "created_at": "2026-01-21T10:00:00Z"
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
  "name": "鸡翅中",
  "category": "meat",
  "category_display": "肉类",
  "calories": null,
  "protein": null,
  "fat": null,
  "carbs": null,
  "created_at": "2026-01-21T10:00:00Z"
}
```

> 注意：营养成分（calories/protein/fat/carbs）在 MVP 阶段为空，后续通过 AI 自动填充。

---

## Users API

### 1. 获取当前用户

**GET** `/api/v1/users/me/`

通过 `X-Device-ID` 请求头识别用户。

**请求头：**
- `X-Device-ID`: 设备唯一标识（必填）

**示例：**
```bash
curl -H "X-Device-ID: abc123" http://localhost:8000/api/v1/users/me/
```

**响应示例：**
```json
{
  "id": 1,
  "device_id": "abc123",
  "username": null,
  "liked_ingredients": [],
  "disliked_ingredients": [],
  "favorite_recipes": [1, 5, 12],
  "disliked_recipes": [],
  "cooked_recipes": {"1": 3, "5": 1},
  "preferences": {},
  "created_at": "2026-01-22T10:00:00Z",
  "updated_at": "2026-01-22T10:00:00Z"
}
```

**错误响应：**
- `404`: 用户不存在

---

### 2. 创建用户

**POST** `/api/v1/users/me/add/`

**请求头：**
- `X-Device-ID`: 设备唯一标识（必填）

**示例：**
```bash
curl -X POST -H "X-Device-ID: abc123" http://localhost:8000/api/v1/users/me/add/
```

**响应：** 返回创建的用户信息（201 Created）

**错误响应：**
- `400`: 用户已存在

---

**PATCH** `/api/v1/users/me/`

**请求头：**
- `X-Device-ID`: 设备唯一标识（必填）

**请求体：**
```json
{
  "username": "美食家",
  "favorite_recipes": [1, 5, 12],
  "liked_ingredients": [10, 20],
  "disliked_ingredients": [30]
}
```

**响应：** 返回更新后的完整用户信息。

---

### 4. 记录制作食谱

**POST** `/api/v1/users/cooked/{recipe_id}/`

记录用户制作了某道食谱，自动累加制作次数。

**请求头：**
- `X-Device-ID`: 设备唯一标识（必填）

**示例：**
```bash
curl -X POST -H "X-Device-ID: abc123" http://localhost:8000/api/v1/users/cooked/15/
```

**响应示例：**
```json
{
  "recipe_id": 15,
  "count": 2
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

---

## 数据统计

当前数据库：
- 食谱总数：327
- 食材总数：1928

按餐段分布：
- 早餐：约 23 道
- 午餐/晚餐：约 280 道（大部分菜品同时适用）
- 甜点：约 18 道
- 饮品：约 6 道
