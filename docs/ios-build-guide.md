# iOS 构建指南

完整的 NewsGap iOS 应用构建和测试指南。

---

## 📋 前置要求

### 必需
- **macOS** 系统 (Xcode 只能在 macOS 上运行)
- **Xcode 15.0+** ([从 App Store 下载](https://apps.apple.com/us/app/xcode/id497799835))
- **Node.js 18+** 和 npm
- **CocoaPods** (Xcode 会自动安装，或运行 `sudo gem install cocoapods`)

### 可选（用于真机测试和发布）
- **Apple Developer Account** ([注册地址](https://developer.apple.com))
  - 免费账号：可以在真机测试 7 天
  - 付费账号（$99/年）：可以发布到 App Store

---

## 🚀 快速开始

### 1. 环境准备

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

# 同步到 iOS 项目
npx cap sync ios
```

### 2. 打开 Xcode 项目

```bash
# 方式 1：使用 Capacitor CLI（推荐）
npx cap open ios

# 方式 2：手动打开
open ios/App/App.xcworkspace
```

**重要**: 必须打开 `.xcworkspace` 文件，不是 `.xcodeproj` 文件！

---

## 🔧 Xcode 项目配置

### 3. 基本配置

打开 Xcode 后，在左侧项目导航器中选择顶部的 **App** 项目：

#### 3.1 通用设置（General）

1. **Display Name**: `NewsGap`（应用显示名称）
2. **Bundle Identifier**: `com.newsgap.app`
   - 如果需要发布，建议改为你自己的域名，如 `com.yourname.newsgap`
3. **Version**: `1.0.0`
4. **Build**: `1`
5. **Deployment Target**: `iOS 13.0`（最低支持的 iOS 版本）

#### 3.2 签名和能力（Signing & Capabilities）

**开发测试（使用个人 Apple ID）:**

1. 在 **Team** 下拉菜单中选择 **Add Account...**
2. 登录你的 Apple ID
3. 选择你的团队（Personal Team）
4. 勾选 **Automatically manage signing**
5. Xcode 会自动生成开发证书和配置文件

**生产发布（需要付费开发者账号）:**

1. 登录 [Apple Developer](https://developer.apple.com)
2. 创建 App ID
3. 创建 Distribution Certificate
4. 创建 Provisioning Profile
5. 在 Xcode 中选择对应的 Team 和 Profile

#### 3.3 所需能力（Capabilities）

NewsGap 需要以下能力，Capacitor 会自动配置：

- ✅ **App Sandbox** (macOS only)
- ✅ **Outgoing Connections (Client)** - 用于网络请求

如果使用推送通知或其他功能，可能需要额外添加：

```
可选能力：
- Push Notifications（推送通知）
- Background Modes（后台模式）
- iCloud（云同步）
```

---

## 📱 在模拟器中运行

### 4. 选择模拟器

1. 在 Xcode 顶部工具栏中，点击设备选择器
2. 选择一个模拟器，推荐：
   - **iPhone 15 Pro** (最新)
   - **iPhone 14** (常用)
   - **iPhone SE (3rd generation)** (小屏幕测试)

### 5. 运行应用

```bash
# 方式 1：Xcode 界面
点击左上角的 ▶️ (Run) 按钮，或按 ⌘R

# 方式 2：命令行
npx cap run ios
```

**首次运行**:
- Xcode 会自动安装模拟器（如果未安装）
- 构建过程需要 2-5 分钟
- 完成后应用会自动启动

### 6. 调试

#### 查看日志

**Xcode 控制台**:
- Xcode 底部的控制台会显示所有日志
- 使用 `console.log()` 输出调试信息

**Safari 开发者工具**:
```bash
# 1. 在 Safari 中启用开发菜单
# Safari → 偏好设置 → 高级 → 勾选"在菜单栏中显示开发菜单"

# 2. 运行应用后
# Safari → 开发 → [你的模拟器] → localhost

# 3. 打开 Web Inspector，可以：
- 查看 Console 日志
- 检查网络请求
- 调试 JavaScript
- 查看本地存储
```

#### 常见调试命令

```javascript
// 在代码中添加调试日志
console.log('调试信息:', data);
console.error('错误:', error);

// 检查平台
import { Capacitor } from '@capacitor/core';
console.log('平台:', Capacitor.getPlatform()); // 'ios'

// 检查原生功能
console.log('是否为原生:', Capacitor.isNativePlatform()); // true
```

---

## 📲 在真机上运行

### 7. 准备 iOS 设备

1. **连接设备**: 使用 USB 线连接 iPhone/iPad 到 Mac
2. **信任电脑**: 设备上会弹出"信任此电脑"，点击信任
3. **启用开发者模式**:
   - iOS 16+: 设置 → 隐私与安全 → 开发者模式 → 开启
   - 重启设备

### 8. 选择设备并运行

1. 在 Xcode 设备选择器中选择你的 iPhone/iPad
2. 点击 Run (⌘R)
3. Xcode 会自动安装应用到设备

### 9. 信任开发者证书（首次运行）

如果使用免费 Apple ID，首次运行会失败，需要手动信任：

1. 设备上打开: **设置 → 通用 → VPN 与设备管理**
2. 找到你的 Apple ID
3. 点击 **信任 "your@email.com"**
4. 确认信任
5. 返回主屏幕，重新打开应用

---

## 🧪 测试功能

### 10. 测试清单

运行应用后，逐项测试以下功能：

#### ✅ 数据库功能
```bash
测试步骤:
1. 首次启动应用
2. 打开 Safari Web Inspector
3. Console 中应该能看到数据库初始化日志
4. 执行一次"一键情报"
5. 检查文章列表是否显示
6. 重启应用，数据应该保留
```

#### ✅ RSS 爬取
```bash
测试步骤:
1. 进入首页
2. 选择行业（如"AI"）
3. 点击"一键情报"
4. 观察 Console 日志:
   - 应该看到 "Fetching RSS from..." 日志
   - 应该看到文章数量
5. 检查网络请求（Network 标签）
6. 确认文章列表加载成功
```

#### ✅ LLM 分析
```bash
前置条件:
1. 进入设置页面
2. 配置 Gemini API Key:
   - 如果没有，访问 https://makersuite.google.com/app/apikey
   - 复制 API Key 并粘贴到设置中
   - 保存

测试步骤:
1. 返回首页
2. 执行"一键情报"
3. 等待分析完成（10-30秒）
4. 进入"分析列表"查看结果
5. 检查分析内容是否完整
```

#### ✅ 本地存储
```bash
测试步骤:
1. 执行几次"一键情报"，生成多条数据
2. 完全关闭应用（从后台清除）
3. 重新打开应用
4. 检查:
   - 历史文章是否还在
   - 历史分析是否还在
   - API Key 是否还在（设置页面）
   - 自定义分类是否保留
```

#### ✅ 网络权限
```bash
测试步骤:
1. 首次运行时应该弹出网络权限请求
2. 如果没有弹出，检查:
   - 设置 → 隐私 → 本地网络
   - 找到 NewsGap，确保开启
```

---

## 📦 构建生产版本

### 11. Archive（归档）

准备提交到 App Store 或分发给测试者：

```bash
# 1. 选择 Generic iOS Device
在设备选择器中选择 "Any iOS Device (arm64)"

# 2. Product → Archive
或使用快捷键: ⌘ + ⇧ + B（Build）然后 Product → Archive

# 3. 等待构建完成（3-10 分钟）
完成后会自动打开 Organizer 窗口
```

### 12. 导出 IPA

**方式 1: App Store 分发**
```
1. 在 Organizer 中选择刚创建的 Archive
2. 点击 "Distribute App"
3. 选择 "App Store Connect"
4. 选择 "Upload"
5. 选择签名选项（自动管理）
6. 点击 "Upload"
7. 等待上传完成
8. 登录 App Store Connect 提交审核
```

**方式 2: Ad Hoc 分发（内部测试）**
```
1. 选择 Archive → Distribute App
2. 选择 "Ad Hoc"
3. 选择签名和设备
4. 导出 IPA 文件
5. 通过 TestFlight 或直接安装分发
```

**方式 3: Development 构建（开发测试）**
```
1. 选择 "Development"
2. 选择设备
3. 导出 IPA
4. 使用 Xcode 或工具安装到测试设备
```

---

## 🐛 常见问题

### 问题 1: "Failed to register bundle identifier"

```
错误信息: The app identifier "com.newsgap.app" cannot be registered to your development team.

解决方案:
1. 修改 Bundle Identifier 为唯一值
2. 格式: com.yourname.newsgap
3. 在 Xcode → General → Bundle Identifier 修改
```

### 问题 2: "Code signing failed"

```
错误信息: No signing certificate "iOS Development" found

解决方案:
1. Xcode → Settings → Accounts
2. 选择你的 Apple ID
3. 点击 "Manage Certificates..."
4. 点击 "+" → "iOS Development"
5. 重新 Build
```

### 问题 3: 应用启动后白屏

```
可能原因:
1. Web 资源未正确构建
2. Capacitor 配置错误

解决方案:
cd frontend
npm run build
npx cap sync ios
npx cap open ios
# 重新 Run
```

### 问题 4: SQLite 初始化失败

```
错误信息: SQLite plugin not initialized

检查步骤:
1. 确认 Capacitor 版本一致:
   npx cap doctor
   
2. 重新安装 SQLite 插件:
   npm uninstall @capacitor-community/sqlite
   npm install @capacitor-community/sqlite
   npx cap sync ios
   
3. 检查 Podfile:
   cd ios/App
   pod install
```

### 问题 5: 网络请求失败

```
错误信息: Network request failed / CORS error

原因: iOS 需要配置 App Transport Security (ATS)

解决方案:
在 ios/App/App/Info.plist 中添加:

<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>

注意: 生产环境建议配置具体域名
```

### 问题 6: "Unable to install..."

```
错误信息: Unable to install "NewsGap"

解决方案:
1. 删除设备上的旧版本应用
2. 清理 Build:
   Xcode → Product → Clean Build Folder (⌘⇧K)
3. 重启 Xcode
4. 重启设备
5. 重新 Build
```

### 问题 7: CocoaPods 相关错误

```
错误信息: [!] CocoaPods could not find compatible versions for pod...

解决方案:
cd ios/App
rm -rf Pods Podfile.lock
pod repo update
pod install
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

# 3. 同步到 iOS
npx cap sync ios

# 4. 在 Xcode 中 Run
# Xcode 会自动检测更改并重新构建
```

### 修改原生代码后更新

```bash
# 如果修改了:
- ios/App/App/Info.plist
- ios/App/Podfile
- Capacitor 插件配置

# 需要:
cd ios/App
pod install
# 然后在 Xcode 中 Clean Build Folder 并 Run
```

### 热重载（Live Reload）

```bash
# 开发时启用热重载，无需每次重新构建:

# 1. 启动开发服务器
cd frontend
npm run dev
# 记住显示的 URL，如 http://192.168.1.100:5173

# 2. 修改 capacitor.config.ts
{
  server: {
    url: 'http://192.168.1.100:5173',  // 你的开发服务器地址
    cleartext: true
  }
}

# 3. 在 Xcode 中 Run
# 应用会从开发服务器加载，支持热重载

# 4. 发布前记得删除 server 配置！
```

---

## 📊 性能优化

### 构建优化

```javascript
// vite.config.ts
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'router': ['react-router-dom'],
          'ui': ['antd', '@ant-design/icons'],
        }
      }
    }
  }
});
```

### 启动性能

```typescript
// src/mobile-services/mobile-api.ts
// 延迟非关键初始化

