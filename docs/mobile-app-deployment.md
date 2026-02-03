# NewsGap 移动端部署和测试指南

## 概述

本文档说明如何构建、测试和部署 NewsGap 移动应用(iOS 和 Android)。

## 前置要求

### macOS (iOS 开发)

| 工具 | 版本 | 说明 |
|------|------|------|
| Xcode | 15.0+ | iOS 开发环境 |
| CocoaPods | 1.11+ | iOS 依赖管理 |
| iOS Simulator | - | 测试环境 |
| Apple Developer Account | - | 真机测试/发布必需 |

```bash
# 安装 Xcode Command Line Tools
xcode-select --install

# 安装 CocoaPods
sudo gem install cocoapods
```

### Windows/Linux (Android 开发)

| 工具 | 版本 | 说明 |
|------|------|------|
| Android Studio | Latest | Android 开发环境 |
| JDK | 17+ | Java 开发工具包 |
| Android SDK | API 33+ | Android SDK |
| Gradle | 8.0+ | 构建工具(自动安装) |

下载: https://developer.android.com/studio

## 项目结构

```
NewsGap/
├── frontend/
│   ├── src/
│   │   ├── mobile-services/      # 移动端核心服务
│   │   │   ├── database.ts       # SQLite 数据库
│   │   │   ├── rss-fetcher.ts    # RSS 爬取
│   │   │   ├── llm-client.ts     # LLM API
│   │   │   ├── mobile-api.ts     # 统一 API
│   │   │   └── types.ts          # 类型定义
│   │   ├── services/
│   │   │   ├── api.ts            # API 代理(条件编译)
│   │   │   └── web-api.ts        # Web API (原有)
│   │   └── ...
│   ├── ios/                       # iOS 原生项目
│   │   └── App/
│   │       ├── App.xcodeproj
│   │       └── App.xcworkspace
│   ├── android/                   # Android 原生项目
│   │   ├── app/
│   │   └── build.gradle
│   ├── capacitor.config.ts        # Capacitor 配置
│   └── package.json
└── docs/
    └── mobile-app-deployment.md   # 本文档
```

## 构建流程

### 1. 安装依赖

```bash
cd frontend

# 安装 npm 依赖
npm install

# 验证 Capacitor 安装
npx cap doctor
```

### 2. 构建 Web 资源

```bash
# 开发构建
npm run build

# 生产构建
NODE_ENV=production npm run build
```

### 3. 同步到原生项目

```bash
# 同步到 iOS 和 Android
npx cap sync

# 仅同步 iOS
npx cap sync ios

# 仅同步 Android
npx cap sync android
```

## iOS 部署

### 1. 打开 Xcode 项目

```bash
cd frontend
npx cap open ios
```

或直接打开:
```bash
open ios/App/App.xcworkspace
```

### 2. 配置签名

1. 在 Xcode 中选择项目 **App**
2. 选择 **Signing & Capabilities**
3. 勾选 **Automatically manage signing**
4. 选择你的 **Team** (Apple Developer Account)
5. 修改 **Bundle Identifier** (例如: `com.yourname.newsgap`)

### 3. 配置权限

在 `ios/App/App/Info.plist` 添加必要权限:

```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>

<key>NSPhotoLibraryUsageDescription</key>
<string>需要访问相册以保存图片</string>

<key>NSCameraUsageDescription</key>
<string>需要访问相机以拍照</string>
```

### 4. 运行模拟器

在 Xcode 中:
1. 选择目标设备 (例如: iPhone 15)
2. 点击 **Run** 按钮 (⌘R)

或使用命令行:
```bash
npx cap run ios --target="iPhone 15"
```

### 5. 真机测试

1. 连接 iPhone/iPad 到 Mac
2. 在 Xcode 中选择你的设备
3. 点击 **Run**
4. 在设备上信任开发者证书:
   - 设置 → 通用 → VPN与设备管理 → 开发者App → 信任

### 6. 构建发布版本

