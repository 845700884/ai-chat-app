#!/usr/bin/env python3
"""
Replit一键构建脚本
在 https://replit.com 中运行
"""

import os
import subprocess
import sys

def setup_environment():
    """设置构建环境"""
    print("🔧 设置构建环境...")
    
    # 安装系统依赖
    os.system("apt update")
    os.system("apt install -y openjdk-8-jdk git zip unzip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev")
    
    # 设置Java环境
    os.environ['JAVA_HOME'] = '/usr/lib/jvm/java-8-openjdk-amd64'
    
    # 安装Python依赖
    subprocess.check_call([sys.executable, "-m", "pip", "install", "buildozer", "cython"])

def build_apk():
    """构建APK"""
    print("🔨 开始构建APK...")
    
    try:
        # 运行buildozer
        result = subprocess.run(["buildozer", "android", "debug"], 
                              capture_output=True, text=True, timeout=3600)
        
        if result.returncode == 0:
            print("✅ APK构建成功！")
            print("📱 APK文件位置: bin/cryptopredict-1.0-debug.apk")
            
            # 检查文件是否存在
            if os.path.exists("bin/cryptopredict-1.0-debug.apk"):
                file_size = os.path.getsize("bin/cryptopredict-1.0-debug.apk") / (1024*1024)
                print(f"📊 APK文件大小: {file_size:.1f} MB")
            
        else:
            print("❌ APK构建失败")
            print("错误输出:", result.stderr)
            
    except subprocess.TimeoutExpired:
        print("⏰ 构建超时，请重试")
    except Exception as e:
        print(f"💥 构建出错: {e}")

def main():
    print("🚀 Replit一键APK构建")
    print("=" * 50)
    
    # 检查环境
    if not os.path.exists("main.py"):
        print("❌ 未找到main.py文件，请确保项目文件完整")
        return
    
    if not os.path.exists("buildozer.spec"):
        print("❌ 未找到buildozer.spec文件，请确保配置文件存在")
        return
    
    # 设置环境
    setup_environment()
    
    # 构建APK
    build_apk()
    
    print("=" * 50)
    print("🎉 构建流程完成！")

if __name__ == "__main__":
    main()
