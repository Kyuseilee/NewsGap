# 报告标题格式统一说明

## 需求

统一所有行业报告的标题格式为：**日期-行业-报告标题**

例如：
- `2026-02-04-财经金融-市场分析报告`
- `2026-02-04-科技互联网-行业动态`
- `2026-02-04-开发者-技术周报`

## 实现方案

### 1. 基础约束 (prompts/base.yaml)

在system_prompt_base中添加标题格式约束:

```yaml
## 4. 格式规范（重要）
- **标题格式**：报告标题必须使用"日期-行业-报告标题"格式
  例如"2026-02-04-财经金融-市场分析报告"或"2026-02-04-科技互联网-行业动态"
```

**优势**: 所有行业自动继承此约束

### 2. 通用辅助方法 (llm/adapter.py)

在BaseLLMAdapter中添加:

#### 行业名称映射
```python
INDUSTRY_NAME_MAP = {
    "socialmedia": "社交媒体",
    "news": "新闻资讯",
    "tech": "科技互联网",
    "developer": "开发者",
    "finance": "财经金融",
    "entertainment": "娱乐影视",
    "gaming": "游戏电竞",
    "anime": "动漫二次元",
    "shopping": "电商购物",
    "education": "学习教育",
    "lifestyle": "生活方式",
    "other": "其他",
    "custom": "自定义",
}
```

#### 标题格式生成方法
```python
def _get_report_title_format(self, industry: Optional[IndustryCategory] = None) -> str:
    """生成报告标题格式提示"""
    today = datetime.now().strftime("%Y-%m-%d")
    industry_cn = self.INDUSTRY_NAME_MAP.get(
        industry.value if industry else "other", 
        "综合"
    )
    return f"# {today}-{industry_cn}-[报告主题]"
```

**优势**: 
- 统一日期格式
- 自动映射行业中英文
- 所有adapter继承使用

### 3. 各Adapter使用 (所有*_adapter.py)

在每个adapter的`_build_markdown_prompt`方法中:

```python
# 使用基类方法生成标题格式
title_format = self._get_report_title_format(industry)

return f"""
⚠️ **输出要求**：
- 报告标题格式：{title_format}
- 直接输出 Markdown 格式，不要用代码块包裹
- 必须完整输出所有章节，确保包含结尾总结
"""
```

**已更新的adapter**:
- ✅ gemini_adapter.py
- ✅ openai_adapter.py
- ✅ deepseek_adapter.py
- ✅ ollama_adapter.py

## 测试结果

```
测试标题格式生成:
================================================================================
finance         → # 2026-02-04-财经金融-[报告主题]
tech            → # 2026-02-04-科技互联网-[报告主题]
news            → # 2026-02-04-新闻资讯-[报告主题]
developer       → # 2026-02-04-开发者-[报告主题]
None            → # 2026-02-04-其他-[报告主题]

检查行业映射完整性:
✓ 所有行业都已映射
```

## 标题示例

| 行业 | 标题示例 |
|------|----------|
| 财经金融 | `# 2026-02-04-财经金融-市场分析报告` |
| 科技互联网 | `# 2026-02-04-科技互联网-行业动态` |
| 开发者 | `# 2026-02-04-开发者-技术周报` |
| 新闻资讯 | `# 2026-02-04-新闻资讯-要闻简报` |
| 社交媒体 | `# 2026-02-04-社交媒体-热点追踪` |
| 娱乐影视 | `# 2026-02-04-娱乐影视-本周推荐` |
| 游戏电竞 | `# 2026-02-04-游戏电竞-新游速递` |
| 动漫二次元 | `# 2026-02-04-动漫二次元-新番导视` |
| 电商购物 | `# 2026-02-04-电商购物-好物精选` |
| 学习教育 | `# 2026-02-04-学习教育-课程推荐` |
| 生活方式 | `# 2026-02-04-生活方式-品质生活` |

## 架构优势

### 分层设计

```
base.yaml (系统约束)
    ↓ 继承
BaseLLMAdapter (通用方法)
    ↓ 继承
各个Adapter (具体实现)
```

### DRY原则

- ✅ 日期格式统一管理
- ✅ 行业映射统一维护
- ✅ 标题生成逻辑复用
- ✅ 所有LLM后端保持一致

### 易于维护

- 新增行业：只需在INDUSTRY_NAME_MAP中添加映射
- 修改格式：只需修改_get_report_title_format方法
- 自动生效：所有adapter自动使用新格式

## 修改文件清单

1. `backend/prompts/base.yaml` - 添加标题格式约束
2. `backend/llm/adapter.py` - 添加通用方法和映射
3. `backend/llm/gemini_adapter.py` - 使用标题格式
4. `backend/llm/openai_adapter.py` - 使用标题格式
5. `backend/llm/deepseek_adapter.py` - 使用标题格式
6. `backend/llm/ollama_adapter.py` - 使用标题格式

## 注意事项

1. **日期格式**: 固定为 `YYYY-MM-DD` (ISO 8601)
2. **行业名称**: 使用中文，保持简洁
3. **报告主题**: 由LLM根据内容自动生成
4. **分隔符**: 使用短横线 `-` 分隔各部分

## 后续扩展

如果需要支持更多标题格式变体:

1. 在BaseLLMAdapter中添加新方法，如`_get_custom_title_format()`
2. 在base.yaml中添加对应约束
3. 各adapter按需调用

示例:
```python
def _get_custom_title_format(self, category_id: str) -> str:
    """为自定义分类生成标题格式"""
    today = datetime.now().strftime("%Y-%m-%d")
    return f"# {today}-自定义-{category_id}-[报告主题]"
```
