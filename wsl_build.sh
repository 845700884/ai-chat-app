#!/bin/bash
# WSL环境下的APK构建脚本
# 密码: a5252169

echo "🐧 WSL环境APK构建脚本"
echo "=================================================="

# 获取Windows主机IP地址
WINDOWS_IP=$(ip route show | grep -i default | awk '{ print $3}')
echo "🔍 检测到Windows主机IP: $WINDOWS_IP"

# 设置代理 - 使用Windows主机IP
export http_proxy=http://$WINDOWS_IP:55395
export https_proxy=http://$WINDOWS_IP:55395
export HTTP_PROXY=http://$WINDOWS_IP:55395
export HTTPS_PROXY=http://$WINDOWS_IP:55395

echo "🌐 代理已设置: http://$WINDOWS_IP:55395"

# 测试代理连接
echo "🔗 测试代理连接..."
if curl -s --connect-timeout 5 --proxy $http_proxy http://www.google.com > /dev/null; then
    echo "✅ 代理连接正常"
else
    echo "❌ 代理连接失败，尝试不使用代理"
    unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
fi

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

echo "✅ 项目文件检查完成"

# 1. 安装Java JDK 8
echo "☕ 安装Java JDK 8..."
echo "a5252169" | sudo -S apt install -y openjdk-8-jdk

# 2. 安装构建依赖
echo "📦 安装构建依赖..."
echo "a5252169" | sudo -S apt install -y \
    git zip unzip autoconf libtool pkg-config \
    zlib1g-dev libncurses5-dev libncursesw5-dev \
    libtinfo5 cmake libffi-dev libssl-dev \
    build-essential ccache m4 \
    libffi-dev libssl-dev libpng-dev libjpeg-dev \
    python3-pip python3-dev

# 3. 设置Java环境
echo "🔧 配置Java环境..."
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export PATH=$PATH:$JAVA_HOME/bin:$HOME/.local/bin

# 4. 安装Python依赖
echo "🐍 安装Python依赖..."
# 检查pip3是否存在，如果不存在则安装
if ! command -v pip3 &> /dev/null; then
    echo "安装pip3..."
    echo "a5252169" | sudo -S apt install -y python3-pip
fi

# 安装Python构建依赖 (使用--break-system-packages绕过Ubuntu 24.04限制)
python3 -m pip install --upgrade pip setuptools wheel --break-system-packages
python3 -m pip install buildozer cython==0.29.33 --break-system-packages

# 5. 清理之前的构建
echo "🧹 清理之前的构建文件..."
rm -rf .buildozer bin

# 6. 开始构建APK
echo "🔨 开始构建APK..."
echo "⏰ 这可能需要20-30分钟，请耐心等待..."

# 设置buildozer环境变量
export BUILDOZER_LOG_LEVEL=2

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
        echo "📥 APK文件已生成在Windows路径:"
        echo "   $(wslpath -w $(pwd))/bin/cryptopredict-1.0-debug.apk"
        echo ""
        echo "📱 安装步骤:"
        echo "1. 将APK传输到Android设备"
        echo "2. 开启'未知来源'安装权限"
        echo "3. 点击APK文件进行安装"
        echo ""
        echo "✅ 构建完成！享受您的加密货币预测应用！"
    else
        echo "❌ 错误: APK文件未生成"
        echo "请检查构建日志"
    fi
else
    echo ""
    echo "❌ APK构建失败"
    echo "=================================================="
    echo "🔍 故障排除:"
    echo "1. 检查网络连接和代理设置"
    echo "2. 确保所有依赖已正确安装"
    echo "3. 重新运行脚本"
    exit 1
fi
