# 🚀 快速开始：GitHub Actions 自动构建和发布

## 三步完成配置

### 1️⃣ 推送工作流文件到 GitHub

工作流文件已创建在 `.github/workflows/release.yml`，直接提交并推送：

```bash
git add .github/workflows/release.yml
git commit -m "chore: 添加 GitHub Actions 自动构建工作流"
git push origin main
```

### 2️⃣ 创建版本 Tag 触发构建

```bash
# 创建 tag（版本号格式：v1.0.0）
git tag v1.0.0 -m "Release version 1.0.0"

# 推送 tag 到远程（这会自动触发构建）
git push origin v1.0.0
```

### 3️⃣ 查看构建结果

1. **查看构建状态**：
   - 进入 GitHub 仓库
   - 点击 **Actions** 标签
   - 查看 "Build and Release to GitHub" 工作流运行状态

2. **下载 APK**：
   - 构建完成后（约 10-15 分钟）
   - 进入 **Releases** 标签
   - 找到对应版本的 Release
   - 下载 `whattoeattoday-v1.0.0.apk`

---

## 📋 详细说明

### 工作流触发条件

- ✅ **创建 Tag**：当推送 `v*` 格式的 tag 时自动触发（如 `v1.0.0`）
- ✅ **手动触发**：在 GitHub Actions 页面手动运行

### 构建过程

1. 自动安装 Node.js、Java、Android SDK
2. 安装项目依赖
3. 运行 Expo prebuild 生成原生项目
4. 使用 Gradle 构建 Android APK
5. 自动创建 GitHub Release 并上传 APK

### 版本管理

每次发布新版本时：

1. **更新版本号**（可选）：
   ```json
   // frontend/app.json
   {
     "expo": {
       "version": "1.0.1",
       "android": {
         "versionCode": 2
       }
     }
   }
   ```

2. **提交更改**：
   ```bash
   git add frontend/app.json
   git commit -m "chore: bump version to 1.0.1"
   git push origin main
   ```

3. **创建新 Tag**：
   ```bash
   git tag v1.0.1 -m "Release version 1.0.1"
   git push origin v1.0.1
   ```

---

## ⚙️ 可选配置

### 配置 API URL

如果需要设置生产环境 API URL：

1. 进入 GitHub 仓库 → **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**
3. 添加：
   - **Name**: `API_URL`
   - **Value**: `https://your-api-domain.com`

工作流会自动使用该 URL 作为 `EXPO_PUBLIC_API_URL` 环境变量。

---

## 🔍 故障排查

### 构建失败

1. **检查 Actions 日志**：
   - GitHub 仓库 → Actions → 点击失败的运行
   - 查看错误信息

2. **常见问题**：
   - **依赖安装失败**：检查 `package.json` 是否正确
   - **Android SDK 问题**：工作流会自动安装，通常无需手动配置
   - **Gradle 构建失败**：检查 `app.json` 配置是否正确

### APK 未上传到 Release

- **原因**：只有创建 Tag 时才会创建 Release
- **解决**：确保使用 `git push origin v1.0.0` 推送 tag，而不是只推送代码

### 找不到 Release

- 检查 Tag 名称格式：必须是 `v*` 格式（如 `v1.0.0`）
- 检查构建是否成功：进入 Actions 查看运行状态

---

## 📚 相关文档

- [完整配置指南](./GITHUB_ACTIONS_SETUP.md) - 详细的配置说明和多种方案
- [API 文档](./API_DOCUMENTATION.md) - 后端 API 文档

---

## ✅ 验证清单

- [ ] 工作流文件已推送到 GitHub
- [ ] 创建并推送了第一个 Tag（如 `v1.0.0`）
- [ ] GitHub Actions 运行成功
- [ ] Release 已创建并包含 APK 文件
- [ ] 可以下载并安装 APK

---

*最后更新时间：2026-01-23*
