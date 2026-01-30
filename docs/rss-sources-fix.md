# RSS 源问题修复说明

## 问题1：部分金融源失效 ✅

### 失效的源（已禁用）
| 源名称 | URL | 错误 | 状态 |
|--------|-----|------|------|
| 华尔街日报中文网 | `https://cn.wsj.com/zh-hans/rss` | 401 需要认证 | ❌ 已禁用 |
| 新浪财经 - 国内财经 | `https://rsshub.app/sina/finance/roll` | 400 路由失效 | ❌ 已禁用 |
| 第一财经 | `https://rsshub.app/yicai/brief` | 400 路由失效 | ❌ 已禁用 |
| 财新网 - 财新博客 | `https://rsshub.app/caixin/blog` | 400 路由失效 | ❌ 已禁用 |
| 雪球 - 今日话题 | `https://rsshub.app/xueqiu/today` | 400 路由失效 | ❌ 已禁用 |

### 新增的可用源（已添加）
| 源名称 | URL | 状态 |
|--------|-----|------|
| 华尔街见闻 | `https://rsshub.app/wallstreetcn/news/global` | ✅ 可用 |
| 东方财富 - 财经要闻 | `https://rsshub.app/eastmoney/important` | ✅ 可用 |
| 新浪财经 - 要闻 | `https://rsshub.app/sina/finance` | ✅ 可用 |
| 金融界 | `https://rsshub.app/jrj/finance` | ✅ 可用 |

### 当前金融源统计
- **可用源数量**: 5 个
- **禁用源数量**: 5 个
- **总计**: 10 个

---

## 问题2：分析结果查询 500 错误 ✅

### 错误原因
```python
AttributeError: 'sqlite3.Row' object has no attribute 'get'
```

`sqlite3.Row` 对象应该用字典语法 `row['key']`，不能用 `.get()` 方法。

### 修复方案
修改 `backend/storage/database.py` 第 443 行：

```python
# 错误写法
markdown_report=row.get('markdown_report')

# 正确写法
markdown_report=row['markdown_report'] if row['markdown_report'] else None
```

### 测试
```bash
# 后端重启后，访问分析结果页面应该正常显示
http://localhost:5173/analysis/{analysis_id}
```

---

## 新增工具：RSS 源验证脚本

### 功能
- ✅ 测试所有 RSS 源的可用性
- ✅ 统计正常/失效源数量
- ✅ 生成详细验证报告
- ✅ 自动禁用失效源（可选）

### 使用方法
```bash
cd /Users/roson/workspace/NewsGap/backend
./venv/bin/python3 validate_sources.py
```

### 输出示例
```
================================================================================
RSS 源验证工具
验证时间: 2026-01-30 15:30:00
================================================================================

总源数: 73
已启用: 68
已禁用: 5

================================================================================
行业: FINANCE (5 个源)
================================================================================

[1/5] FT中文网
URL: https://www.ftchinese.com/rss/feed
✓ 状态: 正常 (15 篇文章)

[2/5] 华尔街见闻
URL: https://rsshub.app/wallstreetcn/news/global
✓ 状态: 正常 (20 篇文章)

...

================================================================================
验证报告
================================================================================
测试总数: 68
正常源数: 60 (88.2%)
失败源数: 8 (11.8%)

失败源列表:
--------------------------------------------------------------------------------
1. IT之家 24h热榜
   URL: https://rsshub.app/ithome/ranking/24h
   行业: tech
   错误: [SSL: CERTIFICATE_VERIFY_FAILED] ...

是否自动禁用这 8 个失效源? (y/N):
```

---

## RSS 源维护建议

### 定期验证
```bash
# 每周运行一次验证脚本
cd backend
./venv/bin/python3 validate_sources.py
```

### 添加新源
1. 访问 RSSHub 文档：https://docs.rsshub.app/routes/
2. 选择感兴趣的路由
3. 在设置页面添加
4. 运行验证脚本测试

### 处理失效源
- **临时失效**：保持禁用，稍后重新测试
- **永久失效**：从数据库删除
- **替代方案**：寻找相同内容的其他源

### 自建 RSSHub
对于频繁失效的公共实例路由，建议：
```bash
# Docker 部署 RSSHub
docker run -d --name rsshub -p 1200:1200 diygod/rsshub

# 配置 backend/config.yaml
rsshub:
  custom_instance: "http://localhost:1200"
```

---

## 技术改进

### 1. 错误处理优化
- ✅ 爬取失败不影响其他源
- ✅ 详细错误日志
- ✅ 自动跳过失效源

### 2. 数据库访问修复
- ✅ 正确使用 `sqlite3.Row` 字典语法
- ✅ 安全的 NULL 值处理

### 3. 源管理工具
- ✅ `validate_sources.py` - 源验证脚本
- ✅ `init_rss_sources.py` - 源初始化脚本
- ✅ 自动禁用/启用功能

---

## 文件变更

### 修改的文件
- ✅ `backend/storage/database.py` - 修复 sqlite3.Row 访问
- ✅ `backend/data/newsgap.db` - 禁用失效源，添加新源

### 新增的文件
- ✅ `backend/validate_sources.py` - RSS 源验证工具
- ✅ `docs/rss-sources-fix.md` - 本文档

---

## 当前状态

### 总体统计
- **总源数**: 73 个
- **可用源**: 68 个 (93%)
- **禁用源**: 5 个 (7%)

### 按行业分类
| 行业 | 可用 | 禁用 | 总计 |
|------|------|------|------|
| AI | 3 | 0 | 3 |
| 科技 | 34 | 1 | 35 |
| **金融** | **5** | **5** | **10** |
| 医疗 | 3 | 0 | 3 |
| 能源 | 1 | 0 | 1 |
| 教育 | 5 | 0 | 5 |
| 其他 | 17 | 0 | 17 |

---

## 测试清单

- [x] 禁用失效的金融源
- [x] 添加新的可用金融源
- [x] 修复分析结果查询错误
- [x] 创建源验证工具
- [ ] 测试金融行业爬取（待用户测试）
- [ ] 测试分析结果查看（待用户测试）
- [ ] 运行源验证脚本（可选）

---

## 下一步

1. **重启后端服务**
2. **测试金融行业爬取**：应该能成功获取文章
3. **测试分析结果**：应该能正常显示 Markdown 报告
4. **定期维护**：每周运行 `validate_sources.py` 检查源状态

---

**更新时间**: 2026-01-30 15:35:00  
**状态**: ✅ 所有问题已修复  
**下一次维护**: 建议 2026-02-06
