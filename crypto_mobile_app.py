#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加密货币预测移动应用 - 完整版
基于原有11_NEW.py的核心功能
"""

import sys
import json
import requests
import threading
import re
import os
import time
from datetime import datetime, timedelta

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.uix.progressbar import ProgressBar
from kivy.core.text import LabelBase
from kivy.resources import resource_add_path

# 注册中文字体
import os
if os.name == 'nt':  # Windows系统
    # 尝试使用系统中文字体
    font_paths = [
        'C:/Windows/Fonts/msyh.ttc',  # 微软雅黑
        'C:/Windows/Fonts/simhei.ttf',  # 黑体
        'C:/Windows/Fonts/simsun.ttc',  # 宋体
    ]

    for font_path in font_paths:
        if os.path.exists(font_path):
            LabelBase.register(name='Chinese', fn_regular=font_path)
            break
    else:
        print("未找到中文字体，可能显示乱码")

# 代理自动修复
def fix_proxy_settings():
    """自动修复代理设置，解决协议不匹配问题"""
    try:
        from urllib.request import getproxies
        proxies = getproxies()

        # 修复HTTPS代理协议
        if 'https' in proxies and proxies['https'].startswith('https://'):
            fixed_proxy = proxies['https'].replace('https://', 'http://')
            os.environ['HTTP_PROXY'] = fixed_proxy
            os.environ['HTTPS_PROXY'] = fixed_proxy
            print(f"代理已修复: {fixed_proxy}")
        elif 'https' in proxies and proxies['https'].startswith('http://'):
            os.environ['HTTP_PROXY'] = proxies['https']
            os.environ['HTTPS_PROXY'] = proxies['https']
            print(f"代理已设置: {proxies['https']}")
    except Exception as e:
        print(f"代理修复失败: {e}")

# 执行代理修复
fix_proxy_settings()

# API配置
API_CONFIG = {
    'base_url': 'https://chrisapi.cn/v1',
    'token': 'sk-MF2gXIIF6eA8bjcBIciuwHMv7uNeJfbHEKdQu6WamvrWP0FH',
}

BINANCE_API = {
    'base_url': 'https://api.binance.com',
}

DEFAULT_MODEL = {
    'id': 'grok-4',
    'name': 'grok-4',
    'temperature': 0.7
}

class BinanceAPI:
    @staticmethod
    def get_klines(symbol, interval='1m', limit=180):
        try:
            url = f"{BINANCE_API['base_url']}/api/v3/klines"
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            session = requests.Session()

            # 设置代理（如果环境变量中有的话）
            if 'HTTP_PROXY' in os.environ:
                session.proxies = {
                    'http': os.environ['HTTP_PROXY'],
                    'https': os.environ['HTTPS_PROXY']
                }

            response = session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                klines = response.json()
                processed_data = []
                for k in klines:
                    processed_data.append({
                        'open_time': datetime.fromtimestamp(k[0]/1000).strftime('%Y-%m-%d %H:%M'),
                        'open': float(k[1]),
                        'high': float(k[2]),
                        'low': float(k[3]),
                        'close': float(k[4]),
                        'volume': float(k[5]),
                    })
                return processed_data
            else:
                return None
        except Exception as e:
            print(f"获取币安数据出错: {str(e)}")
            return None
    
    @staticmethod
    def get_latest_price(symbol):
        try:
            url = f"{BINANCE_API['base_url']}/api/v3/ticker/price"
            params = {'symbol': symbol}
            session = requests.Session()

            # 设置代理（如果环境变量中有的话）
            if 'HTTP_PROXY' in os.environ:
                session.proxies = {
                    'http': os.environ['HTTP_PROXY'],
                    'https': os.environ['HTTPS_PROXY']
                }

            response = session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return float(data['price'])
            else:
                return None
        except Exception as e:
            print(f"获取最新价格出错: {str(e)}")
            return None
    
    @staticmethod
    def get_price_summary(symbol, interval='1m', limit=180):
        klines = BinanceAPI.get_klines(symbol, interval, limit)
        if not klines:
            return None
        
        latest_price = klines[-1]['close']
        highest_price = max([k['high'] for k in klines])
        lowest_price = min([k['low'] for k in klines])
        
        avg_volume = sum([k['volume'] for k in klines]) / len(klines)
        
        price_change = (klines[-1]['close'] - klines[0]['open']) / klines[0]['open'] * 100
        
        prices = [k['close'] for k in klines]
        mean = sum(prices) / len(prices)
        variance = sum([(p - mean) ** 2 for p in prices]) / len(prices)
        volatility = (variance ** 0.5) / mean * 100
        
        return {
            'symbol': symbol,
            'latest_price': latest_price,
            'highest_price': highest_price,
            'lowest_price': lowest_price,
            'price_change_percent': price_change,
            'volatility_percent': volatility,
            'avg_volume': avg_volume,
            'start_time': klines[0]['open_time'],
            'end_time': klines[-1]['open_time'],
            'data_points': len(klines)
        }

class KellyCalculator:
    @staticmethod
    def calculate_kelly(win_probability, win_amount=0.8, loss_amount=1.0):
        if isinstance(win_probability, str):
            win_probability = float(win_probability.strip('%')) / 100
        
        if win_probability <= 0:
            return 0
            
        b = win_amount  
        p = win_probability
        q = 1 - p
        
        kelly_fraction = (b * p - q) / b
        
        if kelly_fraction <= 0:
            return 0
            
        half_kelly = kelly_fraction / 2
        
        return half_kelly
    
    @staticmethod
    def extract_probability(prediction_line):
        up_pattern = r'⬆️(\d+)%'
        up_match = re.search(up_pattern, prediction_line)
        
        if up_match:
            up_probability = float(up_match.group(1)) / 100
            return up_probability
        
        return None
    
    @staticmethod
    def get_kelly_recommendation(prediction_line):
        up_probability = KellyCalculator.extract_probability(prediction_line)
        
        if up_probability is None:
            return "【仓位: 无法计算】"
        
        time_pattern = r'(\d+分钟)'
        time_match = re.search(time_pattern, prediction_line)
        time_period = time_match.group(1) if time_match else "当前时间段"
        
        long_kelly = KellyCalculator.calculate_kelly(up_probability)
        short_kelly = KellyCalculator.calculate_kelly(1 - up_probability)
        
        if long_kelly > short_kelly:
            direction = "做多📈"
            kelly = long_kelly
            win_probability = up_probability
        else:
            direction = "做空📉"
            kelly = short_kelly
            win_probability = 1 - up_probability
        
        if kelly < 0.01:
            return f"【{time_period}仓位: 不建议交易❌】\n理由: 预测胜率不足，风险大于收益。"
        
        if kelly > 0.2: 
            strength = "💰💰💰"
            confidence = "强烈建议"
        elif kelly > 0.1: 
            strength = "💰💰"
            confidence = "适量建仓"
        else: 
            strength = "💰"
            confidence = "谨慎小仓"
        
        kelly_percent = kelly * 100
        win_percent = win_probability * 100
        
        recommendation = f"【{time_period}仓位: {direction} {kelly_percent:.1f}% {strength}】\n"
        recommendation += f"建议: {confidence}，资金比例{kelly_percent:.1f}%"
        
        return recommendation

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'main'
        
        # 主布局
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 标题
        title = Label(
            text='🚀 加密货币趋势预测',
            font_size='28sp',
            size_hint_y=None,
            height='80dp',
            color=(1, 1, 1, 1),
            bold=True,
            font_name='Chinese'
        )

        # 副标题
        subtitle = Label(
            text='AI智能分析 • 凯莉公式仓位建议',
            font_size='16sp',
            size_hint_y=None,
            height='40dp',
            color=(0.8, 0.8, 0.8, 1),
            font_name='Chinese'
        )
        
        # 按钮布局
        button_layout = GridLayout(cols=1, spacing=15, size_hint_y=None)
        button_layout.bind(minimum_height=button_layout.setter('height'))
        
        # BTC预测按钮
        btc_btn = Button(
            text='₿ BTC预测分析',
            size_hint_y=None,
            height='70dp',
            background_color=(1, 0.6, 0, 1),
            font_size='18sp'
        )
        btc_btn.bind(on_press=self.go_to_btc)
        
        # ETH预测按钮
        eth_btn = Button(
            text='⟠ ETH预测分析',
            size_hint_y=None,
            height='70dp',
            background_color=(0.4, 0.8, 1, 1),
            font_size='18sp'
        )
        eth_btn.bind(on_press=self.go_to_eth)
        
        # 状态显示
        self.status_label = Label(
            text='📱 移动端加密货币预测工具\n支持10分钟、30分钟、60分钟预测',
            size_hint_y=None,
            height='60dp',
            color=(0.7, 0.9, 0.7, 1),
            halign='center'
        )
        
        # 添加组件
        button_layout.add_widget(btc_btn)
        button_layout.add_widget(eth_btn)
        
        main_layout.add_widget(title)
        main_layout.add_widget(subtitle)
        main_layout.add_widget(button_layout)
        main_layout.add_widget(self.status_label)
        
        self.add_widget(main_layout)
    
    def go_to_btc(self, instance):
        self.manager.current = 'btc'
    
    def go_to_eth(self, instance):
        self.manager.current = 'eth'

class PredictionScreen(Screen):
    def __init__(self, coin_type, **kwargs):
        super().__init__(**kwargs)
        self.coin_type = coin_type
        self.name = coin_type.lower()
        self.is_loading = False

        # 主布局
        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        # 顶部布局
        top_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='60dp', spacing=10)

        # 返回按钮
        back_btn = Button(
            text='← 返回',
            size_hint_x=None,
            width='80dp',
            background_color=(0.6, 0.6, 0.6, 1)
        )
        back_btn.bind(on_press=self.go_back)

        # 标题
        title = Label(
            text=f'{coin_type}价格预测',
            font_size='20sp',
            color=(1, 1, 1, 1),
            bold=True
        )

        # 预测按钮
        self.predict_btn = Button(
            text=f'🔄 获取{coin_type}预测',
            size_hint_x=None,
            width='140dp',
            background_color=(0.2, 0.8, 0.2, 1)
        )
        self.predict_btn.bind(on_press=self.get_prediction)

        top_layout.add_widget(back_btn)
        top_layout.add_widget(title)
        top_layout.add_widget(self.predict_btn)

        # 进度条
        self.progress_bar = ProgressBar(
            max=100,
            size_hint_y=None,
            height='8dp'
        )
        self.progress_bar.opacity = 0

        # 滚动视图
        scroll = ScrollView()

        # 结果显示区域
        self.result_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.result_layout.bind(minimum_height=self.result_layout.setter('height'))

        # 初始提示
        initial_label = Label(
            text=f'📊 点击"获取{coin_type}预测"开始AI分析\n\n将为您提供：\n• 10分钟、30分钟、60分钟预测\n• 实时价格数据\n• 凯莉公式仓位建议',
            size_hint_y=None,
            height='120dp',
            color=(0.8, 0.8, 0.8, 1),
            halign='center'
        )
        self.result_layout.add_widget(initial_label)

        scroll.add_widget(self.result_layout)

        # 添加到主布局
        main_layout.add_widget(top_layout)
        main_layout.add_widget(self.progress_bar)
        main_layout.add_widget(scroll)

        self.add_widget(main_layout)

    def go_back(self, instance):
        self.manager.current = 'main'

    def get_prediction(self, instance):
        if self.is_loading:
            return

        self.is_loading = True
        self.predict_btn.text = '⏳ 分析中...'
        self.predict_btn.disabled = True

        # 显示进度条
        self.progress_bar.opacity = 1
        self.progress_bar.value = 0

        # 清空之前的结果
        self.result_layout.clear_widgets()

        # 显示加载状态
        loading_label = Label(
            text=f'🤖 正在分析{self.coin_type}市场趋势...\n📈 获取实时数据中',
            size_hint_y=None,
            height='60dp',
            color=(1, 1, 0, 1),
            halign='center'
        )
        self.result_layout.add_widget(loading_label)

        # 启动进度条动画
        self.progress_event = Clock.schedule_interval(self.update_progress, 0.1)

        # 异步获取数据
        Clock.schedule_once(self._get_prediction_async, 0.5)

    def update_progress(self, dt):
        if self.progress_bar.value < 90:
            self.progress_bar.value += 2
        return True

    def _get_prediction_async(self, dt):
        try:
            # 第一步：获取市场数据
            symbol = f"{self.coin_type}USDT"
            market_data = BinanceAPI.get_price_summary(symbol, interval='1m', limit=1440)

            if not market_data:
                self.show_error("无法获取市场数据，请检查网络连接")
                return

            # 更新进度
            self.progress_bar.value = 30

            # 第二步：调用AI预测API
            prediction_result = self._call_ai_prediction(market_data)

            if not prediction_result:
                self.show_error("AI预测服务暂时不可用")
                return

            # 完成进度
            self.progress_bar.value = 100

            # 显示结果
            Clock.schedule_once(lambda dt: self._display_results(market_data, prediction_result), 0.5)

        except Exception as e:
            self.show_error(f"分析过程出错: {str(e)}")

    def _call_ai_prediction(self, market_data):
        try:
            # 构建市场信息
            market_info = f"""
