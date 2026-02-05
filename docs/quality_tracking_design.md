# NewsGap 分析质量跟踪系统 - 设计方案

> 设计时间：2026-02-05  
> 状态：设计阶段，待实现

## 📊 系统概述

分析质量跟踪系统的核心目标是：
1. **量化评估**：用数据衡量AI分析报告的质量
2. **持续优化**：通过A/B测试和反馈循环改进Prompt
3. **性能监控**：追踪LLM性能、成本和用户满意度

---

## 🏗️ 架构设计

### 核心组件

```
┌─────────────────────────────────────────────────────────────┐
│                    质量跟踪系统架构                           │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   质量评分    │    │   A/B测试     │    │  性能分析    │  │
│  │   模块        │    │   框架        │    │  仪表板      │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                    │                    │          │
│         └────────────────────┴────────────────────┘          │
│                             │                                │
│                    ┌────────▼────────┐                       │
│                    │   数据存储层     │                       │
│                    │  (quality_metrics)│                     │
│                    └─────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 📐 数据库设计

### 1. 质量评分表 `quality_metrics`

```sql
CREATE TABLE quality_metrics (
    id TEXT PRIMARY KEY,
    analysis_id TEXT NOT NULL,
    
    -- 自动评分指标
    completeness_score REAL,          -- 完整性评分 (0-100)
    structure_score REAL,             -- 结构性评分 (0-100)
    insight_density REAL,             -- 洞察密度 (insights/1000 words)
    readability_score REAL,           -- 可读性评分 (Flesch)
    keyword_coverage REAL,            -- 关键词覆盖率 (0-100)
    overall_quality_score REAL,       -- 综合质量分 (0-100)
    
    -- 用户反馈
    user_rating INTEGER,              -- 用户评分 (1-5星)
    user_feedback TEXT,               -- 用户文字反馈
    user_helpful_vote BOOLEAN,        -- 是否有帮助
    
    -- 技术指标
    llm_backend TEXT,                 -- 使用的LLM
    llm_model TEXT,                   -- 具体模型
    prompt_version TEXT,              -- Prompt版本
    processing_time REAL,             -- 处理时间
    token_usage INTEGER,              -- Token使用量
    estimated_cost REAL,              -- 成本
    
    -- A/B测试
    experiment_id TEXT,               -- 实验ID
    variant TEXT,                     -- 变体 (A/B/C)
    
    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (analysis_id) REFERENCES analyses(id)
);

CREATE INDEX idx_quality_experiment ON quality_metrics(experiment_id);
CREATE INDEX idx_quality_rating ON quality_metrics(user_rating);
CREATE INDEX idx_quality_model ON quality_metrics(llm_backend, llm_model);
CREATE INDEX idx_quality_score ON quality_metrics(overall_quality_score);
```

### 2. Prompt版本表 `prompt_versions`

```sql
CREATE TABLE prompt_versions (
    id TEXT PRIMARY KEY,
    industry TEXT NOT NULL,           -- 行业分类
    analysis_type TEXT NOT NULL,      -- 分析类型
    version TEXT NOT NULL,            -- 版本号 (v1.0, v1.1)
    prompt_template TEXT NOT NULL,    -- Prompt模板内容
    
    -- 性能统计
    usage_count INTEGER DEFAULT 0,    -- 使用次数
    avg_quality_score REAL,           -- 平均质量分
    avg_user_rating REAL,             -- 平均用户评分
    
    -- 版本控制
    is_active BOOLEAN DEFAULT FALSE,  -- 是否为当前版本
    parent_version TEXT,              -- 父版本ID
    change_description TEXT,          -- 变更说明
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,                  -- 创建者
    
    UNIQUE(industry, analysis_type, version)
);

CREATE INDEX idx_prompt_active ON prompt_versions(industry, analysis_type, is_active);
```

### 3. A/B测试实验表 `experiments`

```sql
CREATE TABLE experiments (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    
    -- 实验配置
    industry TEXT NOT NULL,
    analysis_type TEXT NOT NULL,
    variant_a_prompt_id TEXT,         -- 变体A的Prompt ID
    variant_b_prompt_id TEXT,         -- 变体B的Prompt ID
    traffic_split REAL DEFAULT 0.5,   -- 流量分配比例 (0.0-1.0)
    
    -- 实验状态
    status TEXT DEFAULT 'draft',      -- draft/running/completed/cancelled
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    
    -- 统计数据
    variant_a_count INTEGER DEFAULT 0,
    variant_b_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (variant_a_prompt_id) REFERENCES prompt_versions(id),
    FOREIGN KEY (variant_b_prompt_id) REFERENCES prompt_versions(id)
);

