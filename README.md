# 每天吃点啥 (What to Eat Today)

解决"有食材但没灵感"、"想做饭但不知道做什么"的日常决策焦虑。

## 技术栈

| 模块 | 技术 |
|------|------|
| 前端 | React Native + Expo |
| 后端 | Django + DRF |
| 数据库 | PostgreSQL (生产) / SQLite (开发) |
| AI | DeepSeek API |

## 项目结构

```
whatToEatToday/
├── frontend/          # React Native + Expo 前端
├── backend/           # Django 后端
├── scripts/           # 数据处理脚本
├── recipes_data/      # 菜谱数据（来源：HowToCook）
├── data/              # 处理后的 JSON 数据
└── docs/              # 项目文档
```

## 数据来源

本项目使用的菜谱数据来源于开源项目 [HowToCook](https://github.com/Anduin2017/HowToCook)。

- **原始仓库**: https://github.com/Anduin2017/HowToCook
- **许可证**: Unlicense
- **数据位置**: `recipes_data/` 目录

感谢 HowToCook 项目的贡献者们提供了丰富的中文菜谱资源！

## 快速开始

### 前端

```bash
cd frontend
npm install
npm start
```

使用 Expo Go App 扫码预览。

### 后端

```bash
cd backend

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境 (Windows)
.\.venv\Scripts\Activate.ps1

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 启动开发服务器
python manage.py runserver
```

### 获取菜谱数据

**方式一：已包含数据（推荐）**

项目已包含 `recipes_data/` 目录，直接执行解析和导入：

```bash
python scripts/parse_markdown.py
python scripts/import_recipes.py
```

**方式二：从 GitHub 克隆最新数据**

```bash
# 克隆 HowToCook 仓库到项目目录
git clone https://github.com/Anduin2017/HowToCook.git recipes_data

# 解析 Markdown 为 JSON
python scripts/parse_markdown.py

# 导入到数据库
python scripts/import_recipes.py
```

**注意：** `scripts/parse_markdown.py` 默认从 `recipes_data/dishes/` 目录读取 Markdown 文件。

## API 文档

启动后端后访问：http://localhost:8000/api/v1/

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/recipes/` | GET | 食谱列表 |
| `/api/v1/recipes/{id}/` | GET | 食谱详情 |
| `/api/v1/recipes/recommend/` | GET | 获取推荐 |

## 贡献指南

请参考 `.cursor/rules/git-commit.mdc` 中的提交规范。

## 致谢

感谢以下开源项目：

- [HowToCook](https://github.com/Anduin2017/HowToCook) - 提供丰富的中文菜谱数据
- [Expo](https://expo.dev/) - React Native 开发框架
- [Django REST Framework](https://www.django-rest-framework.org/) - Django API 开发框架

## 许可证

MIT
