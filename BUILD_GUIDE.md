# 📱 APK构建指南

## 🎯 概述
由于Windows环境对Android开发工具链支持有限，我们提供多种APK构建方案。

## 🔧 方案对比

| 方案 | 难度 | 时间 | 推荐度 | 说明 |
|------|------|------|--------|------|
| GitHub Actions | ⭐ | 5-10分钟 | ⭐⭐⭐⭐⭐ | 最简单，自动化 |
| Docker | ⭐⭐ | 10-20分钟 | ⭐⭐⭐⭐ | 本地构建，可控性强 |
| WSL + Buildozer | ⭐⭐⭐ | 20-30分钟 | ⭐⭐⭐ | Windows子系统 |
| 在线服务 | ⭐ | 5分钟 | ⭐⭐⭐⭐ | 第三方服务 |

## 🚀 方案1: GitHub Actions (推荐)

### 步骤：
1. 将项目上传到GitHub仓库
2. 确保包含 `.github/workflows/build-apk.yml` 文件
3. 推送代码到main分支
4. 在GitHub Actions页面查看构建进度
5. 下载生成的APK文件

### 优势：
- ✅ 完全自动化
- ✅ 无需本地环境配置
- ✅ 支持多架构构建
- ✅ 免费使用

## 🐳 方案2: Docker构建

### 前提条件：
- 安装Docker Desktop

### 步骤：
```bash
# 1. 构建Docker镜像
docker build -t crypto-app .

# 2. 运行容器构建APK
docker run -v $(pwd)/bin:/app/bin crypto-app

# 3. APK文件将生成在 ./bin/ 目录
```

## 🐧 方案3: WSL + Buildozer

### 前提条件：
- 启用WSL2
- 安装Ubuntu

### 步骤：
```bash
# 1. 在WSL中安装依赖
sudo apt update
sudo apt install -y git zip unzip openjdk-8-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev

# 2. 安装Buildozer
pip3 install --user buildozer

# 3. 构建APK
buildozer android debug
```

## 🌐 方案4: 在线构建服务

### 推荐服务：
1. **Replit** - 在线IDE，支持Python
2. **CodeSandbox** - 在线开发环境
3. **Gitpod** - 基于VS Code的在线IDE

### 使用步骤：
1. 将代码上传到在线IDE
2. 安装buildozer
3. 运行构建命令

## 📋 构建文件清单

确保项目包含以下文件：
- ✅ `main.py` - 应用入口
- ✅ `crypto_mobile_optimized.py` - 主应用代码
- ✅ `buildozer.spec` - 构建配置
- ✅ `Dockerfile` - Docker构建文件
- ✅ `.github/workflows/build-apk.yml` - GitHub Actions配置

## 🔍 构建后验证

APK构建成功后，检查：
1. 文件大小 (通常10-50MB)
2. 安装到Android设备测试
3. 检查权限设置
4. 验证网络连接功能

## 🐛 常见问题

### Q: 构建失败怎么办？
A: 检查以下项目：
- Python版本兼容性
- 依赖包版本
- 网络连接
- 磁盘空间

### Q: APK无法安装？
A: 可能原因：
- 需要开启"未知来源"安装
- 签名问题
- 架构不匹配

### Q: 应用闪退？
A: 检查：
- 权限设置
- 网络连接
- 字体文件

## 📞 技术支持

如果遇到问题，可以：
1. 查看构建日志
2. 检查GitHub Actions输出
3. 参考Kivy官方文档
4. 搜索相关错误信息

---

**推荐使用GitHub Actions方案，最简单且成功率最高！** 🎉
