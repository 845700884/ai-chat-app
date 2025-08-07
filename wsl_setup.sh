#!/bin/bash
# WSL环境下的APK构建脚本
# 在WSL Ubuntu中运行

echo "🐧 WSL环境APK构建脚本"
echo "=================================================="

# 检查是否在WSL环境中
if ! grep -q Microsoft /proc/version; then
    echo "⚠️  警告: 此脚本需要在WSL环境中运行"
    echo "请在Windows中打开WSL终端后运行此脚本"
    exit 1
fi

echo "✅ 检测到WSL环境"

# 1. 更新系统
echo "📦 更新系统包..."
sudo apt update && sudo apt upgrade -y

# 2. 安装Java JDK 8
echo "☕ 安装Java JDK 8..."
sudo apt install -y openjdk-8-jdk

# 3. 安装构建依赖
echo "📦 安装构建依赖..."
sudo apt install -y \
    git zip unzip autoconf libtool pkg-config \
    zlib1g-dev libncurses5-dev libncursesw5-dev \
    libtinfo5 cmake libffi-dev libssl-dev \
    build-essential ccache m4 \
    libffi-dev libssl-dev libpng-dev libjpeg-dev \
    python3-pip python3-dev

# 4. 设置Java环境
echo "🔧 配置Java环境..."
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
echo 'export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64' >> ~/.bashrc
echo 'export PATH=$PATH:$JAVA_HOME/bin' >> ~/.bashrc

# 5. 安装Python依赖
echo "🐍 安装Python依赖..."
pip3 install --upgrade pip setuptools wheel
pip3 install buildozer cython==0.29.33

# 6. 设置Android环境变量
echo "📱 配置Android环境..."
echo 'export ANDROID_HOME=$HOME/.buildozer/android/platform/android-sdk' >> ~/.bashrc
echo 'export PATH=$PATH:$ANDROID_HOME/tools:$ANDROID_HOME/platform-tools' >> ~/.bashrc

# 重新加载环境变量
source ~/.bashrc

echo "✅ WSL环境配置完成！"
echo ""
echo "📋 下一步操作："
echo "1. 将Windows中的项目文件复制到WSL"
echo "2. 运行构建脚本: ./wsl_build.sh"
echo ""
echo "💡 复制文件命令示例："
echo "cp -r /mnt/d/Projects/kaggle/ai_B/code/* ."
