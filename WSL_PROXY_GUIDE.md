# WSL支持和网络代理功能指南

## 概述

此分支（`wsl-proxy-support`）为NewsGap项目添加了WSL环境支持和全局网络代理功能，适用于需要在WSL环境中运行或需要通过代理访问网络的场景。

## 新增功能

### 1. WSL环境支持

**问题**：默认情况下，WSL中的服务绑定到localhost，Windows无法直接通过localhost访问。

**解决方案**：
- 后端服务绑定到 `0.0.0.0`，允许从任何网络接口访问
- CORS配置支持通过WSL IP地址访问（如 `http://172.x.x.x:5173`）
- 支持正则表达式匹配任意IP的5173端口

**使用方法**：

1. 在WSL中启动后端服务：
   ```bash
   cd backend
   python main.py
   ```
   
2. 获取WSL的IP地址：
   ```bash
   hostname -I
   # 输出类似: 172.28.144.1
   ```

3. 在Windows浏览器中访问：
   ```
   http://172.28.144.1:5173
   ```

4. 配置前端环境变量（如需要）：
   ```bash
   # frontend/.env.local
   VITE_API_BASE_URL=http://172.28.144.1:8000
   ```

### 2. 网络代理功能

**支持范围**：
- RSS feed拉取（所有HTTP/HTTPS请求）
- AI API调用（OpenAI、DeepSeek、Gemini、Ollama）
- 网页内容提取

**支持协议**：
- HTTP代理
- SOCKS5代理

**配置方式**：

#### 方法一：通过前端界面配置（推荐）

1. 访问 `设置` 页面
2. 找到 `网络代理配置` 部分
3. 点击 `配置代理`
4. 填写以下信息：
   - 启用代理：勾选复选框
   - 代理协议：选择 HTTP 或 SOCKS5
   - 代理地址：如 `127.0.0.1` 或 `proxy.example.com`
   - 端口：如 `7890`（Clash默认端口）
5. 点击 `保存`

#### 方法二：直接调用API

```bash
# 设置代理
curl -X POST http://localhost:8000/api/config/proxy \
  -H "Content-Type: application/json" \
  -d '{
    "enabled": true,
    "host": "127.0.0.1",
    "port": 7890,
    "protocol": "http"
  }'

# 查询代理配置
curl http://localhost:8000/api/config/proxy

# 禁用代理
curl -X DELETE http://localhost:8000/api/config/proxy
```

## 技术实现

### 后端架构

1. **ConfigManager** (`backend/config_manager.py`)
   - 新增 `get_proxy_config()` 和 `set_proxy_config()` 方法
   - 新增 `get_proxy_url()` 方法，返回格式化的代理URL
   - 代理配置存储在SQLite数据库的config表中

2. **Fetcher** (`backend/crawler/fetcher.py`)
   - 构造函数新增 `proxy_url` 参数
   - 使用httpx的proxies参数配置代理

3. **LLM适配器** (`backend/llm/`)
   - 所有适配器基类新增 `proxy_url` 参数
   - OpenAI/DeepSeek：使用httpx.AsyncClient配置代理
   - Gemini：通过环境变量设置代理（HTTP_PROXY/HTTPS_PROXY）
   - Ollama：通过httpx的proxies参数配置

4. **路由层**
   - `routes/fetch.py`：爬虫依赖注入时获取代理配置
   - `routes/analyze.py`：分析器创建时传递代理配置
   - `routes/config.py`：新增代理配置CRUD端点

### 前端架构

1. **API客户端** (`frontend/src/services/api.ts`)
   - 新增 `getProxyConfig()`、`setProxyConfig()`、`deleteProxyConfig()` 方法

2. **设置页面** (`frontend/src/pages/Settings.tsx`)
   - 新增 `ProxyConfigManager` 组件
   - 支持可视化配置代理
   - 实时显示配置状态

## 常见使用场景

### 场景1：WSL开发环境

```bash
# WSL中启动后端
cd backend
python main.py

# WSL中启动前端
cd frontend
npm run dev

# Windows浏览器访问
# 1. 获取WSL IP: wsl hostname -I
# 2. 访问: http://<WSL_IP>:5173
```

### 场景2：使用Clash代理

```yaml
# Clash配置文件（示例）
port: 7890
socks-port: 7891
allow-lan: true
mode: Rule
```

在NewsGap中配置：
- 代理地址：`127.0.0.1`
- 端口：`7890`
- 协议：`HTTP`

### 场景3：企业网络代理

```
代理地址：proxy.company.com
端口：8080
协议：HTTP
```

## 注意事项

1. **代理配置持久化**：代理配置保存在数据库中，重启服务后仍然有效

2. **代理测试**：配置代理后，建议先测试RSS拉取功能，确认代理工作正常

3. **性能影响**：使用代理可能会增加网络延迟，特别是在链路较长的情况下

4. **安全性**：
   - 代理配置存储在本地数据库中
   - 建议在可信网络环境中使用
   - 不要使用不可信的代理服务器

5. **Gemini特殊说明**：
   - Gemini使用环境变量设置代理
   - 如果遇到问题，可以重启后端服务
   - 代理变更后建议重启服务确保生效

## 故障排查

### 问题1：Windows无法访问WSL服务

**解决方案**：
```bash
# 1. 确认WSL服务正在运行
ps aux | grep uvicorn

# 2. 确认监听地址
netstat -tuln | grep 8000
# 应该显示: 0.0.0.0:8000 而不是 127.0.0.1:8000

# 3. 确认防火墙规则（WSL2）
# Windows PowerShell (管理员)
New-NetFirewallRule -DisplayName "WSL" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

### 问题2：代理不生效

**检查步骤**：
```bash
# 1. 确认代理配置
curl http://localhost:8000/api/config/proxy

# 2. 确认代理服务器可访问
curl -x http://127.0.0.1:7890 https://www.google.com

# 3. 查看后端日志
tail -f logs/backend.log
```

### 问题3：Gemini代理配置问题

**解决方案**：
```bash
# 重启后端服务以确保环境变量生效
pkill -f "python main.py"
python main.py
```

## 开发说明

如果需要进一步开发或调试：

1. **添加新的代理协议支持**：
   - 修改 `backend/config_manager.py` 的 `get_proxy_url()` 方法
   - 更新前端的协议选择选项

2. **调试代理连接**：
   - 在 `backend/crawler/fetcher.py` 中添加日志
   - 使用 `logger.debug(f"Using proxy: {self.proxy_url}")`

3. **测试代理功能**：
   ```python
   # backend/test_proxy.py
   import asyncio
   from crawler.fetcher import Fetcher
   
   async def test():
       fetcher = Fetcher(proxy_url="http://127.0.0.1:7890")
       content, status = await fetcher.fetch("https://www.google.com")
       print(f"Status: {status}, Length: {len(content)}")
   
   asyncio.run(test())
   ```

## 总结

此分支为NewsGap添加了完整的WSL支持和网络代理功能，使其能够在更多环境中稳定运行。所有网络请求（RSS拉取和AI API调用）都支持通过代理服务器进行，配置简单且持久化。