CREATE INDEX idx_experiment_status ON experiments(status);
CREATE INDEX idx_experiment_industry ON experiments(industry, analysis_type);
```

---

## 🎯 质量评分算法

### 1. 自动评分维度

#### A. 完整性评分 (Completeness Score)

检查报告是否包含必需的章节：

```python
def calculate_completeness_score(markdown_report: str, analysis_type: str) -> float:
    """
    计算报告完整性
    
    检查必需章节是否存在
    
    Args:
        markdown_report: Markdown格式的报告内容
        analysis_type: 分析类型 (comprehensive, trend, signal, gap, brief)
        
    Returns:
        完整性评分 (0-100)
    """
    required_sections = {
        'comprehensive': [
            '## 一、核心洞察',
            '## 二、趋势分析',
            '## 三、执行建议',
            '## 四、风险提示'
        ],
        'trend': [
            '## 趋势概述',
            '## 关键指标',
            '## 趋势预测'
        ],
        'signal': [
            '## 信号聚类',
            '## 关键事件',
            '## 信号强度'
        ],
        'gap': [
            '## 信息差识别',
            '## 机会分析'
        ],
        'brief': [
            '## 执行摘要'
        ]
    }
    
    sections = required_sections.get(analysis_type, [])
    if not sections:
        return 100  # 未知类型，默认满分
    
    found_sections = sum(1 for section in sections if section in markdown_report)
    
    return (found_sections / len(sections)) * 100
```

#### B. 结构性评分 (Structure Score)

评估Markdown结构的规范性：

```python
def calculate_structure_score(markdown_report: str) -> float:
    """
    评估报告结构质量
    
    检查：
    - 标题层级是否合理 (H1/H2/H3)
    - 是否有列表项
    - 段落长度是否适中
    - 是否有代码块或引用
    
    Returns:
        结构性评分 (0-100)
    """
    lines = markdown_report.split('\n')
    
    # 统计各级标题
    h1_count = sum(1 for line in lines if line.startswith('# '))
    h2_count = sum(1 for line in lines if line.startswith('## '))
    h3_count = sum(1 for line in lines if line.startswith('### '))
    
    # 统计列表
    list_count = sum(1 for line in lines if line.strip().startswith(('-', '*', '1.')))
    
    # 统计引用
    quote_count = sum(1 for line in lines if line.strip().startswith('>'))
    
    # 段落统计
    paragraphs = [p for p in markdown_report.split('\n\n') if p.strip() and not p.startswith('#')]
    avg_paragraph_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0
    
    # 评分逻辑
    score = 0
    
    # 1. 标题结构合理 (40分)
    # H1不超过1个，有足够的H2和H3
    if h1_count <= 1 and h2_count >= 3 and h3_count >= 2:
        score += 40
    elif h2_count >= 2:
        score += 20
    
    # 2. 有列表项 (30分)
    if list_count >= 10:
        score += 30
    elif list_count >= 5:
        score += 20
    elif list_count >= 2:
        score += 10
    
    # 3. 段落长度适中 (20分)
    # 理想范围：50-150词
    if 50 <= avg_paragraph_length <= 150:
        score += 20
    elif 30 <= avg_paragraph_length <= 200:
        score += 10
    
    # 4. 有引用或强调 (10分)
    if quote_count >= 2:
        score += 10
    elif quote_count >= 1:
        score += 5
    
    return min(score, 100)
```

#### C. 洞察密度 (Insight Density)

衡量报告中实质性洞察的密度：

```python
def calculate_insight_density(markdown_report: str) -> float:
    """
    计算洞察密度：每1000词中的洞察数量
    
    洞察识别特征：
    - 包含关键动词：表明、显示、揭示、发现、趋势、信号
    - 使用数据/数字支撑
    - 提供建议或判断
    - 因果关系表述
    
    Returns:
        洞察密度 (每1000词的洞察数)
    """
    import re
    
    # 洞察关键词模式
    insight_patterns = [
        r'(表明|显示|揭示|发现|趋势|信号|建议|应当|需要|可能|预计)',
        r'\d+%',                           # 百分比
        r'\d+倍',                          # 倍数
        r'(上升|下降|增长|减少|提升)\s*\d+', # 变化数据
        r'(因为|由于|导致|引发|促使)',       # 因果关系
        r'(但是|然而|不过|尽管)',           # 转折对比
        r'(第一|首先|其次|最后|总之)',       # 结构化表述
    ]
    
    insight_count = 0
    for pattern in insight_patterns:
        matches = re.findall(pattern, markdown_report)
        insight_count += len(matches)
    
    # 计算词数 (中文按字符数，英文按单词数)
    # 简化：按字符数计算
    char_count = len(re.sub(r'\s+', '', markdown_report))
    word_count = char_count  # 中文1字=1词
    
    # 每1000词的洞察数
    density = (insight_count / word_count) * 1000 if word_count > 0 else 0
    
    return density
