# 网络代理功能指南

## 概述

NewsGap现已支持全局网络代理配置，允许通过HTTP/SOCKS5代理服务器访问RSS源和AI API。此功能特别适用于受限网络环境或需要通过代理访问外部资源的场景。

## 功能特性

### 支持范围
- ✅ RSS feed拉取（所有HTTP/HTTPS请求）
- ✅ AI API调用（OpenAI、DeepSeek、Gemini、Ollama）
- ✅ 网页内容提取
- ✅ 所有网络请求统一使用代理配置

### 支持协议
- HTTP代理
- SOCKS5代理

### 配置持久化
- 代理配置存储在SQLite数据库中
- 重启服务后配置自动生效
- 可随时启用/禁用

## 使用方法

### 方法一：通过前端界面配置（推荐）

1. 访问 `设置` 页面
2. 找到 `网络代理配置` 部分
3. 点击 `配置代理`
4. 填写以下信息：
   - **启用代理**：勾选复选框
   - **代理协议**：选择 HTTP 或 SOCKS5
   - **代理地址**：如 `127.0.0.1` 或 `proxy.example.com`
   - **端口**：如 `7890`（Clash默认端口）
5. 点击 `保存`

配置完成后，所有网络请求将自动通过代理服务器。

### 方法二：通过API配置

#### 设置代理
```bash
curl -X POST http://localhost:8000/api/config/proxy \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "host": "127.0.0.1",
    "port": 7890,
    "protocol": "http"
  }'
```

#### 查询代理配置
```bash
curl http://localhost:8000/api/config/proxy
```

#### 禁用代理
```bash
curl -X DELETE http://localhost:8000/api/config/proxy
```

## 常见使用场景

### 场景1：使用Clash代理

**Clash配置示例**：
```yaml
port: 7890
socks-port: 7891
allow-lan: true
mode: Rule
```

**NewsGap配置**：
- 代理地址：`127.0.0.1`
- 端口：`7890`
- 协议：`HTTP`

### 场景2：使用V2Ray代理

**V2Ray通常使用的端口**：
- HTTP: 10809
- SOCKS5: 10808

**NewsGap配置**：
- 代理地址：`127.0.0.1`
- 端口：`10809`（HTTP）或 `10808`（SOCKS5）
- 协议：根据实际配置选择

### 场景3：企业网络代理

```
代理地址：proxy.company.com
端口：8080
协议：HTTP
```

### 场景4：使用代理访问受限RSS源

如果某些RSS源在你的网络环境中无法访问：
1. 配置代理服务器
2. 启用代理
3. 重新拉取RSS源

所有请求将自动通过代理进行。

## API接口说明

### GET /api/config/proxy
获取当前代理配置

**响应示例**：
```json
{
  "enabled": true,
  "host": "127.0.0.1",
  "port": 7890,
  "protocol": "http"
}
```

### POST /api/config/proxy
设置代理配置

**请求体**：
```json
{
  "enabled": true,
  "host": "127.0.0.1",
  "port": 7890,
  "protocol": "http"
}
```

**响应示例**：
```json
{
  "success": true,
  "message": "代理配置已保存",
  "config": {
    "enabled": true,
    "host": "127.0.0.1",
    "port": 7890,
    "protocol": "http"
  }
}
```

### DELETE /api/config/proxy
禁用代理配置

**响应示例**：
```json
{
  "success": true,
  "message": "代理配置已禁用"
}
```

## 技术实现

### 后端架构

1. **ConfigManager** (`backend/config_manager.py`)
   - `get_proxy_config()`: 获取代理配置
   - `set_proxy_config()`: 设置代理配置
   - `get_proxy_url()`: 返回格式化的代理URL

2. **Fetcher** (`backend/crawler/fetcher.py`)
   - 构造函数支持 `proxy_url` 参数
   - 使用httpx的proxies参数配置代理
   - 所有HTTP请求统一使用代理

3. **LLM适配器** (`backend/llm/`)
   - 所有适配器基类支持 `proxy_url` 参数
   - OpenAI/DeepSeek：使用httpx.AsyncClient配置代理
   - Gemini：通过环境变量设置代理
   - Ollama：使用httpx的proxies参数

4. **路由层**
   - `routes/fetch.py`：爬虫依赖注入时自动获取代理配置
   - `routes/analyze.py`：分析器创建时自动传递代理配置
   - `routes/config.py`：提供代理配置CRUD端点

### 前端架构

1. **API客户端** (`frontend/src/services/api.ts`)
   - `getProxyConfig()`: 获取代理配置
   - `setProxyConfig()`: 设置代理配置
   - `deleteProxyConfig()`: 禁用代理配置

