#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
移动应用测试版本 - 验证所有功能
"""

import os
from crypto_mobile_optimized import CryptoPredictionApp

def test_app():
    """测试应用功能"""
    print("🚀 启动加密货币预测移动应用...")
    print("📱 窗口大小: 360x640 (模拟手机屏幕)")
    print("🔔 支持弹窗提示")
    print("📳 支持震动反馈 (桌面端为模拟)")
    print("🌐 支持网络请求")
    print("💰 支持实时价格获取")
    print("🤖 支持AI预测分析")
    print("📊 支持凯莉公式建议")
    print("\n" + "="*50)
    print("测试功能:")
    print("1. 点击'网络测试'验证网络连接")
    print("2. 点击'BTC预测分析'测试BTC功能")
    print("3. 点击'ETH预测分析'测试ETH功能")
    print("4. 观察弹窗提示和震动反馈")
    print("="*50 + "\n")
    
    # 启动应用
    app = CryptoPredictionApp()
    app.run()

if __name__ == '__main__':
    test_app()