```

#### D. 可读性评分 (Readability Score)

使用简化的中文可读性评分：

```python
def calculate_readability_score(markdown_report: str) -> float:
    """
    简化的中文可读性评分
    
    基于：
    - 平均句子长度
    - 标点符号使用频率
    - 段落结构
    
    Returns:
        可读性评分 (0-100)，分数越高越易读
    """
    import re
    
    # 移除Markdown标记
    text = re.sub(r'[#*`\[\]\(\)]', '', markdown_report)
    
    # 统计句子
    sentences = re.split(r'[。！？\n]', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 5]
    
    if not sentences:
        return 50
    
    # 1. 平均句子长度 (字符数)
    avg_sentence_length = sum(len(s) for s in sentences) / len(sentences)
    
    # 理想句长：20-40字
    if 20 <= avg_sentence_length <= 40:
        length_score = 100
    elif avg_sentence_length < 20:
        length_score = 70 + (avg_sentence_length / 20) * 30
    elif avg_sentence_length <= 60:
        length_score = 100 - (avg_sentence_length - 40) * 1.5
    else:
        length_score = max(0, 100 - (avg_sentence_length - 40) * 2)
    
    # 2. 标点符号使用 (逗号、分号帮助断句)
    punctuation_count = len(re.findall(r'[，,；;、]', text))
    punctuation_ratio = punctuation_count / len(sentences) if sentences else 0
    
    # 理想：每句1-3个断句标点
    if 1 <= punctuation_ratio <= 3:
        punctuation_score = 100
    else:
        punctuation_score = max(0, 100 - abs(punctuation_ratio - 2) * 20)
    
    # 综合评分 (句长权重70%，标点权重30%)
    score = length_score * 0.7 + punctuation_score * 0.3
    
    return round(score, 2)
```

#### E. 关键词覆盖率 (Keyword Coverage)

检查报告是否覆盖了文章中的关键主题：

```python
def calculate_keyword_coverage(markdown_report: str, articles: List[Article]) -> float:
    """
    计算报告对文章关键词的覆盖率
    
    提取文章标题中的关键词，检查报告中的覆盖情况
    
    Args:
        markdown_report: 报告内容
        articles: 源文章列表
        
    Returns:
        关键词覆盖率 (0-100)
    """
    import jieba
    from collections import Counter
    
    # 提取文章关键词 (来自标题)
    article_keywords = []
    for article in articles:
        # 分词
        words = jieba.cut(article.title)
        # 过滤停用词和短词
        article_keywords.extend([w for w in words if len(w) > 1])
    
    # 统计高频关键词
    keyword_freq = Counter(article_keywords)
    top_keywords = [k for k, v in keyword_freq.most_common(20)]
    
    if not top_keywords:
        return 100  # 没有关键词，默认满分
    
    # 检查报告覆盖情况
    covered_keywords = sum(1 for kw in top_keywords if kw in markdown_report)
    
    coverage = (covered_keywords / len(top_keywords)) * 100
    
    return coverage
```

### 2. 综合质量分计算

```python
def calculate_overall_quality_score(metrics: dict) -> float:
    """
    计算综合质量分
    
    加权平均：
    - 完整性: 25%
    - 结构性: 20%
    - 洞察密度: 25%
    - 可读性: 15%
    - 关键词覆盖: 15%
    
    Args:
        metrics: 包含各项指标的字典
        
    Returns:
        综合质量分 (0-100)
    """
    weights = {
        'completeness': 0.25,
        'structure': 0.20,
        'insight_density_normalized': 0.25,
        'readability': 0.15,
        'keyword_coverage': 0.15
    }
    
    # 归一化洞察密度到0-100范围
    # 假设理想值为 5-15 insights/1000 words
    density = metrics.get('insight_density', 0)
    if density <= 5:
        normalized_density = (density / 5) * 70  # 5以下线性映射到0-70
    elif density <= 15:
        normalized_density = 70 + (density - 5) / 10 * 30  # 5-15映射到70-100
    else:
        normalized_density = 100  # 15以上都是100
    
    metrics['insight_density_normalized'] = normalized_density
    
    # 加权求和
    overall_score = sum(
        metrics.get(metric, 0) * weight
        for metric, weight in weights.items()
    )
    
    return round(overall_score, 2)
```

---

## 🔬 A/B测试框架

### 工作流程

```
1. 创建实验
   ├─ 定义实验名称和目标
   ├─ 选择要测试的两个Prompt版本
   ├─ 设置流量分配比例 (默认50/50)
   └─ 设置实验时长和最小样本量