2. **设置页面** (`frontend/src/pages/Settings.tsx`)
   - `ProxyConfigManager` 组件
   - 可视化配置界面
   - 实时状态显示

## 注意事项

### 1. 代理服务器要求
- 确保代理服务器正常运行
- 确保代理服务器允许访问目标资源
- 确认代理服务器的协议类型（HTTP或SOCKS5）

### 2. 性能影响
- 使用代理会增加网络延迟
- 建议使用本地代理服务器（如Clash、V2Ray）以减少延迟
- 代理服务器的带宽会影响RSS拉取和API调用速度

### 3. 安全性
- 代理配置存储在本地数据库中
- 不要使用不可信的代理服务器
- 敏感数据（如API Key）通过代理传输时请确保代理服务器可信

### 4. 特殊说明

#### Gemini代理配置
Gemini使用环境变量设置代理。如果修改代理配置后遇到问题：
1. 重启后端服务
2. 确认环境变量已更新

#### Ollama本地模型
如果Ollama运行在本地，通常不需要配置代理。但如果Ollama需要访问外部资源，可以配置代理。

## 故障排查

### 问题1：代理配置后无法访问网络

**检查步骤**：
```bash
# 1. 确认代理配置
curl http://localhost:8000/api/config/proxy

# 2. 测试代理服务器
curl -x http://127.0.0.1:7890 https://www.google.com

# 3. 查看后端日志
tail -f logs/backend.log
```

**可能原因**：
- 代理服务器未运行
- 代理地址或端口配置错误
- 代理服务器无法访问目标资源

### 问题2：RSS拉取失败

**解决方案**：
1. 检查代理配置是否正确
2. 测试代理服务器是否能访问RSS源
3. 尝试禁用代理，确认是否为代理问题
4. 查看后端日志获取详细错误信息

### 问题3：AI API调用失败

**解决方案**：
1. 确认API Key配置正确
2. 确认代理服务器允许访问AI API域名
3. 对于Gemini，尝试重启后端服务
4. 检查代理服务器的协议类型是否正确

### 问题4：部分请求使用代理，部分不使用

**说明**：
- 一旦启用代理，所有网络请求都会使用代理
- 如果出现不一致，可能是配置未生效
- 尝试重启后端服务

## 测试代理功能

### 测试1：测试代理连接
```python
# backend/test_proxy.py
import asyncio
from crawler.fetcher import Fetcher

async def test():
    fetcher = Fetcher(proxy_url="http://127.0.0.1:7890")
    try:
        content, status = await fetcher.fetch("https://www.google.com")
        print(f"✓ 代理连接成功！Status: {status}")
    except Exception as e:
        print(f"✗ 代理连接失败：{str(e)}")

asyncio.run(test())
```

### 测试2：测试RSS拉取
1. 配置代理
2. 在前端选择一个RSS源
3. 点击拉取
4. 查看是否成功获取文章

### 测试3：测试AI API
1. 配置代理
2. 配置AI API Key
3. 执行分析任务
4. 查看是否成功生成分析报告

## 最佳实践

1. **首次配置**：
   - 先测试代理服务器是否正常
   - 再在NewsGap中配置代理
   - 从简单的RSS源测试开始

2. **日常使用**：
   - 根据网络环境灵活启用/禁用代理
   - 定期检查代理服务器状态
   - 注意监控网络延迟

3. **问题排查**：
   - 首先确认代理服务器状态
   - 查看后端日志获取详细错误
   - 尝试禁用代理对比测试

## 开发说明

如果需要进一步开发或自定义：

### 添加新的代理协议
修改 `backend/config_manager.py` 的 `get_proxy_url()` 方法：
```python
def get_proxy_url(self) -> Optional[str]:
    config = await self.get_proxy_config()
    if config and config.get('enabled'):
        protocol = config.get('protocol', 'http')
        # 添加新协议支持
        if protocol == 'custom':
            return f"custom://{host}:{port}"
```

### 添加代理日志
在 `backend/crawler/fetcher.py` 中：
```python
import logging
logger = logging.getLogger(__name__)

def __init__(self, proxy_url: Optional[str] = None):
    if proxy_url:
        logger.info(f"使用代理: {proxy_url}")
```

### 添加代理认证
如果代理服务器需要认证：
```python
# 在ConfigManager中添加用户名和密码字段
proxy_url = f"{protocol}://{username}:{password}@{host}:{port}"
```

## 总结

NewsGap的代理功能为在受限网络环境中使用提供了完整的解决方案。通过简单的配置，即可让所有网络请求通过代理服务器，确保RSS源和AI API的正常访问。配置持久化和可视化界面使得代理管理变得简单高效。
