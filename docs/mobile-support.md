# 移动端适配说明

## 概述

此分支 (`mobile-support`) 为 NewsGap 项目添加了完整的移动端响应式支持,确保在各种屏幕尺寸的设备上都能提供良好的用户体验。

## 主要改进

### 1. 响应式导航
- **桌面端**: 固定侧边栏导航 (宽度 256px)
- **移动端**: 
  - 顶部固定导航栏,显示项目名称和汉堡菜单按钮
  - 点击汉堡菜单展开侧边栏导航
  - 包含半透明遮罩层,点击可关闭菜单
  - 使用 CSS transform 动画实现流畅的展开/收起效果

### 2. 响应式布局

#### 页面级优化
所有页面都针对移动端进行了优化:

- **首页 (Home.tsx)**
  - 标题字号: 桌面 4xl → 移动 2xl
  - 内边距: 桌面 py-12/px-6 → 移动 py-6/px-4
  - 按钮布局: 桌面横向 → 移动纵向堆叠
  - 时间范围选择: 使用 grid 布局适配小屏

- **文章列表 (Articles.tsx)**
  - 统计卡片: 桌面 4 列 → 移动 2 列
  - 筛选表单: 桌面横向 → 移动纵向
  - 批量操作工具栏: 多行布局优化
  - 文章卡片: 时间显示简化(移动端只显示日期)

- **设置页 (Settings.tsx)**
  - 表单字段: 桌面 2 列 → 移动 1 列
  - 代理配置: 响应式表单布局
  - 按钮: 桌面横向 → 移动纵向堆叠

- **分析列表 (AnalysisList.tsx)**
  - 卡片布局优化
  - 元数据显示: 桌面横向 → 移动纵向
  - 时间格式: 桌面完整时间 → 移动简化日期

- **归档管理 (Archive.tsx)**
  - 分类选择器: 响应式表单
  - 统计卡片: 桌面 3 列 → 移动 1-2 列
  - 文章列表: 元数据布局优化

### 3. 触摸优化

#### CSS 优化 (index.css)
```css
/* 移动端触摸优化 */
body {
  -webkit-tap-highlight-color: transparent;  /* 移除点击高亮 */
  touch-action: manipulation;                /* 优化触摸响应 */
}

/* 滚动优化 */
* {
  -webkit-overflow-scrolling: touch;         /* iOS 平滑滚动 */
}

/* 防止移动端自动缩放 */
input, select, textarea, button {
  font-size: 16px;  /* 移动端 */
}

@media (min-width: 768px) {
  input, select, textarea, button {
    font-size: 14px;  /* 桌面端 */
  }
}
```

### 4. 响应式断点

项目使用 Tailwind CSS 默认断点:

| 断点 | 最小宽度 | 描述 |
|------|---------|------|
| `sm` | 640px | 小屏设备 |
| `md` | 768px | 平板竖屏 |
| `lg` | 1024px | 平板横屏/小笔记本 |
| `xl` | 1280px | 桌面显示器 |

主要使用 `lg:` 断点区分桌面和移动端布局。

## 测试建议

### 浏览器开发者工具
1. 打开 Chrome DevTools (F12)
2. 切换到设备模拟器 (Ctrl/Cmd + Shift + M)
3. 测试以下设备:
   - iPhone SE (375px)
   - iPhone 12/13 Pro (390px)
   - iPad Mini (768px)
   - iPad Pro (1024px)

### 测试要点
- [ ] 导航菜单在移动端正常展开/收起
- [ ] 所有表单在小屏幕上可以正常填写
- [ ] 按钮和链接有足够的点击区域 (最小 44x44px)
- [ ] 文本内容不会溢出或被截断
- [ ] 滚动流畅,无卡顿
- [ ] 横屏和竖屏都能正常显示

## 技术栈

- **框架**: React 18 + TypeScript
- **样式**: Tailwind CSS 3.4
- **构建**: Vite 6
- **路由**: React Router 7

## 构建和部署

```bash
# 开发模式
cd frontend
npm run dev

# 生产构建
npm run build

# 预览构建结果
npm run preview
```

构建产物位于 `frontend/dist/` 目录,可直接部署到任何静态服务器。

## 未来改进

- [ ] 添加 PWA 支持(Service Worker, 离线访问)
- [ ] 优化图片加载(懒加载, WebP)
- [ ] 添加手势支持(滑动关闭菜单等)
- [ ] 性能优化(代码分割, 按需加载)
- [ ] 添加暗色主题支持

## 版本信息

- 分支: `mobile-support`
- 基于: `master` (bb0323e)
- 提交: d533488 "feat: 添加移动端响应式支持"

## 相关文件

```
frontend/
├── src/
│   ├── App.tsx              # 移动端导航主逻辑
│   ├── index.css            # 移动端全局样式
│   └── pages/
│       ├── Home.tsx         # 首页响应式
│       ├── Articles.tsx     # 文章列表响应式
│       ├── Settings.tsx     # 设置页响应式
│       ├── Archive.tsx      # 归档管理响应式
│       └── AnalysisList.tsx # 分析列表响应式
└── index.html               # viewport 配置
```