2. 运行实验
   ├─ 用户触发分析请求
   ├─ 系统随机分配变体 (A或B)
   ├─ 使用对应Prompt生成分析
   ├─ 记录实验数据 (变体、质量分、用户反馈)
   └─ 更新实验统计

3. 收集数据
   ├─ 自动质量评分 (5个维度)
   ├─ 用户反馈评分 (可选)
   ├─ 性能指标 (时间、成本、Token)
   └─ 达到最小样本量后可分析

4. 分析结果
   ├─ 计算各变体的平均质量分
   ├─ 统计显著性检验 (t-test)
   ├─ 计算提升幅度 (lift)
   └─ 生成实验报告

5. 决策
   ├─ 确定获胜变体
   ├─ 停止实验
   ├─ 更新生产Prompt
   └─ 归档实验结果
```

### 实现示例

```python
class ABTestManager:
    """A/B测试管理器"""
    
    def __init__(self, db: Database):
        self.db = db
    
    async def assign_variant(
        self, 
        user_id: str, 
        experiment_id: str
    ) -> str:
        """
        为用户分配实验变体
        
        使用一致性哈希确保同一用户总是看到相同变体
        
        Args:
            user_id: 用户ID (可以是session ID)
            experiment_id: 实验ID
            
        Returns:
            'A' 或 'B' 或 'control'
        """
        import hashlib
        
        # 获取实验配置
        experiment = await self.db.get_experiment(experiment_id)
        
        if not experiment or experiment.status != 'running':
            return 'control'  # 实验未运行，使用默认Prompt
        
        # 一致性哈希分配
        hash_input = f"{user_id}:{experiment_id}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
        
        # 根据traffic_split决定分配
        threshold = experiment.traffic_split
        normalized_hash = (hash_value % 100) / 100
        
        variant = 'A' if normalized_hash < threshold else 'B'
        
        return variant
    
    async def get_prompt_for_variant(
        self,
        experiment_id: str,
        variant: str
    ) -> str:
        """
        获取实验变体对应的Prompt
        
        Args:
            experiment_id: 实验ID
            variant: 'A' 或 'B'
            
        Returns:
            Prompt模板内容
        """
        experiment = await self.db.get_experiment(experiment_id)
        
        if variant == 'A':
            prompt_version = await self.db.get_prompt_version(experiment.variant_a_prompt_id)
        else:
            prompt_version = await self.db.get_prompt_version(experiment.variant_b_prompt_id)
        
        return prompt_version.prompt_template if prompt_version else None
    
    async def record_result(
        self,
        experiment_id: str,
        variant: str,
        analysis_id: str,
        quality_metrics: dict
    ):
        """
        记录实验结果
        
        Args:
            experiment_id: 实验ID
            variant: 'A' 或 'B'
            analysis_id: 分析ID
            quality_metrics: 质量指标字典
        """
        # 保存到quality_metrics表
        await self.db.save_quality_metrics({
            'analysis_id': analysis_id,
            'experiment_id': experiment_id,
            'variant': variant,
            **quality_metrics
        })
        
        # 更新实验计数
        experiment = await self.db.get_experiment(experiment_id)
        if variant == 'A':
            experiment.variant_a_count += 1
        else:
            experiment.variant_b_count += 1
        
        await self.db.update_experiment(experiment)
    
    async def analyze_experiment(
        self,
        experiment_id: str
    ) -> dict:
        """
        分析实验结果
        
        返回统计摘要和显著性检验结果
        
        Args:
            experiment_id: 实验ID
            
        Returns:
            实验分析结果字典
        """
        # 获取实验数据
        results = await self.db.get_quality_metrics_by_experiment(experiment_id)
        
        variant_a = [r for r in results if r['variant'] == 'A']
        variant_b = [r for r in results if r['variant'] == 'B']
        
        if len(variant_a) < 10 or len(variant_b) < 10:
            return {
                'error': '样本量不足',
                'min_samples': 10,
                'variant_a_samples': len(variant_a),
                'variant_b_samples': len(variant_b)
            }
        
        # 计算平均质量分
        avg_quality_a = sum(r['overall_quality_score'] for r in variant_a) / len(variant_a)
        avg_quality_b = sum(r['overall_quality_score'] for r in variant_b) / len(variant_b)
        
        # 计算平均用户评分 (如果有)
        rated_a = [r for r in variant_a if r.get('user_rating')]
        rated_b = [r for r in variant_b if r.get('user_rating')]
        
        avg_rating_a = sum(r['user_rating'] for r in rated_a) / len(rated_a) if rated_a else None
        avg_rating_b = sum(r['user_rating'] for r in rated_b) / len(rated_b) if rated_b else None
        
        # 计算平均成本
        avg_cost_a = sum(r['estimated_cost'] for r in variant_a) / len(variant_a)
        avg_cost_b = sum(r['estimated_cost'] for r in variant_b) / len(variant_b)
        
        # T检验 (显著性检验)
        from scipy import stats
        quality_a = [r['overall_quality_score'] for r in variant_a]
        quality_b = [r['overall_quality_score'] for r in variant_b]
        t_stat, p_value = stats.ttest_ind(quality_a, quality_b)
        
        is_significant = p_value < 0.05
        winner = 'A' if avg_quality_a > avg_quality_b else 'B'
        lift_percent = ((max(avg_quality_a, avg_quality_b) / min(avg_quality_a, avg_quality_b)) - 1) * 100
        
        return {
            'experiment_id': experiment_id,
            'sample_size_a': len(variant_a),
            'sample_size_b': len(variant_b),
            'avg_quality_a': round(avg_quality_a, 2),
            'avg_quality_b': round(avg_quality_b, 2),
            'avg_rating_a': round(avg_rating_a, 2) if avg_rating_a else None,
            'avg_rating_b': round(avg_rating_b, 2) if avg_rating_b else None,
            'avg_cost_a': round(avg_cost_a, 4),
            'avg_cost_b': round(avg_cost_b, 4),
            't_statistic': round(t_stat, 4),
            'p_value': round(p_value, 4),
            'is_significant': is_significant,
            'winner': winner if is_significant else None,
            'lift_percent': round(lift_percent, 2),
            'confidence_level': '95%' if is_significant else '<95%',
            'recommendation': self._generate_recommendation(
                winner, is_significant, lift_percent, avg_cost_a, avg_cost_b
            )
        }
    
    def _generate_recommendation(
        self,
        winner: str,
        is_significant: bool,
        lift_percent: float,
        cost_a: float,
        cost_b: float
    ) -> str:
        """生成实验建议"""
        if not is_significant:
            return "实验结果无显著差异，建议继续收集数据或尝试更大的改动"
        
        cost_diff_percent = abs(cost_a - cost_b) / min(cost_a, cost_b) * 100
        
        if lift_percent > 10 and cost_diff_percent < 20:
            return f"变体{winner}明显优于另一变体（提升{lift_percent:.1f}%），且成本相近，建议采用"
        elif lift_percent > 5 and cost_diff_percent < 10:
            return f"变体{winner}表现更好（提升{lift_percent:.1f}%），建议采用"
        elif lift_percent < 3:
            return "虽然有统计显著性，但提升幅度较小，可考虑其他优化方向"
        else:
            return f"变体{winner}更优（提升{lift_percent:.1f}%），但需权衡成本差异"
