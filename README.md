# 🚀 加密货币预测移动应用

## 📱 项目简介
基于Kivy开发的移动端加密货币价格预测应用，支持BTC和ETH的智能分析。

## ✨ 主要功能
- 🤖 AI智能预测（10分钟、30分钟、60分钟）
- 💰 实时价格获取
- 📊 凯莉公式仓位建议
- 🔔 弹窗提示系统
- 📳 震动反馈功能
- 📱 移动端优化界面

## 🔨 一键构建APK

### 使用GitHub Codespaces构建：

1. **点击绿色"Code"按钮**
2. **选择"Codespaces" → "Create codespace"**
3. **等待环境启动**（约2-3分钟）
4. **在终端中运行**：
   ```bash
   chmod +x one_click_build.sh
   ./one_click_build.sh
   ```
5. **等待构建完成**（约20-30分钟）
6. **下载APK文件**：`bin/cryptopredict-1.0-debug.apk`

### 构建状态检查：
```bash
# 检查构建进度
tail -f .buildozer/android/platform/build-*/build.log

# 检查APK文件
ls -la bin/
```

## 📱 安装测试
1. 将APK文件传输到Android设备
2. 开启"未知来源"安装权限
3. 安装并测试应用功能

## 🛠️ 技术栈
- **框架**: Kivy 2.3.1
- **语言**: Python 3.9
- **打包**: Buildozer
- **API**: 币安API + Grok-4 AI

## 📞 支持
如有问题，请查看构建日志或提交Issue。

---
**享受智能投资分析！** 🎉
