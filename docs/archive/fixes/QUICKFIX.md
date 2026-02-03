# 快速修复参考卡片

## 🎯 核心改进

### RSS 源策略 ✅
```
❌ rsshub.app (SSL 错误)
↓
✅ 原生 RSS 源 (稳定可靠)
```

### 金融源状态 ✅
```
可用: 6 个原生 RSS 源
类型: FT中文网、新浪财经、东方财富等
状态: 无 SSL 问题，稳定可用
```

### Debug 日志 ✅
```bash
# 后端终端实时显示：
[DEBUG] 开始爬取 finance 行业
[DEBUG] 信息源数量: 6
[DEBUG] 正在爬取: FT中文网
[DEBUG] 获取到 15 篇文章
[DEBUG] 爬取完成! 文章总数: 68 篇
[DEBUG] 开始分析
[DEBUG] 第一篇文章标题: XXX
```

### 前端路由 ✅
```
/analysis       → 分析列表页（历史报告）
/analysis/:id   → 分析详情页（单个报告）
```

---

## 🚀 快速测试

```bash
# 1. 重启后端（查看日志）
cd /Users/roson/workspace/NewsGap/backend
./venv/bin/python3 main.py

# 2. 访问前端
http://localhost:5173

# 3. 测试金融情报
首页 → 选择"金融" → "一键情报"

# 4. 查看后端日志
应该看到完整的爬取和分析日志
```

---

## 📊 期望结果

### 爬取阶段
- ✅ 6 个金融源开始爬取
- ✅ 至少 3-4 个源成功
- ✅ 获取 50+ 篇文章
- ✅ 无 SSL 错误

### 分析阶段
- ✅ 文章标题是最新的（非缓存）
- ✅ 成功生成 Markdown 报告
- ✅ 自动跳转到报告详情页

### 前端显示
- ✅ `/analysis` 显示分析列表
- ✅ `/analysis/{id}` 显示完整报告
- ✅ 侧边栏链接正常工作

---

## 🔍 问题排查

### 如果还是 SSL 错误
```bash
# 检查是否还有 rsshub.app 源
cd backend
./venv/bin/python3 validate_sources.py
# 禁用所有 rsshub.app 源
```

### 如果文章是旧的
```bash
# 查看后端日志中的文章 ID
[DEBUG] 文章ID列表: [...]
# 确认 ID 是本次生成的（不是之前的）
```

### 如果路由 404
```bash
# 确认前端已更新
cd frontend
# 重启前端开发服务器
npm run dev
```

---

## 📝 重要文件

### 后端
- `routes/intelligence.py` - 爬取和分析逻辑（含日志）
- `data/newsgap.db` - 数据库（已更新金融源）

### 前端
- `pages/AnalysisList.tsx` - 新增的列表页
- `pages/Analysis.tsx` - 详情页
- `App.tsx` - 路由配置

### 文档
- `docs/latest-fix.md` - 详细修复说明
- `docs/rss-sources-fix.md` - RSS 源维护指南

---

## 💡 关键点

1. **完全弃用 rsshub.app** - 改用原生 RSS
2. **Debug 日志** - 后端终端实时查看
3. **新路由** - `/analysis` 列表页已添加
4. **金融源** - 6 个稳定可用

---

## ✅ 检查清单

- [ ] 后端启动，能看到初始化日志
- [ ] 选择金融行业
- [ ] 点击一键情报
- [ ] 后端显示详细爬取日志
- [ ] 成功获取 50+ 篇文章
- [ ] 分析完成，自动跳转
- [ ] 显示完整 Markdown 报告
- [ ] 点击侧边栏"分析结果"正常显示

---

**现在可以测试了！** 🎉