```

---

## 📈 性能分析仪表板

### 关键指标可视化

#### 1. 质量趋势图

```python
# API端点：GET /api/analytics/quality-trend
{
    "params": {
        "time_range": "last_30_days",
        "group_by": "llm_backend"  # 或 "industry", "analysis_type"
    },
    "response": {
        "data": [
            {
                "date": "2026-01-06",
                "gemini": 85.3,
                "deepseek": 82.1,
                "openai": 87.6
            },
            ...
        ]
    }
}
```

**可视化**：折线图
- X轴：日期
- Y轴：平均质量分 (0-100)
- 多条线：不同LLM后端

#### 2. 成本效率矩阵

```python
# API端点：GET /api/analytics/cost-efficiency
{
    "response": {
        "models": [
            {
                "name": "Gemini 2.5 Flash",
                "avg_quality": 85.3,
                "avg_cost": 0.023,
                "usage_count": 523
            },
            {
                "name": "DeepSeek Chat",
                "avg_quality": 82.1,
                "avg_cost": 0.008,
                "usage_count": 234
            },
            ...
        ]
    }
}
```

**可视化**：散点图/气泡图
- X轴：成本 ($/分析)
- Y轴：质量分
- 气泡大小：使用次数
- 理想位置：右上角（高质量、低成本）

#### 3. 用户满意度热力图

```python
# API端点：GET /api/analytics/satisfaction-heatmap
{
    "response": {
        "data": [
            ["tech", "comprehensive", 4.6],
            ["tech", "trend", 4.2],
            ["finance", "comprehensive", 4.8],
            ...
        ],
        "industries": ["tech", "finance", "developer", ...],
        "analysis_types": ["comprehensive", "trend", "signal", ...]
    }
}
```

**可视化**：热力图
- X轴：行业
- Y轴：分析类型
- 颜色：平均用户评分 (1-5星)

#### 4. Prompt版本对比表

```markdown
| 版本  | 行业     | 使用次数 | 平均质量分 | 平均评分 | 平均成本 | 胜率  | 状态   |
|-------|---------|---------|-----------|---------|---------|-------|--------|
| v1.3  | tech    | 523     | 87.3      | 4.6     | $0.023  | 68%   | 活跃   |
| v1.2  | tech    | 892     | 82.1      | 4.2     | $0.019  | 52%   | 废弃   |
| v2.1  | finance | 234     | 91.2      | 4.8     | $0.031  | 75%   | 活跃   |
| v2.0  | finance | 567     | 88.5      | 4.5     | $0.028  | 63%   | 废弃   |
```

**胜率**：在A/B测试中获胜的比例

---

## 🛠️ 实现计划

### Phase 1: 基础设施 (预计1-2周)

**目标**：建立质量评分的基础能力

- [ ] 创建数据库表
  - [ ] `quality_metrics` 表
  - [ ] `prompt_versions` 表
  - [ ] `experiments` 表
  - [ ] 添加索引

- [ ] 实现质量评分算法
  - [ ] 完整性评分
  - [ ] 结构性评分
  - [ ] 洞察密度计算
  - [ ] 可读性评分
  - [ ] 关键词覆盖
  - [ ] 综合质量分计算

- [ ] 集成到分析流程
  - [ ] 在 `analyzer.py` 中调用质量评分
  - [ ] 保存质量指标到数据库
  - [ ] 在分析详情页展示质量分

- [ ] 添加API端点
  - [ ] `GET /api/analytics/quality-metrics/{analysis_id}`
  - [ ] `GET /api/analytics/quality-summary`

### Phase 2: 用户反馈 (预计1周)

**目标**：收集用户对分析质量的反馈

- [ ] 前端UI
  - [ ] 分析详情页添加星级评分组件
  - [ ] 添加反馈文本框（可选）
  - [ ] "有帮助/无帮助"按钮

- [ ] 后端API
  - [ ] `POST /api/analyses/{id}/feedback` - 提交反馈
  - [ ] `GET /api/analyses/{id}/feedback` - 获取反馈

- [ ] 数据关联
  - [ ] 将用户反馈更新到 `quality_metrics` 表
  - [ ] 计算平均用户评分

### Phase 3: Prompt版本管理 (预计3-5天)

**目标**：管理和追踪Prompt的不同版本

- [ ] Prompt版本CRUD
  - [ ] `POST /api/prompts/versions` - 创建新版本
  - [ ] `GET /api/prompts/versions` - 列出所有版本
  - [ ] `PUT /api/prompts/versions/{id}/activate` - 激活版本
  - [ ] `GET /api/prompts/versions/{id}/stats` - 版本统计

- [ ] 版本控制逻辑
  - [ ] 从现有Prompt文件导入初始版本
  - [ ] 支持基于父版本创建新版本
  - [ ] 记录变更说明

### Phase 4: A/B测试框架 (预计1-2周)

**目标**：支持Prompt的A/B测试

- [ ] 实验管理API
  - [ ] `POST /api/experiments` - 创建实验
  - [ ] `GET /api/experiments` - 列出实验
  - [ ] `PUT /api/experiments/{id}/start` - 启动实验
  - [ ] `PUT /api/experiments/{id}/stop` - 停止实验
  - [ ] `GET /api/experiments/{id}/results` - 查看结果

- [ ] 核心逻辑
  - [ ] 实现 `ABTestManager` 类
  - [ ] 变体分配算法（一致性哈希）
  - [ ] 实验结果记录
  - [ ] 统计分析（t-test）

- [ ] 集成到分析流程
  - [ ] 在生成分析前检查是否有运行中的实验
  - [ ] 根据实验配置选择Prompt
  - [ ] 记录实验数据

### Phase 5: 分析仪表板 (预计1-2周)

**目标**：可视化展示质量数据和实验结果

- [ ] 后端API
  - [ ] `GET /api/analytics/quality-trend`
  - [ ] `GET /api/analytics/cost-efficiency`
  - [ ] `GET /api/analytics/satisfaction-heatmap`
  - [ ] `GET /api/analytics/prompt-comparison`

- [ ] 前端页面
  - [ ] 创建 `Analytics.tsx` 页面
  - [ ] 质量趋势图（使用 Chart.js 或 Recharts）
  - [ ] 成本效率散点图
  - [ ] 用户满意度热力图
  - [ ] Prompt版本对比表

- [ ] 交互功能
  - [ ] 时间范围筛选
  - [ ] 按LLM/行业/类型筛选
  - [ ] 数据导出（CSV/Excel）

### Phase 6: 自动化优化 (可选，预计1周)

**目标**：基于质量数据自动触发优化

- [ ] 告警机制
  - [ ] 质量分低于阈值时发送通知
  - [ ] 用户评分持续下降时告警

- [ ] 自动实验触发
  - [ ] 检测到质量下降时自动启动A/B测试
  - [ ] 测试新的Prompt变体

- [ ] 推荐系统
  - [ ] 为每个行业推荐最佳Prompt
  - [ ] 为每个用户推荐最佳LLM后端

---

## 💡 使用场景示例

### 场景1：自动监控Prompt性能

```python
# 在analyzer.py中集成质量评分
async def analyze(self, articles, analysis_type, ...):
    # 生成分析
    analysis = await self._generate_analysis(...)
    
    # 计算质量分
    quality_evaluator = QualityEvaluator()
    quality_metrics = quality_evaluator.evaluate(
        markdown_report=analysis.markdown_report,
        analysis_type=analysis_type,
        articles=articles,
        llm_backend=self.llm_backend,
        llm_model=self.model,
        processing_time=analysis.processing_time_seconds,
        token_usage=analysis.token_usage,
        estimated_cost=analysis.estimated_cost
    )
    
    # 保存质量指标
    await self.db.save_quality_metrics(analysis.id, quality_metrics)
    
    # 如果质量分低于阈值，触发告警
    if quality_metrics['overall_quality_score'] < 70:
        await self._send_low_quality_alert(analysis.id, quality_metrics)
    
    return analysis
