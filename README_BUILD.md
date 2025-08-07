# AI聊天助手 - 构建指南

## 🚀 方法1：GitHub Actions自动构建 (推荐)

### 步骤：
1. 将代码推送到GitHub仓库
2. 在GitHub仓库页面，点击 "Actions" 标签
3. 点击 "Build Android APK" 工作流
4. 点击 "Run workflow" 按钮
5. 等待构建完成（约10-15分钟）
6. 下载生成的APK文件

### 优点：
- ✅ 无需本地安装任何工具
- ✅ 自动处理所有依赖
- ✅ 构建环境稳定
- ✅ 支持自动发布

---

## 🌐 方法2：使用Replit在线构建

### 步骤：
1. 访问 https://replit.com
2. 创建新的Python项目
3. 上传所有项目文件
4. 在Shell中运行：
   ```bash
   pip install buildozer
   buildozer android debug
   ```
5. 下载生成的APK

---

## 🐳 方法3：使用Docker本地构建

### 前提条件：
- 安装Docker Desktop

### 步骤：
```bash
# 构建Docker镜像
docker build -f Dockerfile.android -t ai-chat-builder .

# 运行构建
docker run --rm -v $(pwd)/output:/output ai-chat-builder

# APK文件将保存在 output/ 目录
```

---

## 📱 方法4：直接在Android手机运行

### 使用Termux：
1. 在手机上安装Termux应用
2. 在Termux中运行：
   ```bash
   pkg install python
   pip install kivy requests
   python crypto_mobile_optimized.py
   ```

---

## 🔧 本地构建问题解决

如果遇到buildozer问题：

### Windows用户：
```powershell
# 使用WSL2
wsl --install
# 然后在WSL中构建
```

### 网络问题：
```bash
# 设置pip镜像源
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 📦 APK安装说明

1. **下载APK文件**到手机
2. **允许未知来源安装**：
   - 设置 → 安全 → 未知来源 → 开启
3. **点击APK文件安装**
4. **首次运行时允许权限**：
   - 网络权限
   - 震动权限
   - 存储权限

---

## 🎯 推荐方案

**最简单：** GitHub Actions自动构建
**最快速：** Replit在线构建  
**最稳定：** Docker本地构建

选择适合你的方法开始构建吧！🚀
