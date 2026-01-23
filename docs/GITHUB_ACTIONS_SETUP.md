# GitHub Actions 自动构建和发布配置指南

本文档说明如何配置 GitHub Actions 实现自动构建应用并发布到 GitHub Releases。

---

## 📋 目录

1. [方案选择](#方案选择)
2. [方案一：使用 EAS Build（推荐）](#方案一使用-eas-build推荐)
3. [方案二：本地构建](#方案二本地构建)
4. [配置步骤](#配置步骤)
5. [触发构建](#触发构建)
6. [常见问题](#常见问题)

---

## 方案选择

### 方案一：EAS Build（推荐）⭐
- ✅ 简单易用，无需配置 Android/iOS 环境
- ✅ 支持云端构建，不占用本地资源
- ✅ 自动处理签名和证书
- ❌ 需要 Expo 账号（免费）
- ❌ 构建产物在 Expo 平台，需要手动下载

### 方案二：本地构建
- ✅ 完全控制构建过程
- ✅ 构建产物直接上传到 GitHub Releases
- ❌ 需要配置 Android SDK 和 Xcode
- ❌ 构建时间较长
- ❌ iOS 构建需要 macOS runner（GitHub Actions 收费）

**推荐使用方案一（EAS Build）**，更简单且免费。

---

## 方案一：使用 EAS Build（推荐）

### 前置条件

1. **Expo 账号**
   - 访问 [https://expo.dev](https://expo.dev) 注册账号（免费）

2. **获取 Expo Token**
   - 登录 Expo 后，访问：`https://expo.dev/accounts/[your-account]/settings/access-tokens`
   - 创建新的 Access Token
   - 复制 Token（只显示一次，请妥善保存）

3. **配置 EAS**
   - 在项目根目录运行：`cd frontend && npx eas login`
   - 运行：`npx eas build:configure`
   - 这会创建 `eas.json` 配置文件

### 配置步骤

#### 1. 创建 `eas.json` 配置文件

在 `frontend/` 目录下创建 `eas.json`：

```json
{
  "cli": {
    "version": ">= 5.2.0"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal"
    },
    "preview": {
      "distribution": "internal",
      "android": {
        "buildType": "apk"
      },
      "ios": {
        "simulator": false
      }
    },
    "production": {
      "distribution": "store",
      "android": {
        "buildType": "apk"
      }
    }
  },
  "submit": {
    "production": {}
  }
}
```

#### 2. 配置 GitHub Secrets

1. 进入 GitHub 仓库
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. 添加以下 Secret：

| Secret 名称 | 值 | 说明 |
|------------|-----|------|
| `EXPO_TOKEN` | 你的 Expo Access Token | 从 Expo 账号设置中获取 |

#### 3. 使用工作流文件

已创建 `.github/workflows/build-eas.yml`，该工作流会：
- 在 push 到 main/master 分支时触发
- 在创建 tag（如 `v1.0.0`）时触发并创建 Release
- 支持手动触发

#### 4. 修改 `app.json`（可选）

确保 `app.json` 中的版本信息正确：

```json
{
  "expo": {
    "version": "1.0.0",
    "android": {
      "versionCode": 1,
      "package": "com.yourcompany.whattoeattoday"
    },
    "ios": {
      "buildNumber": "1",
      "bundleIdentifier": "com.yourcompany.whattoeattoday"
    }
  }
}
```

### 触发构建

#### 自动触发
- **Push 到 main/master**：自动构建，但不创建 Release
- **创建 Tag**：自动构建并创建 Release

```bash
# 创建并推送 tag
git tag v1.0.0
git push origin v1.0.0
```

#### 手动触发
1. 进入 GitHub 仓库
2. 点击 **Actions** 标签
3. 选择 **Build with EAS** 工作流
4. 点击 **Run workflow**
5. 选择平台（all/android/ios）
6. 点击 **Run workflow**

### 下载构建产物

1. 构建完成后，访问 [Expo Dashboard](https://expo.dev)
2. 进入你的项目
3. 点击 **Builds** 查看构建列表
4. 下载 APK/IPA 文件
5. （可选）手动上传到 GitHub Releases

---

## 方案二：本地构建

### 前置条件

1. **Android 构建**
   - 需要 Android SDK（GitHub Actions 会自动安装）
   - 需要 Java 17

2. **iOS 构建**
   - 需要 macOS runner（GitHub Actions 免费版不支持）
   - 需要 Xcode

### 配置步骤

#### 1. 使用工作流文件

已创建 `.github/workflows/build-and-release.yml`，该工作流会：
- 自动安装 Android SDK 和 Java
- 构建 Android APK
- 自动上传到 GitHub Releases（仅当创建 tag 时）

#### 2. 配置环境变量（可选）

如果需要配置 API URL，添加 GitHub Secret：

| Secret 名称 | 值 | 说明 |
|------------|-----|------|
| `API_URL` | `https://your-api.com` | 后端 API 地址 |

#### 3. 修改 `app.json`

确保包名和版本正确：

```json
{
  "expo": {
    "version": "1.0.0",
    "android": {
      "versionCode": 1,
      "package": "com.yourcompany.whattoeattoday"
    }
  }
}
```

### 触发构建

#### 自动触发
- **Push 到 main/master**：自动构建，但不创建 Release
- **创建 Tag**：自动构建并创建 Release

```bash
# 创建并推送 tag
git tag v1.0.0
git push origin v1.0.0
```

#### 手动触发
1. 进入 GitHub 仓库
2. 点击 **Actions** 标签
3. 选择 **Build and Release** 工作流
4. 点击 **Run workflow**

### 下载构建产物

1. 进入 GitHub 仓库
2. 点击 **Releases**
3. 找到对应的 Release
4. 下载 APK 文件

---

## 配置步骤总结

### 快速开始（推荐：自动发布到 Releases）⭐

1. **确保工作流文件存在**：`.github/workflows/release.yml`（已创建）
2. **创建 Tag 并推送**：
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
3. **查看构建状态**：GitHub 仓库 → Actions
4. **下载 APK**：GitHub 仓库 → Releases → 找到对应版本

### 快速开始（EAS Build）

1. **注册 Expo 账号**：https://expo.dev
2. **获取 Token**：https://expo.dev/accounts/[your-account]/settings/access-tokens
3. **配置 GitHub Secret**：`EXPO_TOKEN`
4. **创建 `eas.json`**：在 `frontend/` 目录下
5. **创建 Tag 并推送**：
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

### 快速开始（本地构建）

1. **确保工作流文件存在**：`.github/workflows/build-and-release.yml`
2. **创建 Tag 并推送**：
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

---

## 触发构建

### 方式一：创建 Tag（推荐）

```bash
# 创建 tag
git tag v1.0.0 -m "Release version 1.0.0"

# 推送 tag
git push origin v1.0.0
```

### 方式二：Push 到主分支

```bash
git push origin main
```

### 方式三：手动触发

1. GitHub 仓库 → **Actions**
2. 选择工作流
3. 点击 **Run workflow**

---

## 常见问题

### 1. EAS Build 失败：Token 无效

**解决方案**：
- 检查 `EXPO_TOKEN` 是否正确配置
- 重新生成 Token 并更新 Secret

### 2. 本地构建失败：找不到 Android SDK

**解决方案**：
- 工作流会自动安装 Android SDK
- 如果仍然失败，检查 `setup-android` action 版本

### 3. 构建成功但没有创建 Release

**原因**：只有创建 Tag 时才会创建 Release

**解决方案**：
```bash
git tag v1.0.0
git push origin v1.0.0
```

### 4. iOS 构建失败

**原因**：GitHub Actions 免费版不支持 macOS runner

**解决方案**：
- 使用 EAS Build（推荐）
- 或升级到 GitHub Actions 付费版

### 5. 构建产物在哪里？

- **EAS Build**：Expo Dashboard → Builds
- **本地构建**：GitHub Releases

---

## 工作流文件说明

### `release.yml`（推荐）⭐
- **用途**：自动构建 Android APK 并发布到 GitHub Releases
- **触发**：创建 `v*` 格式的 tag 时自动触发
- **特点**：
  - ✅ 完全自动化
  - ✅ 自动上传到 Releases
  - ✅ 无需额外配置
  - ✅ 免费使用

### `build-eas.yml`（EAS Build）
- 使用 Expo EAS 云端构建
- 需要 `EXPO_TOKEN` Secret
- 构建产物在 Expo 平台

### `build-and-release.yml`（本地构建）
- 在 GitHub Actions runner 上构建
- Android 构建在 Ubuntu runner
- iOS 构建在 macOS runner（需要付费）
- 自动上传到 GitHub Releases

---

## 版本管理建议

### 版本号格式
- 使用语义化版本：`v1.0.0`、`v1.0.1`、`v1.1.0`
- Tag 名称：`v*`（如 `v1.0.0`）

### 更新版本

1. **更新 `app.json`**：
   ```json
   {
     "expo": {
       "version": "1.0.1",
       "android": {
         "versionCode": 2
       }
     }
   }
   ```

2. **创建 Tag**：
   ```bash
   git add frontend/app.json
   git commit -m "Bump version to 1.0.1"
   git tag v1.0.1
   git push origin main
   git push origin v1.0.1
   ```

---

## 下一步

1. ✅ 选择构建方案（推荐 EAS Build）
2. ✅ 配置 GitHub Secrets
3. ✅ 创建并推送 Tag
4. ✅ 检查 GitHub Actions 运行状态
5. ✅ 下载构建产物

---

*最后更新时间：2026-01-23*