```

### 场景2：优化特定行业的Prompt

```python
# 管理员创建A/B测试
experiment = await ab_test_manager.create_experiment(
    name="Developer行业Prompt v2.0测试",
    description="测试增强代码示例和技术深度的新版Prompt",
    industry="developer",
    analysis_type="comprehensive",
    variant_a_prompt_id="developer_v1_comprehensive",  # 当前版本
    variant_b_prompt_id="developer_v2_comprehensive",  # 新版本
    traffic_split=0.5,  # 50/50流量分配
    min_samples_per_variant=30  # 每个变体至少30个样本
)

# 启动实验
await ab_test_manager.start_experiment(experiment.id)

# 2周后，检查结果
results = await ab_test_manager.analyze_experiment(experiment.id)

# 输出示例：
# {
#     "sample_size_a": 45,
#     "sample_size_b": 47,
#     "avg_quality_a": 82.3,
#     "avg_quality_b": 89.7,
#     "p_value": 0.003,
#     "is_significant": True,
#     "winner": "B",
#     "lift_percent": 9.0,
#     "recommendation": "变体B明显优于另一变体（提升9.0%），建议采用"
# }

# 应用获胜版本
if results['is_significant'] and results['winner'] == 'B':
    await prompt_manager.activate_version("developer_v2_comprehensive")
    await ab_test_manager.stop_experiment(experiment.id, reason="Winner applied")
