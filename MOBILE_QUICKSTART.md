# 📱 移动端快速开始指南

> 5 分钟快速体验 NewsGap 移动端功能

## 🚀 快速启动

### 1. 启动服务

```bash
# 确保已完成基础部署（如未完成，先运行 ./deploy.sh）
./start.sh
```

### 2. 查找电脑 IP 地址

**macOS/Linux:**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
# 或
ipconfig getifaddr en0  # Wi-Fi
```

**Windows:**
```cmd
ipconfig
# 查找 "IPv4 地址"
```

### 3. 移动端访问

1. **确保设备在同一 Wi-Fi 网络**
2. **在手机/平板浏览器输入:**
   ```
   http://[你的电脑IP]:5173
   ```
   
   **示例:** `http://192.168.1.100:5173`

3. **首次访问可能需要允许防火墙访问**

## ✨ 移动端特性

- ✅ **汉堡菜单** - 点击右上角菜单按钮展开导航
- ✅ **响应式布局** - 自动适配手机和平板屏幕
- ✅ **触摸优化** - 按钮和表单针对触摸屏优化
- ✅ **横竖屏支持** - 自动适应设备方向

## 📱 使用技巧

### 导航
- 点击 **右上角** 的汉堡菜单图标 (☰) 打开导航
- 选择页面后自动关闭菜单
- 点击遮罩层也可关闭菜单

### 最佳体验
- **推荐使用**: Safari (iOS) 或 Chrome (Android)
- **网络**: 保持设备与电脑在同一 Wi-Fi
- **横屏**: 在归档管理等数据密集页面使用横屏获得更好体验

## 🔧 常见问题

### ❌ 无法访问？

**检查清单:**
1. ✅ 设备和电脑在同一 Wi-Fi？
2. ✅ IP 地址正确？
3. ✅ 防火墙已允许？
4. ✅ 服务正在运行？(`./status.sh`)

**快速测试:**
```bash
# 在电脑上测试后端是否正常
curl http://localhost:8000/api/health

# 查看访问日志
tail -f logs/frontend.log
```

### 🔥 防火墙设置

**macOS:**
```bash
# 系统偏好设置 → 安全性与隐私 → 防火墙
# 允许 Node.js 接受传入连接
```

**Windows:**
```powershell
# 以管理员身份运行 PowerShell
New-NetFirewallRule -DisplayName "NewsGap Dev" -Direction Inbound -LocalPort 5173 -Protocol TCP -Action Allow
```

**Linux (ufw):**
```bash
sudo ufw allow 5173/tcp
sudo ufw reload
```

## 📖 更多文档

- [完整移动端适配说明](docs/mobile-support.md)
- [详细构建和部署指南](docs/build-and-deploy.md)
- [分支完整总结](docs/mobile-branch-summary.md)
- [主 README](README.md)

## 💡 提示

### 添加到主屏幕（PWA 样式）

**iOS Safari:**
1. 打开网站
2. 点击分享按钮
3. 选择"添加到主屏幕"
4. 像原生 App 一样使用

**Android Chrome:**
1. 打开网站
2. 点击菜单 (⋮)
3. 选择"添加到主屏幕"
4. 创建快捷方式

### 开发模式下的网络访问

如果你修改了配置禁用了网络访问，可以临时启用:

```bash
cd frontend
npm run dev -- --host
```

或永久启用（已默认开启）:
```typescript
// frontend/vite.config.ts
server: {
  host: '0.0.0.0',  // ✅ 已配置
  port: 5173,
}
```

## 🎯 下一步

移动端体验满意？试试这些功能:

1. **一键情报** - 在首页快速生成行业情报
2. **文章筛选** - 在文章列表页按行业和状态筛选
3. **归档分析** - 在归档管理页分析历史数据
4. **自定义分类** - 在设置页创建专属信息源

---

**遇到问题?**  
查看 [故障排查指南](docs/build-and-deploy.md#故障排查) 或提交 Issue

**版本**: mobile-support 分支  
**更新**: 2026-02-03
