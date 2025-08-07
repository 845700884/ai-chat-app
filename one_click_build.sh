#!/bin/bash
# 一键APK构建脚本 - 在GitHub Codespaces中运行
# 作者: AI Assistant
# 版本: 1.0

set -e  # 遇到错误立即退出

echo "🚀 加密货币预测应用 - 一键APK构建"
echo "=================================================="
echo "⏰ 预计构建时间: 20-30分钟"
echo "💾 需要磁盘空间: ~3GB"
echo "=================================================="

# 检查必要文件
echo "🔍 检查项目文件..."
if [ ! -f "main.py" ]; then
    echo "❌ 错误: 未找到main.py文件"
    exit 1
fi

if [ ! -f "buildozer.spec" ]; then
    echo "❌ 错误: 未找到buildozer.spec文件"
    exit 1
fi

if [ ! -f "crypto_mobile_optimized.py" ]; then
    echo "❌ 错误: 未找到crypto_mobile_optimized.py文件"
    exit 1
fi

echo "✅ 项目文件检查完成"

# 1. 更新系统
echo "📦 更新系统包..."
sudo apt update -qq

# 2. 安装Java JDK
echo "☕ 安装Java JDK 8..."
sudo apt install -y openjdk-8-jdk

# 3. 设置JAVA_HOME
echo "🔧 配置Java环境..."
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
echo 'export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64' >> ~/.bashrc
echo "JAVA_HOME设置为: $JAVA_HOME"

# 4. 安装Android构建依赖
echo "📦 安装Android构建依赖..."
sudo apt install -y \
    git zip unzip autoconf libtool pkg-config \
    zlib1g-dev libncurses5-dev libncursesw5-dev \
    libtinfo5 cmake libffi-dev libssl-dev \
    build-essential ccache m4 libtool \
    libffi-dev libssl-dev libpng-dev libjpeg-dev

# 5. 安装Python依赖
echo "🐍 安装Python构建依赖..."
pip install --upgrade pip setuptools wheel
pip install buildozer cython==0.29.33

# 6. 清理之前的构建
echo "🧹 清理之前的构建文件..."
rm -rf .buildozer bin

# 7. 初始化buildozer（如果需要）
echo "⚙️ 初始化构建环境..."
buildozer android clean || true

# 8. 开始构建APK
echo "🔨 开始构建APK..."
echo "⏰ 这可能需要20-30分钟，请耐心等待..."
echo "📊 您可以在另一个终端运行以下命令查看进度:"
echo "   tail -f .buildozer/android/platform/build-*/build.log"
echo ""

# 构建APK
if buildozer android debug; then
    echo ""
    echo "🎉 APK构建成功！"
    echo "=================================================="

    # 检查APK文件
    if [ -f "bin/cryptopredict-1.0-debug.apk" ]; then
        APK_SIZE=$(du -h bin/cryptopredict-1.0-debug.apk | cut -f1)
        echo "📱 APK文件: bin/cryptopredict-1.0-debug.apk"
        echo "📊 文件大小: $APK_SIZE"
        echo ""
        echo "📥 下载步骤:"
        echo "1. 在左侧文件管理器中找到 bin/ 文件夹"
        echo "2. 右键点击 cryptopredict-1.0-debug.apk"
        echo "3. 选择 'Download' 下载到本地"
        echo ""
        echo "📱 安装步骤:"
        echo "1. 将APK传输到Android设备"
        echo "2. 开启'未知来源'安装权限"
        echo "3. 点击APK文件进行安装"
        echo ""
        echo "✅ 构建完成！享受您的加密货币预测应用！"
    else
        echo "❌ 错误: APK文件未生成"
        echo "请检查构建日志: .buildozer/android/platform/build-*/build.log"
    fi
else
    echo ""
    echo "❌ APK构建失败"
    echo "=================================================="
    echo "🔍 故障排除:"
    echo "1. 检查构建日志: .buildozer/android/platform/build-*/build.log"
    echo "2. 确保网络连接正常"
    echo "3. 重新运行脚本: ./one_click_build.sh"
    echo ""
    echo "📞 如需帮助，请查看README.md或提交Issue"
    exit 1
fi