```

### 场景3：用户反馈驱动改进

```python
# 1. 收集用户反馈
# 用户在前端给分析打2星，评论："建议太笼统，没有具体案例"

# 2. 系统分析低分反馈
low_rated = await db.get_analyses_with_rating(max_rating=3, limit=100)

# 3. 提取共性问题
feedback_analysis = analyze_feedback_patterns(low_rated)
# 结果：
# {
#     "common_complaints": [
#         {"keyword": "建议", "count": 45, "sentiment": "negative"},
#         {"keyword": "案例", "count": 38, "sentiment": "negative"},
#         {"keyword": "具体", "count": 32, "sentiment": "negative"}
#     ],
#     "affected_industries": ["tech", "developer"],
#     "affected_analysis_types": ["comprehensive"]
# }

# 4. 调整Prompt
new_prompt = enhance_prompt(
    base_prompt="prompts/tech_comprehensive_v1.yaml",
    improvements=[
        "在执行建议部分增加具体案例",
        "每条建议提供可操作的步骤",
        "引用源文章中的数据支撑建议"
    ]
)

# 5. 创建A/B测试验证改进
experiment = await ab_test_manager.create_experiment(
    name="Tech综合分析：增强建议具体性",
    industry="tech",
    analysis_type="comprehensive",
    variant_a_prompt_id="tech_v1",
    variant_b_prompt_id=new_prompt.id
)

# 6. 等待结果并应用
```

### 场景4：多模型性能对比

```python
# 定期生成性能报告
report = await analytics.generate_model_comparison_report(
    time_range="last_30_days"
)

