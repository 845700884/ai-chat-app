#!/bin/bash

echo "🚀 开始构建Android APK..."

# 创建输出目录
mkdir -p output

# 使用Docker构建APK
docker build -f Dockerfile.android -t ai-chat-builder .

# 运行容器并复制APK
docker run --rm -v $(pwd)/output:/output ai-chat-builder

echo "✅ APK构建完成！文件位于 output/ 目录"
echo "📱 你可以将APK文件传输到Android手机安装"