```bash
# Archive for App Store
# 在 Xcode 中: Product → Archive
# 然后: Window → Organizer → Distribute App
```

## Android 部署

### 1. 打开 Android Studio 项目

```bash
cd frontend
npx cap open android
```

### 2. 配置项目

编辑 `android/app/build.gradle`:

```gradle
android {
    namespace "com.newsgap.app"
    compileSdk 34
    
    defaultConfig {
        applicationId "com.newsgap.app"  // 修改为你的包名
        minSdk 22
        targetSdk 34
        versionCode 1
        versionName "1.0.0"
    }
    
    buildTypes {
        release {
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android.txt'), 'proguard-rules.pro'
        }
    }
}
```

### 3. 配置权限

在 `android/app/src/main/AndroidManifest.xml`:

```xml
<manifest>
    <!-- 网络权限 -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    
    <!-- 存储权限 -->
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" 
                     android:maxSdkVersion="32" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" 
                     android:maxSdkVersion="32" />
    
    <application
        android:usesCleartextTraffic="true"
        ...>
    </application>
</manifest>
```

### 4. 运行模拟器

在 Android Studio 中:
1. 打开 **AVD Manager** (Tools → Device Manager)
2. 创建/启动模拟器
3. 点击 **Run** 按钮 (Shift+F10)

或使用命令行:
```bash
# 列出可用设备
npx cap run android --list

# 运行到模拟器
npx cap run android --target="Pixel_5_API_33"
```

### 5. 真机测试

1. 在手机上启用 **开发者选项** 和 **USB 调试**
2. 连接手机到电脑
3. 在 Android Studio 中选择你的设备
4. 点击 **Run**

### 6. 构建发布版本

```bash
cd frontend/android

# 生成签名密钥
keytool -genkey -v -keystore my-release-key.keystore \
        -alias my-key-alias -keyalg RSA -keysize 2048 -validity 10000

# 配置签名 (android/app/build.gradle)
signingConfigs {
    release {
        storeFile file('my-release-key.keystore')
        storePassword 'your-password'
        keyAlias 'my-key-alias'
        keyPassword 'your-password'
    }
}

# 构建 APK
./gradlew assembleRelease

# 构建 AAB (Google Play)
./gradlew bundleRelease
```

输出:
- APK: `android/app/build/outputs/apk/release/app-release.apk`
- AAB: `android/app/build/outputs/bundle/release/app-release.aab`

## 测试指南

### 单元测试

```bash
cd frontend

# 运行测试
npm test

# 覆盖率报告
npm run test:coverage
```

### 功能测试清单

#### 数据库功能
- [ ] 创建文章
- [ ] 查询文章 (带筛选)
- [ ] 更新文章 (归档)
- [ ] 删除文章
- [ ] 创建分析
- [ ] 查询分析

#### RSS 爬取
- [ ] 单源爬取
- [ ] 多源并发爬取
- [ ] 时间过滤
- [ ] 错误处理
- [ ] 去重功能

#### LLM API
- [ ] Gemini API 调用
- [ ] DeepSeek API 调用
- [ ] OpenAI API 调用
- [ ] API Key 管理
- [ ] 错误处理

#### 一键情报
- [ ] 标准分类爬取+分析
- [ ] 自定义分类爬取+分析
- [ ] 进度显示
- [ ] 错误提示

#### UI/UX
- [ ] 响应式布局
- [ ] 触摸交互
- [ ] 加载状态
- [ ] 错误提示
- [ ] 离线提示

### 性能测试

```bash
# iOS
# 在 Xcode 中: Product → Profile → Time Profiler

# Android
# 在 Android Studio 中: View → Tool Windows → Profiler
```

**关键指标:**
- 应用启动时间: < 2秒
- 数据库查询: < 100ms
- RSS 爬取: < 5秒/源
- LLM 分析: < 30秒

### 网络测试

测试不同网络环境:
- ✅ Wi-Fi
- ✅ 4G/5G
- ✅ 弱网 (模拟)
- ✅ 离线 (基本功能)

