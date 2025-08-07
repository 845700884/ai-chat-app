#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
APK构建脚本 - 使用python-for-android
"""

import os
import subprocess
import sys

def install_p4a():
    """安装python-for-android"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-for-android"])
        print("✅ python-for-android 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ python-for-android 安装失败: {e}")
        return False

def build_apk():
    """构建APK"""
    try:
        # p4a命令
        cmd = [
            "p4a", "apk",
            "--private", ".",
            "--package", "com.crypto.predict",
            "--name", "CryptoPredict",
            "--version", "1.0",
            "--bootstrap", "sdl2",
            "--requirements", "python3,kivy,requests",
            "--permission", "INTERNET",
            "--permission", "VIBRATE",
            "--arch", "arm64-v8a",
            "--release"
        ]
        
        print("🔨 开始构建APK...")
        subprocess.check_call(cmd)
        print("✅ APK构建成功！")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ APK构建失败: {e}")
        return False

def main():
    print("🚀 开始APK构建流程...")
    
    # 检查是否在Linux/macOS环境
    if os.name == 'nt':
        print("⚠️  警告: Windows环境可能不支持直接构建APK")
        print("建议使用以下方案:")
        print("1. 使用WSL (Windows Subsystem for Linux)")
        print("2. 使用Docker")
        print("3. 使用GitHub Actions")
        return
    
    # 安装依赖
    if not install_p4a():
        return
    
    # 构建APK
    if build_apk():
        print("🎉 APK构建完成！")
        print("📱 APK文件位置: ./dist/")
    else:
        print("💥 构建失败，请检查错误信息")

if __name__ == "__main__":
    main()