# 输出示例：
# {
#     "models": [
#         {
#             "name": "Gemini 2.5 Flash",
#             "avg_quality": 85.3,
#             "avg_cost": 0.023,
#             "avg_time": 12.5,
#             "usage_count": 523,
#             "user_rating": 4.6,
#             "strengths": ["快速", "成本适中"],
#             "weaknesses": ["深度分析略弱"]
#         },
#         {
#             "name": "DeepSeek Chat",
#             "avg_quality": 82.1,
#             "avg_cost": 0.008,
#             "avg_time": 18.3,
#             "usage_count": 234,
#             "user_rating": 4.2,
#             "strengths": ["成本极低"],
#             "weaknesses": ["速度较慢", "质量略低"]
#         },
#         {
#             "name": "GPT-4o",
#             "avg_quality": 91.2,
#             "avg_cost": 0.087,
#             "avg_time": 15.2,
#             "usage_count": 89,
#             "user_rating": 4.9,
#             "strengths": ["质量最高", "深度分析强"],
#             "weaknesses": ["成本高"]
#         }
#     ],
#     "recommendation": "日常分析使用Gemini 2.5，重要分析使用GPT-4o"
# }
```

---

## 📊 预期收益

### 1. 质量提升

- **基线**：当前平均质量分 ~75-80（估计）
- **目标**：通过持续优化提升至 85-90
- **提升幅度**：15-25%
- **实现路径**：
  - 第1个月：识别低分模式，修复明显问题 → +5分
  - 第2-3个月：A/B测试优化Prompt → +5分
  - 第4-6个月：基于用户反馈精细调优 → +5分

### 2. 成本优化

- **现状**：每次分析平均成本 $0.02-0.03
- **优化方向**：
  - 识别"性价比最优"模型配置
  - 在保证质量的前提下选择更便宜的模型
  - 避免过度使用昂贵模型
- **预期节省**：10-20%的成本（约$0.002-0.006/次）
- **年度影响**：如果每月1000次分析，年节省 $240-720

### 3. 用户满意度

- **基线**：当前用户评分未知（需要先实现反馈功能）
- **目标**：平均4.5星以上（满分5星）
- **提升策略**：
  - 快速响应低分反馈
  - 针对性优化问题最多的行业/类型
  - 持续迭代Prompt

### 4. 可追溯性和可解释性

- **当前问题**：分析质量好坏无法量化，问题难以定位
- **改进后**：
  - 每个分析都有质量分和分项得分
  - 可追溯到使用的Prompt版本和LLM
  - 可对比不同配置的效果
  - 便于向用户解释分析质量

### 5. 开发效率

- **当前**：Prompt优化靠主观判断，缺乏数据支撑
- **改进后**：
  - A/B测试提供客观数据
  - 快速验证Prompt改动效果
  - 避免"改进"实际上变差
  - 积累最佳实践

---

## 🔐 隐私和伦理考虑

### 1. 用户隐私

- 质量指标不包含用户个人信息
- 用户反馈可选匿名
- 聚合统计数据，不暴露单个用户行为

### 2. 偏见缓解

- 定期检查不同行业/类型的质量分布
- 避免算法对某些行业产生系统性偏见
- 多样化测试数据源

### 3. 透明度

- 向用户展示质量分计算方式
- 说明A/B测试的目的和影响
- 允许用户选择退出实验

---

## 📚 相关资源

### 论文和文献

1. **LLM Output Quality Evaluation**
   - "Automatic Evaluation of Text Generation"
   - "Metrics for Natural Language Generation"

2. **A/B Testing Best Practices**
   - "Trustworthy Online Controlled Experiments" (Microsoft)
   - "Practical Guide to Controlled Experiments on the Web" (Google)

3. **Prompt Engineering**
   - "The Prompt Report: A Systematic Survey"
   - "Large Language Model Prompt Engineering"

### 工具和库

1. **统计分析**
   - `scipy.stats` - T检验、卡方检验
   - `statsmodels` - 更多统计模型

2. **文本分析**
   - `jieba` - 中文分词
   - `nltk` - 自然语言处理
   - `textstat` - 可读性评分

3. **可视化**
   - `matplotlib` / `seaborn` - 后端图表生成
   - `Chart.js` / `Recharts` - 前端交互式图表

### 示例项目

1. **类似系统**
   - Google Experiments Platform
   - Optimizely
   - LaunchDarkly

2. **开源参考**
   - [Evidently AI](https://github.com/evidentlyai/evidently) - ML模型监控
   - [PlanOut](https://github.com/facebook/planout) - Facebook的A/B测试框架

---

## 🎯 总结

分析质量跟踪系统是一个**数据驱动的持续改进框架**，通过以下方式提升NewsGap的分析质量：

1. **量化评估**：5个维度的自动质量评分
2. **用户反馈**：收集真实用户的评价
3. **A/B测试**：科学验证Prompt改进效果
4. **性能监控**：追踪质量趋势和模型表现
5. **闭环优化**：反馈驱动的Prompt迭代

**实施建议**：
- 优先实现 Phase 1（质量评分）和 Phase 2（用户反馈）
- 积累2-4周数据后再启动A/B测试
- 逐步完善，避免一次性投入过大

**关键成功因素**：
- 准确的质量评分算法
- 足够的样本量（每个实验至少30个样本）
- 持续的迭代和优化意识

---

**最后更新**：2026-02-05  
**作者**：Kyusei  
**版本**：v1.0
