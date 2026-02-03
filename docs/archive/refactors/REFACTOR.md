# 快速操作指南 - 3 步完成重构

## ⚡ 快速开始

```bash
# 第1步：启动 RSSHub (30秒)
cd /Users/roson/workspace/NewsGap
docker-compose up -d

# 第2步：重构信息源 (10秒)
cd backend
./venv/bin/python3 refactor_sources.py

# 第3步：启动后端测试 (即刻)
./venv/bin/python3 main.py
```

然后访问 `http://localhost:5173`，选择行业，点击"一键情报"。

---

## 🔍 验证检查

### Docker 检查
```bash
docker ps
# 应该看到: newsgap-rsshub   Up
```

### RSSHub 检查
```bash
curl http://localhost:1200/
# 应该返回: RSSHub 首页
```

### 源数量检查
```bash
# 应该显示: ✓ 成功添加 29/29 个源
```

---

## 📊 期望结果

### 爬取阶段（后端日志）
```
[DEBUG] 爬取完成!
[DEBUG] 成功: 10/12 个源
[DEBUG] 文章总数: 150+ 篇
[DEBUG] 新文章: 120+ 篇
```

### 分析阶段（后端日志）
```
[DEBUG] 本次爬取的文章ID数量: 150
[DEBUG] 第一篇: [最新标题]
[DEBUG] 发布时间: 2026-01-30 [当天时间]
```

### 关键指标
- ✅ 无 SSL 错误
- ✅ 80%+ 源成功
- ✅ 100+ 篇文章
- ✅ 文章是当天的
- ✅ 分析结果匹配

---

## ⚠️ 如果出错

### RSSHub 无法启动
```bash
# 检查端口
lsof -i :1200
# 如果被占用，修改 docker-compose.yml 中的端口

# 重新启动
docker-compose down
docker-compose up -d
```

### 文章还是旧的
1. 检查后端日志中的**发布时间**
2. 确认是今天的日期
3. 如果不是，查看爬取失败的源

### 某些源失败
- 正常情况，不影响使用
- 只要成功率 > 80% 即可
- 可以在设置页面禁用失败的源

---

## 📝 重要提示

1. **先启动 RSSHub** - 不然所有本地源都会失败
2. **观察后端日志** - 这是诊断问题的关键
3. **验证文章时间** - 确保是当天最新的
4. **清除浏览器缓存** - 如果前端显示异常

---

## 🎯 完整文档

详细说明请查看：`docs/refactor-guide.md`

---

**开始重构吧！** 🚀
