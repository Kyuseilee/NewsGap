# Android 构建指南

完整的 NewsGap Android 应用构建和测试指南。

---

## 📋 前置要求

### 必需
- **任何操作系统** (Windows / macOS / Linux)
- **Android Studio Hedgehog (2023.1.1) 或更高版本** ([下载](https://developer.android.com/studio))
- **JDK 17+** (Android Studio 自带，或单独安装)
- **Node.js 18+** 和 npm
- **Android SDK** (Android Studio 自动安装)

### 推荐
- **至少 8GB RAM**
- **20GB 可用磁盘空间**

### 可选（用于真机测试和发布）
- **Google Play Developer Account** ($25 一次性费用) ([注册](https://play.google.com/console))
- **Android 设备** (用于真机测试)

---

## 🚀 快速开始

### 1. 安装 Android Studio

#### Windows
```bash
1. 下载安装包: https://developer.android.com/studio
2. 运行安装程序
3. 选择 "Standard" 安装类型
4. 等待 SDK 组件下载完成
```

#### macOS
```bash
1. 下载 DMG 文件
2. 拖动到 Applications 文件夹
3. 首次打开，选择 "Standard" 安装
4. 等待 SDK 下载
```

#### Linux
```bash
# 下载并解压
wget https://redirector.gvt1.com/edgedl/android/studio/ide-zips/2023.1.1.28/android-studio-2023.1.1.28-linux.tar.gz
tar -xzf android-studio-*-linux.tar.gz

# 运行
cd android-studio/bin
./studio.sh

# 首次运行选择 "Standard" 安装
```

### 2. 环境准备

```bash
# 克隆仓库（如果还没有）
git clone <repository-url>
cd NewsGap

# 切换到移动端分支
git checkout mobile-app

# 进入前端目录
cd frontend

# 安装依赖
npm install

# 构建 Web 资源
npm run build

# 同步到 Android 项目
npx cap sync android
```

### 3. 打开 Android Studio 项目

```bash
# 方式 1：使用 Capacitor CLI（推荐）
npx cap open android

# 方式 2：手动打开 Android Studio
# File → Open → 选择 frontend/android 目录
```

---

## 🔧 Android Studio 项目配置

### 4. 首次打开项目

Android Studio 会自动执行以下操作：

1. **Gradle 同步** (首次需要 5-10 分钟)
   - 下载依赖
   - 配置项目
   - 索引文件

2. **SDK 检查**
   - 如果缺少 SDK 组件，会提示安装
   - 点击 "Install missing SDK packages"

3. **构建工具**
   - 自动配置 Gradle
   - 配置 Android 构建工具

**等待所有同步完成后再继续！**

### 5. 基本配置

#### 5.1 应用信息

打开 `android/app/build.gradle`:

```gradle
android {
    namespace "com.newsgap.app"
    compileSdk 34  // 目标 SDK 版本
    
    defaultConfig {
        applicationId "com.newsgap.app"  // 应用包名（发布时建议修改为唯一值）
        minSdk 22          // 最低支持 Android 5.1
        targetSdk 34       // 目标 Android 14
        versionCode 1      // 内部版本号（每次发布递增）
        versionName "1.0.0"  // 显示版本号
    }
}
```

**发布前建议修改 `applicationId`**:
```gradle
applicationId "com.yourname.newsgap"  // 使用你的域名
```

#### 5.2 应用名称和图标

**应用名称**:
编辑 `android/app/src/main/res/values/strings.xml`:
```xml
<resources>
    <string name="app_name">NewsGap</string>
    <string name="title_activity_main">NewsGap</string>
</resources>
```

**应用图标**:
```
android/app/src/main/res/
├── mipmap-hdpi/ic_launcher.png       (72x72)
├── mipmap-mdpi/ic_launcher.png       (48x48)
├── mipmap-xhdpi/ic_launcher.png      (96x96)
├── mipmap-xxhdpi/ic_launcher.png     (144x144)
└── mipmap-xxxhdpi/ic_launcher.png    (192x192)

# 推荐使用 Android Studio 的 Image Asset 工具:
右键 res → New → Image Asset → Launcher Icons
```

#### 5.3 权限配置

编辑 `android/app/src/main/AndroidManifest.xml`:

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    
    <!-- 必需权限 -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    
    <!-- 可选权限 -->
    <!-- <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" /> -->
    <!-- <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" /> -->
    
    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/AppTheme"
        android:usesCleartextTraffic="true">  <!-- 允许 HTTP（开发用）-->
        
        <!-- MainActivity -->
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:launchMode="singleTask"
            android:theme="@style/AppTheme.NoActionBarLaunch">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```

---

## 📱 在模拟器中运行

### 6. 创建 Android 虚拟设备 (AVD)

#### 方式 1: 通过 AVD Manager（推荐）

```bash
1. Android Studio → Tools → Device Manager
2. 点击 "Create Device"
3. 选择设备定义:
   推荐: Pixel 6 (常用), Pixel 4a (小屏), Pixel 7 Pro (大屏)
4. 选择系统映像:
   推荐: Android 14 (API 34) - x86_64 / arm64-v8a
   如果需要下载，点击旁边的下载图标
5. 验证配置:
   - RAM: 至少 2048 MB
   - VM heap: 256 MB
   - Internal Storage: 2048 MB
6. 点击 "Finish"
```

#### 方式 2: 命令行

```bash
# 列出可用的系统映像
sdkmanager --list | grep system-images

# 下载系统映像
sdkmanager "system-images;android-34;google_apis;x86_64"

# 创建 AVD
avdmanager create avd -n Pixel_6_API_34 -k "system-images;android-34;google_apis;x86_64" -d pixel_6

# 启动模拟器
emulator -avd Pixel_6_API_34
```

### 7. 运行应用

#### 在 Android Studio 中运行

```bash
1. 确保 Gradle 同步完成
2. 点击顶部工具栏的设备选择器
3. 选择你创建的模拟器
4. 点击绿色的 Run 按钮 (▶️) 或按 Shift+F10
5. 等待构建和安装（首次需要 3-5 分钟）
6. 应用会自动启动
```

#### 使用命令行

```bash
# 方式 1: Capacitor CLI
cd frontend
npx cap run android

# 方式 2: Gradle
cd frontend/android
./gradlew installDebug  # Linux/macOS
gradlew.bat installDebug  # Windows

# 然后手动启动应用
```

### 8. 调试

#### Logcat（查看日志）

```bash
# Android Studio 底部的 Logcat 标签
# 过滤器推荐设置:
- Package: com.newsgap.app
- Log Level: Debug

# 常见日志标签:
- Capacitor: Capacitor 框架日志
- Console: JavaScript console.log 输出
- SQLite: 数据库操作日志
- Network: 网络请求日志
```

#### Chrome DevTools

```bash
1. 在应用中打开 WebView
2. Chrome 浏览器访问: chrome://inspect
3. 找到 "Remote Target" 下的 NewsGap
4. 点击 "inspect"
5. 可以使用完整的 DevTools:
   - Console (查看日志)
   - Network (网络请求)
   - Application (本地存储)
   - Sources (调试 JavaScript)
```

#### 调试命令

```javascript
// 在代码中添加调试
console.log('调试信息:', data);
console.error('错误:', error);

// 检查平台
import { Capacitor } from '@capacitor/core';
console.log('平台:', Capacitor.getPlatform()); // 'android'

// 检查原生功能
console.log('是否为原生:', Capacitor.isNativePlatform()); // true
```

---

## 📲 在真机上运行

### 9. 准备 Android 设备

#### 启用开发者选项

```bash
1. 打开设置
2. 关于手机 → 连续点击"版本号" 7次
3. 返回设置 → 系统 → 开发者选项
4. 开启"开发者选项"
5. 开启"USB 调试"
```

#### 连接设备

```bash
# USB 连接
1. 使用 USB 线连接手机到电脑
2. 手机上选择"文件传输"模式
3. 允许 USB 调试（弹窗）

# 验证连接
adb devices
# 应该显示你的设备
```

#### 无线调试 (Android 11+)

```bash
1. 手机和电脑连接同一 Wi-Fi
2. 设置 → 开发者选项 → 无线调试
3. 点击"使用配对码配对设备"
4. 记住 IP 和端口

# 电脑上执行
adb pair <IP>:<配对端口>
# 输入配对码

adb connect <IP>:<无线调试端口>

# 验证
adb devices
```

### 10. 在真机上运行

```bash
1. Android Studio 设备选择器中选择你的设备
2. 点击 Run (▶️)
3. 应用会自动安装到手机
4. 首次安装可能需要在手机上确认
```

---

## 🧪 测试功能

### 11. 测试清单

#### ✅ 数据库功能
```bash
测试步骤:
1. 首次启动应用
2. 连接 Chrome DevTools (chrome://inspect)
3. Console 中查看数据库初始化日志
4. 执行一次"一键情报"
5. 检查文章列表
6. 重启应用，确认数据持久化
```

#### ✅ RSS 爬取
```bash
测试步骤:
1. 进入首页
2. 选择行业
3. 点击"一键情报"
4. 查看 Logcat:
   - 搜索 "Capacitor/Console"
   - 应该看到 RSS 请求日志
5. 确认文章加载成功
```

#### ✅ LLM 分析
```bash
前置条件:
1. 进入设置
2. 配置 Gemini API Key
3. 保存

测试步骤:
1. 返回首页
2. 执行"一键情报"
3. 等待分析完成
4. 进入"分析列表"
5. 检查分析结果
```

#### ✅ 本地存储
```bash
测试步骤:
1. 生成多条数据
2. 完全关闭应用（从最近任务中划掉）
3. 重新打开
4. 确认数据保留:
   - 文章
   - 分析
   - API Key
   - 自定义分类
```

#### ✅ 权限
```bash
测试步骤:
1. 首次运行检查网络访问
2. 设置 → 应用 → NewsGap → 权限
3. 确认已授予必要权限
```

#### ✅ 性能
```bash
测试指标:
- 启动时间 < 3 秒
- RSS 爬取时间合理
- 列表滚动流畅
- 无 ANR (应用无响应)
- 内存使用合理
```

---

## 📦 构建生产版本

### 12. 生成签名密钥

**首次构建需要创建签名密钥**:

```bash
# 使用 keytool 生成密钥库
keytool -genkey -v -keystore newsgap-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias newsgap

# 按提示输入:
- 密钥库密码（记住它！）
- 名字和组织信息
- 密钥密码（可以与密钥库密码相同）

# 会生成 newsgap-release-key.jks 文件
# ⚠️ 妥善保管此文件，丢失后无法更新应用！
```

### 13. 配置签名

创建 `android/keystore.properties`:

```properties
storePassword=你的密钥库密码
keyPassword=你的密钥密码
keyAlias=newsgap
storeFile=/path/to/newsgap-release-key.jks
```

**⚠️ 重要**: 将此文件添加到 `.gitignore`:

```bash
echo "android/keystore.properties" >> .gitignore
echo "*.jks" >> .gitignore
```

修改 `android/app/build.gradle`:

```gradle
android {
    // ... 其他配置
    
    // 加载签名配置
    def keystorePropertiesFile = rootProject.file("keystore.properties")
    def keystoreProperties = new Properties()
    if (keystorePropertiesFile.exists()) {
        keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
    }
    
    signingConfigs {
        release {
            if (keystorePropertiesFile.exists()) {
                keyAlias keystoreProperties['keyAlias']
                keyPassword keystoreProperties['keyPassword']
                storeFile file(keystoreProperties['storeFile'])
                storePassword keystoreProperties['storePassword']
            }
        }
    }
    
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true  // 启用代码混淆
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}
```

### 14. 构建 APK

#### Debug 版本（测试用）

```bash
cd frontend/android

# Linux/macOS
./gradlew assembleDebug

# Windows
gradlew.bat assembleDebug

# 输出位置:
# android/app/build/outputs/apk/debug/app-debug.apk
```

#### Release 版本（发布用）

```bash
cd frontend/android

# Linux/macOS
./gradlew assembleRelease

# Windows
gradlew.bat assembleRelease

# 输出位置:
# android/app/build/outputs/apk/release/app-release.apk

# 查看 APK 信息
aapt dump badging app-release.apk
```

### 15. 构建 AAB (Android App Bundle)

**推荐用于 Google Play 发布**:

```bash
cd frontend/android

# Linux/macOS
./gradlew bundleRelease

# Windows
gradlew.bat bundleRelease

# 输出位置:
# android/app/build/outputs/bundle/release/app-release.aab
```

**AAB vs APK**:
- **AAB**: Google Play 推荐，自动优化，文件更小
- **APK**: 通用格式，可以直接安装

---

## 🐛 常见问题

### 问题 1: Gradle 同步失败

```
错误信息: Gradle sync failed: Connection timed out

解决方案:
# 配置国内镜像（中国用户）
编辑 android/build.gradle:

allprojects {
    repositories {
        maven { url 'https://maven.aliyun.com/repository/google' }
        maven { url 'https://maven.aliyun.com/repository/jcenter' }
        maven { url 'https://maven.aliyun.com/repository/public' }
        google()
        mavenCentral()
    }
}
```

### 问题 2: SDK 版本问题

```
错误信息: Failed to find target with hash string 'android-34'

解决方案:
1. Android Studio → Tools → SDK Manager
2. SDK Platforms 标签 → 勾选 Android 14.0 (API 34)
3. SDK Tools 标签 → 勾选 Android SDK Build-Tools 34
4. 点击 Apply 下载
5. 重新同步 Gradle
```

### 问题 3: "App not installed" 错误

```
错误信息: App not installed as package appears to be invalid

可能原因:
1. 签名不匹配（安装了不同签名的版本）
2. APK 损坏

解决方案:
# 卸载旧版本
adb uninstall com.newsgap.app

# 重新安装
adb install app-release.apk
```

### 问题 4: SQLite 插件错误

```
错误信息: SQLite plugin not available

解决方案:
cd frontend

# 重新安装插件
npm uninstall @capacitor-community/sqlite
npm install @capacitor-community/sqlite

# 同步
npx cap sync android

# 清理并重新构建
cd android
./gradlew clean
./gradlew assembleDebug
```

### 问题 5: CORS / 网络请求失败

```
错误信息: net::ERR_CLEARTEXT_NOT_PERMITTED

原因: Android 9+ 默认禁止 HTTP

解决方案:
在 AndroidManifest.xml 中添加:
<application
    android:usesCleartextTraffic="true">
    
注意: 生产环境应该只使用 HTTPS
```

### 问题 6: WebView 白屏

```
可能原因:
1. Web 资源未正确构建
2. capacitor.config.ts 配置错误

解决方案:
cd frontend
npm run build
npx cap sync android
npx cap open android
# 重新 Run
```

### 问题 7: ADB 找不到设备

```
错误信息: no devices/emulators found

解决方案:
# 重启 ADB
adb kill-server
adb start-server
adb devices

# 检查 USB 调试
手机: 设置 → 开发者选项 → USB 调试 (开启)

# Windows: 可能需要安装驱动
访问手机厂商官网下载 USB 驱动
```

### 问题 8: Out of Memory

```
错误信息: OutOfMemoryError: Java heap space

解决方案:
编辑 android/gradle.properties:

org.gradle.jvmargs=-Xmx4096m -XX:MaxPermSize=512m -XX:+HeapDumpOnOutOfMemoryError -Dfile.encoding=UTF-8
```

---

## 🔄 更新应用

### 修改代码后更新

```bash
# 1. 修改 React/TypeScript 代码
# 编辑 frontend/src/ 下的文件

# 2. 重新构建
cd frontend
npm run build

# 3. 同步到 Android
npx cap sync android

# 4. 在 Android Studio 中 Run
# 或
npx cap run android
```

### 热重载 (Live Reload)

```bash
# 开发时启用热重载:

# 1. 启动开发服务器
cd frontend
npm run dev
# 记住地址，如 http://192.168.1.100:5173

# 2. 修改 capacitor.config.ts
{
  server: {
    url: 'http://192.168.1.100:5173',
    cleartext: true
  }
}

# 3. 同步并运行
npx cap sync android
npx cap run android

# 4. 现在修改代码会自动刷新应用

# 5. 发布前删除 server 配置！
```

---

## 📊 性能优化

### ProGuard 混淆

创建 `android/app/proguard-rules.pro`:

```proguard
# Capacitor
-keep class com.getcapacitor.** { *; }
-keep @com.getcapacitor.annotation.CapacitorPlugin class * { *; }

# SQLite
-keep class io.sqlc.** { *; }

# 保留 JavaScript 接口
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}

# 保留 JSON 序列化类
-keepattributes Signature
-keepattributes *Annotation*

# Gson (如果使用)
-keep class com.google.gson.** { *; }
```

### 减小 APK 大小

编辑 `android/app/build.gradle`:

```gradle
android {
    buildTypes {
        release {
            minifyEnabled true
            shrinkResources true  // 移除未使用资源
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
    
    // 分架构构建（可选）
    splits {
        abi {
            enable true
            reset()
            include 'armeabi-v7a', 'arm64-v8a', 'x86', 'x86_64'
            universalApk true
        }
    }
}
```

### 启动性能优化

```xml
<!-- AndroidManifest.xml -->
<activity
    android:name=".MainActivity"
    android:theme="@style/AppTheme.NoActionBarLaunch"
    android:windowSoftInputMode="adjustResize"
    android:launchMode="singleTask"
    android:configChanges="orientation|keyboardHidden|keyboard|screenSize|locale|smallestScreenSize|screenLayout|uiMode">
```

---

## 📝 版本管理

### 更新版本号

编辑 `android/app/build.gradle`:

```gradle
android {
    defaultConfig {
        versionCode 2        // 每次发布递增（整数）
        versionName "1.1.0"  // 显示给用户的版本
    }
}
```

**版本规则**:
- `versionCode`: 内部版本号，必须递增（1, 2, 3, ...）
- `versionName`: 语义化版本（1.0.0, 1.1.0, 2.0.0）

---

## 🎯 发布到 Google Play

### 完整流程

#### 1. 注册 Google Play 开发者账号
```
1. 访问 https://play.google.com/console
2. 支付 $25 注册费（一次性）
3. 填写开发者信息
4. 等待审核（1-2 天）
```

#### 2. 创建应用

```
1. Play Console → 所有应用 → 创建应用
2. 填写应用详情:
   - 应用名称: NewsGap
   - 默认语言: 简体中文
   - 应用类型: 应用
   - 免费或付费: 免费
```

#### 3. 准备商店列表

```
必需内容:
- 应用图标 (512x512, PNG, 32-bit)
- 功能图片 (1024x500)
- 手机截图 (至少 2 张, 最多 8 张)
  - 16:9 比例: 1920x1080
  - 9:16 比例: 1080x1920
- 应用描述 (简短 + 完整)
- 应用类别
- 联系邮箱
- 隐私政策链接
```

#### 4. 内容分级

```
1. 完成内容分级问卷
2. 根据应用内容回答问题
3. 获取分级证书
```

#### 5. 设置价格和发布区域

```
1. 选择免费
2. 选择发布国家/地区
3. 配置应用内购（如果有）
```

#### 6. 上传 AAB

```
1. 生成签名的 AAB:
   cd frontend/android
   ./gradlew bundleRelease

2. Play Console → 版本 → 生产版
3. 创建新版本
4. 上传 app-release.aab
5. 填写版本说明
6. 保存并审核
```

#### 7. 提交审核

```
1. 检查所有必填项
2. 提交审核
3. 等待审核（通常 1-7 天）
4. 通过后应用自动发布
```

### 更新应用

```bash
# 1. 更新版本号
编辑 build.gradle:
versionCode 2
versionName "1.1.0"

# 2. 构建新版本
./gradlew bundleRelease

# 3. 上传到 Play Console
生产版 → 创建新版本 → 上传 AAB

# 4. 填写更新说明
如: "修复已知问题，优化性能"

# 5. 提交审核
```

---

## 🧪 内部测试 & Beta 测试

### 内部测试

```
1. Play Console → 版本 → 内部测试
2. 创建内部测试版本
3. 上传 AAB
4. 添加测试者邮箱
5. 分享测试链接
6. 测试者可以立即下载测试
```

### 公开测试（Beta）

```
1. 版本 → 公开测试
2. 上传 AAB
3. 设置测试人数上限（可选）
4. 发布测试版本
5. 用户可以在 Play 商店加入测试
```

---

## 📚 参考资源

- [Capacitor Android 文档](https://capacitorjs.com/docs/android)
- [Android 开发者文档](https://developer.android.com/docs)
- [Android Studio 用户指南](https://developer.android.com/studio/intro)
- [Google Play 发布流程](https://support.google.com/googleplay/android-developer/answer/9859152)
- [NewsGap 移动端架构文档](./mobile-app-architecture.md)

---

## 💡 最佳实践

### 开发流程

```
1. 使用 Live Reload 提高开发效率
2. 定期在真机测试（模拟器有局限性）
3. 使用 Chrome DevTools 调试 WebView
4. 监控 Logcat 日志
5. 测试不同 Android 版本（至少 3 个版本）
6. 测试不同屏幕尺寸
7. 测试低端设备性能
```

### 代码质量

```
1. 启用 ProGuard 混淆
2. 移除未使用的资源
3. 优化图片资源
4. 使用 AAB 而不是 APK
5. 定期更新依赖
6. 进行内存泄漏检测
```

### 安全性

```
1. API Key 不要硬编码
2. 使用 HTTPS (生产环境)
3. 签名密钥妥善保管（备份！）
4. 启用 ProGuard 代码混淆
5. 定期安全审计
6. 遵循 Android 安全最佳实践
```

---

## ✅ 发布前检查清单

- [ ] 所有功能测试通过
- [ ] 在真机上测试通过（至少 3 个设备）
- [ ] 测试不同 Android 版本
- [ ] 性能可接受（启动 < 3秒，无 ANR）
- [ ] 无内存泄漏
- [ ] 无崩溃
- [ ] 网络权限正常
- [ ] versionCode 和 versionName 已更新
- [ ] applicationId 正确（唯一）
- [ ] 签名配置正确
- [ ] ProGuard 规则完整
- [ ] 图标和截图准备完毕
- [ ] Google Play 商店信息填写完整
- [ ] 隐私政策已发布
- [ ] 内容分级已完成

---

## 🎉 总结

Android 构建相对简单：

✅ **优点**:
- 任何系统都可以开发
- 模拟器启动快
- 调试工具强大
- 发布流程简单
- 一次性费用 ($25)

⚠️ **注意**:
- 妥善保管签名密钥
- 测试多个设备和版本
- 遵循 Google Play 政策
- 定期更新和维护

---

**需要帮助？** 请参考 [常见问题](#-常见问题) 或提交 Issue。

🚀 祝你构建顺利！
