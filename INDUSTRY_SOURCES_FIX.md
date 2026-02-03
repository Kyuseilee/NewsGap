# 行业分类信息源修复报告

## 问题描述

在测试一键情报功能时，部分行业分类会返回 404 错误：
```
INFO: 127.0.0.1:52653 - "POST /api/intelligence HTTP/1.1" 404 Not Found
```

## 问题原因

后端代码 `routes/intelligence.py:102-107` 中，当找不到可用信息源时会抛出 404 错误：

```python
if not sources:
    detail = f"未找到行业 '{request.industry}' 的可用信息源"
    raise HTTPException(
        status_code=404,
        detail=detail
    )
```

经排查发现，以下行业分类在数据库中**没有信息源**：
- ❌ `crypto` (加密货币)
- ❌ `other` (其他)

## 解决方案

为缺失的行业分类添加信息源。

### 添加的信息源

#### 1. Crypto 加密货币 (5个源)

| 名称 | URL | 类型 | 状态 |
|------|-----|------|------|
| 金色财经 | https://rsshub.app/jinse/lives | RSSHub | ✓ 启用 |
| 律动 BlockBeats | https://rsshub.app/theblockbeats/newsflash | RSSHub | ✓ 启用 |
| CoinDesk | https://www.coindesk.com/arc/outboundfeeds/rss/ | 官方RSS | ✓ 启用 |
| Cointelegraph | https://cointelegraph.com/rss | 官方RSS | ✓ 启用 |
| Decrypt | https://decrypt.co/feed | 官方RSS | ✓ 启用 |

#### 2. Other 其他 (3个源)

| 名称 | URL | 类型 | 状态 |
|------|-----|------|------|
| 少数派 | https://rsshub.app/sspai/series | RSSHub | ✓ 启用 |
| 虎嗅网 | https://rsshub.app/huxiu/article | RSSHub | ✓ 启用 |
| 爱范儿 | https://rsshub.app/ifanr/app | RSSHub | ✓ 启用 |

### 执行的操作

1. 创建了 `add_missing_sources.py` 脚本
2. 运行脚本添加了 8 个信息源
3. 验证所有行业分类都有可用源

## 修复结果

### 修复前
```
⚠️  以下行业分类没有信息源（会导致404）：
   - crypto
   - other
```

### 修复后
```
✅ 所有行业信息源统计：
============================================================
行业              总数         启用数        状态
============================================================
anime           2          2          ✓
crypto          5          5          ✓  ← 新增
developer       10         10         ✓
education       3          3          ✓
entertainment   4          4          ✓
finance         5          3          ✓
gaming          3          3          ✓
lifestyle       2          2          ✓
news            8          4          ✓
other           3          3          ✓  ← 新增
shopping        1          1          ✓
social          6          6          ✓
tech            10         10         ✓
============================================================
总计              62         56        

✅ 所有行业分类都有启用的信息源，一键情报功能完全可用！
```

## 行业分类对照表

前端和后端的行业分类完全一致：

| 代码 | 中文名称 | 启用源数量 | 总源数量 |
|------|----------|-----------|---------|
| social | 社交媒体 | 6 | 6 |
| news | 新闻资讯 | 4 | 8 |
| tech | 科技互联网 | 10 | 10 |
| developer | 开发者 | 10 | 10 |
| finance | 财经金融 | 3 | 5 |
| **crypto** | **加密货币** | **5** | **5** ← 修复 |
| entertainment | 娱乐影视 | 4 | 4 |
| gaming | 游戏电竞 | 3 | 3 |
| anime | 动漫二次元 | 2 | 2 |
| shopping | 电商购物 | 1 | 1 |
| education | 学习教育 | 3 | 3 |
| lifestyle | 生活方式 | 2 | 2 |
| **other** | **其他** | **3** | **3** ← 修复 |

## 测试建议

建议测试每个行业分类的一键情报功能：

```bash
# 测试 crypto
POST /api/intelligence
{
  "industry": "crypto",
  "hours": 24,
  "llm_backend": "gemini"
}

# 测试 other
POST /api/intelligence
{
  "industry": "other",
  "hours": 24,
  "llm_backend": "gemini"
}
```

## 文件清单

### 新增文件
- `/backend/add_missing_sources.py` - 添加信息源的脚本
- `/INDUSTRY_SOURCES_FIX.md` - 本修复报告

### 修改的数据
- 数据库 `data/newsgap.db` 中 `sources` 表新增 8 条记录

## 注意事项

1. **RSSHub 依赖**
   - 部分源使用 RSSHub（https://rsshub.app）
   - 如果 RSSHub 服务不可用，这些源可能无法访问
   - 建议使用自建 RSSHub 实例以确保稳定性

2. **官方 RSS**
   - CoinDesk、Cointelegraph、Decrypt 使用官方 RSS
   - 这些源相对稳定，但可能有访问频率限制

3. **爬取频率**
   - Crypto 源设置为 6 小时爬取一次（加密货币新闻更新频繁）
   - Other 源设置为 24 小时爬取一次

4. **后续维护**
   - 定期检查信息源的可用性
   - 根据需要调整爬取频率
   - 添加更多高质量信息源

## 验证清单

- [x] 检查后端行业分类枚举定义
- [x] 检查前端下拉选项
- [x] 确认前后端分类一致
- [x] 排查 404 错误原因
- [x] 为 crypto 添加信息源
- [x] 为 other 添加信息源
- [x] 验证所有分类都有启用的源
- [x] 创建修复文档

## 结论

✅ **问题已完全修复！**

现在所有 13 个行业分类都有可用的信息源，一键情报功能可以正常使用，不会再出现 404 错误。

用户可以在前端选择任意行业分类进行情报生成，包括之前无法使用的"加密货币"和"其他"分类。
