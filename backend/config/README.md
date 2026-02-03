# 信息源配置系统

## 📋 概述

NewsGap 支持两种方式管理信息源：

1. **YAML 配置文件** (推荐) - `config/sources.yaml`
2. **Python 代码** (传统) - `official_rss_sources.py`

## 🎯 为什么使用配置文件？

### 优点
- ✅ **易于编辑** - 无需修改代码，直接编辑 YAML
- ✅ **版本控制友好** - 更清晰的 git diff
- ✅ **非技术人员友好** - 运营人员也能添加源
- ✅ **结构清晰** - 按分类组织
- ✅ **热重载** - 修改后重启即生效

### 缺点
- ⚠️ 需要额外的 YAML 解析依赖
- ⚠️ 错误配置可能导致启动失败

## 🚀 快速开始

### 启用 YAML 配置

设置环境变量：

```bash
export USE_YAML_CONFIG=true
```

或在 `.env` 文件中：

```
USE_YAML_CONFIG=true
```

### 编辑配置文件

编辑 `config/sources.yaml`：

```yaml
official_rss:
  - name: "你的信息源"
    url: "https://example.com/feed"
    type: "rss"
    priority: "official_rss"
    industry: "tech"
    enabled: true
    metadata:
      description: "描述信息"
```

### 重启服务

```bash
./stop.sh
./start.sh
```

## 📖 配置文件格式

### 基本结构

```yaml
# 分类名称（可自定义）
category_name:
  - name: "源名称"          # 必需：显示名称
    url: "https://..."      # 必需：RSS/订阅地址
    type: "rss"             # 必需：rss/web/api
    priority: "official_rss" # 必需：优先级
    industry: "tech"        # 必需：行业分类
    enabled: true           # 可选：是否启用（默认 true）
    fetch_interval_hours: 24 # 可选：爬取间隔（默认 24）
    metadata:               # 可选：额外信息
      description: "描述"
      layer: 1
```

### 字段说明

#### `type` - 信息源类型
- `rss` - RSS/Atom 订阅
- `web` - 网页爬取
- `api` - API 接口

#### `priority` - 优先级
- `official_rss` - 官方 RSS（最稳定）
- `rsshub_stable` - RSSHub 稳定路由
- `rsshub_high_risk` - RSSHub 高风险路由
- `custom_crawler` - 自定义爬虫

#### `industry` - 行业分类
- `social` - 社交媒体
- `news` - 新闻资讯
- `tech` - 科技互联网
- `developer` - 开发者
- `finance` - 财经金融
- `crypto` - 加密货币
- `entertainment` - 娱乐影视
- `gaming` - 游戏电竞
- `anime` - 动漫二次元
- `shopping` - 电商购物
- `education` - 教育学习
- `lifestyle` - 生活方式
- `other` - 其他

## 🔧 高级用法

### 按分类组织

建议按源的特性分类：

```yaml
# 官方 RSS（最稳定）
official_rss:
  - name: "..."
    # ...

# RSSHub 通用源
rsshub_general:
  - name: "..."
    # ...

# 财经专业源
finance:
  - name: "..."
    # ...

# 高风险源（默认禁用）
high_risk:
  - name: "..."
    enabled: false
    # ...
```

### 使用元数据

```yaml
metadata:
  description: "描述信息"
  update_freq: "实时"      # 更新频率
  layer: 1                 # 信息层级（财经专用）
  asset_class: "crypto"    # 资产类别
  customizable: true       # 是否可自定义
  warning: "注意事项"      # 警告信息
```

### 条件启用

根据环境启用不同的源：

```yaml
# 开发环境
- name: "测试源"
  url: "http://localhost:8080/feed"
  enabled: true

# 生产环境（手动修改为 false）
- name: "测试源"
  url: "http://localhost:8080/feed"
  enabled: false
```

## 🔄 迁移指南

### 从 Python 迁移到 YAML

1. **备份当前配置**
   ```bash
   cp backend/official_rss_sources.py backend/official_rss_sources.py.bak
   ```

2. **运行迁移脚本**（如果有）
   ```bash
   python backend/scripts/migrate_sources_to_yaml.py
   ```

3. **验证配置**
   ```bash
   cd backend
   PYTHONPATH=. python3 config/source_loader.py
   ```

4. **启用 YAML**
   ```bash
   export USE_YAML_CONFIG=true
   ./start.sh
   ```

## 🐛 故障排查

### 配置加载失败

**症状**: 启动时显示"YAML 加载失败"

**解决**:
1. 检查 YAML 语法：
   ```bash
   python3 -c "import yaml; yaml.safe_load(open('backend/config/sources.yaml'))"
   ```

2. 检查必需字段是否缺失

3. 系统会自动回退到 Python 文件

### 源未生效

**症状**: 添加的源没有出现在前端

**原因**: 数据库中已有该 URL 的源

**解决**:
1. 删除数据库中的旧源（通过设置页面）
2. 重启后端，触发重新加载

### 重复的源

**症状**: 同一个源被添加多次

**原因**: URL 不同但实际相同

**解决**: 统一使用 `http://localhost:1200` 作为 RSSHub 地址

## 📚 最佳实践

1. **使用注释** - 在 YAML 中添加说明注释
2. **分类清晰** - 按功能/稳定性分组
3. **默认禁用高风险源** - 避免频繁失败
4. **提供元数据** - 帮助用户理解源的用途
5. **版本控制** - 将配置文件纳入 Git
6. **定期审查** - 移除失效的源

## 🔗 相关文件

- `config/sources.yaml` - 主配置文件
- `config/source_loader.py` - 配置加载器
- `official_rss_sources.py` - Python 源定义（向后兼容）
- `main.py` - 启动时加载逻辑

## 📞 获取帮助

如有问题，请：
1. 查看日志：`tail -f logs/backend.log`
2. 运行测试：`PYTHONPATH=. python3 config/source_loader.py`
3. 提交 Issue