### 设备测试

**iOS:**
- iPhone SE (小屏)
- iPhone 15 (标准)
- iPhone 15 Pro Max (大屏)
- iPad (平板)

**Android:**
- Pixel 5 (标准)
- Samsung Galaxy S23 (高端)
- 低端设备 (API 22)

## 调试技巧

### iOS 调试

```bash
# 查看日志
npx cap run ios --target="iPhone 15"

# 在 Safari 中调试 WebView
Safari → 开发 → iPhone 模拟器 → localhost
```

### Android 调试

```bash
# 查看日志
adb logcat

# 查看 Capacitor 日志
adb logcat | grep Capacitor

# Chrome DevTools
chrome://inspect
```

### Web 调试

```bash
# 开发模式(会使用 Web API,不是移动端 API)
npm run dev

# 在浏览器中模拟移动端
Chrome DevTools → Toggle Device Toolbar (Cmd+Shift+M)
```

### 常见问题

**问题: SQLite 插件未加载**
```bash
# 重新安装插件
npm install @capacitor-community/sqlite@latest
npx cap sync
```

**问题: HTTP 请求被阻止 (iOS)**

在 `Info.plist` 添加:
```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>
```

**问题: Android 构建失败**
```bash
# 清理并重新构建
cd android
./gradlew clean
./gradlew build
```

**问题: Capacitor 插件冲突**
```bash
# 同步并更新
npx cap sync --force
```

## 发布流程

### iOS App Store

1. **准备素材**
   - 应用图标 (1024x1024)
   - 截图 (各种尺寸)
   - 描述、关键词

2. **构建 Archive**
   - Xcode → Product → Archive

3. **上传到 App Store Connect**
   - Window → Organizer → Upload

4. **提交审核**
   - App Store Connect → 我的App → 提交审核

### Google Play

1. **准备素材**
   - 应用图标 (512x512)
   - 功能图片 (1024x500)
   - 截图 (最少 2 张)
   - 描述、分类

2. **构建 AAB**
   ```bash
   cd android
   ./gradlew bundleRelease
   ```

3. **上传到 Google Play Console**
   - 创建应用 → 上传 AAB
   - 填写商店列表信息
   - 提交审核

## CI/CD 自动化

### GitHub Actions (示例)

创建 `.github/workflows/mobile-build.yml`:

```yaml
name: Mobile Build

on:
  push:
    branches: [mobile-app]

jobs:
  build-ios:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      
      - name: Install dependencies
        working-directory: ./frontend
        run: npm ci
      
      - name: Build web assets
        working-directory: ./frontend
        run: npm run build
      
      - name: Sync to iOS
        working-directory: ./frontend
        run: npx cap sync ios
  
  build-android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      
      - name: Install dependencies
        working-directory: ./frontend
        run: npm ci
      
      - name: Build web assets
        working-directory: ./frontend
        run: npm run build
      
      - name: Sync to Android
        working-directory: ./frontend
        run: npx cap sync android
      
      - name: Build APK
        working-directory: ./frontend/android
        run: ./gradlew assembleRelease
```

## 维护和更新

### 更新 Capacitor

```bash
npm install @capacitor/core@latest @capacitor/cli@latest
npm install @capacitor/ios@latest @capacitor/android@latest
npx cap sync
```

### 更新插件

```bash
npm update @capacitor-community/sqlite
npm update @capacitor-community/http
npx cap sync
```

### 更新 Web 资源

```bash
# 修改代码后
npm run build
npx cap copy

# 无需重新编译原生项目
```

## 相关资源

- [Capacitor 官方文档](https://capacitorjs.com/docs)
- [iOS 开发文档](https://developer.apple.com/documentation/)
- [Android 开发文档](https://developer.android.com/docs)
- [SQLite Plugin](https://github.com/capacitor-community/sqlite)
- [HTTP Plugin](https://github.com/capacitor-community/http)

---

**文档版本**: v1.0  
**最后更新**: 2026-02-03  
**维护者**: NewsGap Team