最新价格: {market_data['latest_price']:.2f} USDT
3小时价格变动: {market_data['price_change_percent']:.2f}%
最高价: {market_data['highest_price']:.2f} USDT
最低价: {market_data['lowest_price']:.2f} USDT
波动性: {market_data['volatility_percent']:.2f}%
平均成交量: {market_data['avg_volume']:.2f}
数据范围: {market_data['start_time']} 至 {market_data['end_time']}
"""

            # 构建提示词
            prompt = f"""Analyze the current {self.coin_type} price trend and predict price trends for the next 10 minutes, 30 minutes, and 60 minutes.

Below is market data from the past 16 hours:
{market_info}

Please conduct a comprehensive analysis combining the real-time price data provided by the API and your existing cryptocurrency market knowledge. Consider current market sentiment, technical indicators, and possible macroeconomic factors.

For each time period (10 minutes, 30 minutes, 60 minutes), provide:
1. Probability of rise and fall (percentage)
2. Overall trend classification: "Oscillating", "Rising", or "Falling"
3. Target price prediction (approximate price level that may be reached)
4. Brief reason for prediction (one sentence explaining the basis for your prediction)

Keep responses concise, one line per time period.
Use these emojis to indicate rise and fall: ⬆️ ⬇️

Format example:
10 minutes: ⬆️/⬇️x% ⬆️/⬇️x% - Trend: Rising - Target price: a-b - Reason: Brief summary of your thinking process and results
30 minutes: ⬆️/⬇️x% ⬆️/⬇️x% - Trend: Oscillating - Target price: a-b - Reason: Brief summary of your thinking process and results
60 minutes: ⬆️/⬇️x% ⬆️/⬇️x% - Trend: Falling - Target price: a-b - Reason: Brief summary of your thinking process and results