async initialize() {
  // 关键: 立即初始化
  await this.db.initialize();
  
  // 非关键: 后台初始化
  setTimeout(() => {
    this.loadCachedData();
  }, 1000);
}
```

---

## 📝 版本管理

### 更新版本号

```bash
# 在 Xcode 中:
1. 选择项目 → General
2. 更新 Version (如 1.0.0 → 1.1.0)
3. 更新 Build (如 1 → 2)

# 或在 Info.plist 中:
CFBundleShortVersionString = 1.1.0  (Version)
CFBundleVersion = 2                  (Build)
```

### 语义化版本

```
主版本.次版本.修订版本

1.0.0 - 初始发布
1.1.0 - 新功能
1.1.1 - Bug 修复
2.0.0 - 重大更新（不兼容）
```

---

## 🎯 发布到 App Store

### 完整流程

1. **准备**
   - 申请付费开发者账号（$99/年）
   - 准备应用图标（1024x1024 无透明度）
   - 准备截图（不同设备尺寸）
   - 准备应用描述、关键词

2. **App Store Connect**
   - 登录 https://appstoreconnect.apple.com
   - 创建新应用
   - 填写应用信息
   - 上传截图和图标

3. **Xcode Archive & Upload**
   - Product → Archive
   - Distribute App → App Store Connect
   - Upload

4. **提交审核**
   - 在 App Store Connect 中提交审核
   - 等待审核（1-3 天）
   - 通过后发布

---

## 📚 参考资源

- [Capacitor iOS 文档](https://capacitorjs.com/docs/ios)
- [Apple Developer 文档](https://developer.apple.com/documentation/)
- [Xcode 使用指南](https://developer.apple.com/xcode/)
- [App Store 审核指南](https://developer.apple.com/app-store/review/guidelines/)
- [NewsGap 移动端架构文档](./mobile-app-architecture.md)

---

## 💡 最佳实践

### 开发流程

```bash
1. 使用 Live Reload 开发（提高效率）
2. 定期在真机测试（模拟器不能完全代表真实设备）
3. 使用 Safari Web Inspector 调试
4. 检查内存泄漏（Instruments）
5. 测试不同 iOS 版本
6. 测试不同设备尺寸
```

### 代码质量

```bash
1. TypeScript 严格模式
2. ESLint + Prettier
3. 单元测试（Jest）
4. E2E 测试（可选）
5. Code Review
```

### 安全性

```bash
1. API Key 不要硬编码（使用 Preferences）
2. HTTPS only（生产环境）
3. 数据加密（敏感信息）
4. 定期更新依赖
5. 遵循 Apple 安全指南
```

---

## ✅ 检查清单

发布前确认：

- [ ] 所有功能测试通过
- [ ] 在真机上测试通过
- [ ] 性能可接受（启动 < 3秒）
- [ ] 无内存泄漏
- [ ] 无崩溃
- [ ] 隐私政策完整
- [ ] 版本号正确
- [ ] Bundle Identifier 正确
- [ ] 图标和截图准备完毕
- [ ] App Store 信息填写完整

---

**需要帮助？** 请参考 [常见问题](#-常见问题) 或提交 Issue。

🎉 祝你构建顺利！