Important note: Reply should not use any HTML tags, only plain text. Reply must be in Chinese. Do not add explanations or other content, strictly output three lines of prediction results according to the format."""

            # 调用API
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f"Bearer {API_CONFIG['token']}"
            }

            data = {
                'model': DEFAULT_MODEL['id'],
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': DEFAULT_MODEL['temperature'],
                'stream': False
            }

            session = requests.Session()
            if 'HTTP_PROXY' in os.environ:
                session.proxies = {
                    'http': os.environ['HTTP_PROXY'],
                    'https': os.environ['HTTPS_PROXY']
                }

            response = session.post(
                f"{API_CONFIG['base_url']}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                prediction = result['choices'][0]['message']['content']

                # 清理HTML标签
                prediction = re.sub(r'<[^>]*>', '', prediction)

                # 过滤有效预测行
                lines = prediction.strip().split('\n')
                cleaned_prediction = ""

                for line in lines:
                    if any(period in line for period in ["10分钟", "30分钟", "60分钟"]) and any(symbol in line for symbol in ["⬆️", "⬇️"]):
                        cleaned_prediction += line + "\n"

                return cleaned_prediction.strip()
            else:
                return None

        except Exception as e:
            print(f"AI预测调用失败: {str(e)}")
            return None

    def _display_results(self, market_data, prediction_result):
        # 停止进度条
        if hasattr(self, 'progress_event'):
            self.progress_event.cancel()
        self.progress_bar.opacity = 0

        # 重置按钮
        self.predict_btn.text = f'🔄 获取{self.coin_type}预测'
        self.predict_btn.disabled = False
        self.is_loading = False

        # 清空加载状态
        self.result_layout.clear_widgets()

        # 显示当前时间
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        time_label = Label(
            text=f'📅 更新时间: {current_time}',
            size_hint_y=None,
            height='30dp',
            color=(0.7, 0.7, 0.7, 1),
            font_size='14sp'
        )
        self.result_layout.add_widget(time_label)

        # 显示价格信息
        price_info = f'💰 当前{self.coin_type}价格: ${market_data["latest_price"]:.2f}\n📊 24h变动: {market_data["price_change_percent"]:.2f}%'
        price_label = Label(
            text=price_info,
            size_hint_y=None,
            height='60dp',
            font_size='16sp',
            color=(0, 1, 0, 1) if market_data["price_change_percent"] > 0 else (1, 0.3, 0.3, 1),
            halign='center'
        )
        self.result_layout.add_widget(price_label)

        # 分隔线
        separator = Label(
            text='━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━',
            size_hint_y=None,
            height='20dp',
            color=(0.5, 0.5, 0.5, 1)
        )
        self.result_layout.add_widget(separator)

        # 标题
        title_label = Label(
            text='🤖 AI预测分析结果',
            size_hint_y=None,
            height='40dp',
            font_size='18sp',
            color=(1, 1, 1, 1),
            bold=True
        )
        self.result_layout.add_widget(title_label)

        # 显示预测结果
        if prediction_result:
            lines = prediction_result.strip().split('\n')
            for line in lines:
                if line.strip():
                    # 预测结果
                    pred_label = Label(
                        text=line,
                        size_hint_y=None,
                        height='50dp',
                        text_size=(None, None),
                        halign='left',
                        color=(1, 1, 1, 1),
                        font_size='14sp'
                    )
                    self.result_layout.add_widget(pred_label)

                    # 凯莉公式建议
                    kelly_recommendation = KellyCalculator.get_kelly_recommendation(line)
                    kelly_label = Label(
                        text=kelly_recommendation,
                        size_hint_y=None,
                        height='60dp',
                        color=(0.8, 1, 0.8, 1),
                        font_size='13sp',
                        halign='left'
                    )
                    self.result_layout.add_widget(kelly_label)

                    # 小分隔线
                    mini_sep = Label(
                        text='- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -',
                        size_hint_y=None,
                        height='15dp',
                        color=(0.3, 0.3, 0.3, 1),
                        font_size='10sp'
                    )
                    self.result_layout.add_widget(mini_sep)
        else:
            # 显示模拟数据（如果API调用失败）
            self._show_demo_results()

        # 底部提示
        footer_label = Label(
            text='💡 仅供参考，投资有风险，决策需谨慎',
            size_hint_y=None,
            height='40dp',
            color=(1, 0.8, 0.2, 1),
            font_size='12sp'
        )
        self.result_layout.add_widget(footer_label)

    def _show_demo_results(self):
        """显示演示数据"""
        demo_predictions = [
            f"10分钟: ⬆️65% ⬇️35% - 趋势: 上升 - 目标价: 95000-96000 - 理由: 技术指标显示{self.coin_type}短期看涨",
            f"30分钟: ⬆️55% ⬇️45% - 趋势: 震荡 - 目标价: 94000-97000 - 理由: 市场情绪谨慎，预期震荡整理",
            f"60分钟: ⬆️45% ⬇️55% - 趋势: 下跌 - 目标价: 92000-95000 - 理由: 获利回吐压力增加"
        ]

        for line in demo_predictions:
            # 预测结果
            pred_label = Label(
                text=line,
                size_hint_y=None,
                height='50dp',
                color=(0.9, 0.9, 0.9, 1),
                font_size='14sp'
            )
            self.result_layout.add_widget(pred_label)

            # 凯莉公式建议
            kelly_recommendation = KellyCalculator.get_kelly_recommendation(line)
            kelly_label = Label(
                text=kelly_recommendation,
                size_hint_y=None,
                height='60dp',
                color=(0.7, 0.9, 0.7, 1),
                font_size='13sp'
            )
            self.result_layout.add_widget(kelly_label)

    def show_error(self, error_msg):
        # 停止进度条
        if hasattr(self, 'progress_event'):
            self.progress_event.cancel()
        self.progress_bar.opacity = 0

        # 重置按钮
        self.predict_btn.text = f'🔄 获取{self.coin_type}预测'
        self.predict_btn.disabled = False
        self.is_loading = False

        # 显示错误
        self.result_layout.clear_widgets()
        error_label = Label(
            text=f'❌ {error_msg}\n\n请检查网络连接或稍后重试',
            size_hint_y=None,
            height='80dp',
            color=(1, 0.3, 0.3, 1),
            halign='center'
        )
        self.result_layout.add_widget(error_label)

class CryptoPredictionApp(App):
    def build(self):
        self.title = '加密货币预测'

        # 设置代理（如果需要）
        if 'HTTP_PROXY' not in os.environ:
            os.environ['HTTP_PROXY'] = 'http://127.0.0.1:55395'
            os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:55395'

        # 创建屏幕管理器
        sm = ScreenManager()

        # 添加屏幕
        sm.add_widget(MainScreen())
        sm.add_widget(PredictionScreen('BTC'))
        sm.add_widget(PredictionScreen('ETH'))

        return sm

if __name__ == '__main__':
    CryptoPredictionApp().run()
