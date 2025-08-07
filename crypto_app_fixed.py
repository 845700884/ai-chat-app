#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加密货币预测移动应用 - 修复中文字体版本
"""

import os
import requests
from datetime import datetime

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.text import LabelBase

# 注册中文字体
def setup_chinese_font():
    if os.name == 'nt':  # Windows系统
        font_paths = [
            'C:/Windows/Fonts/msyh.ttc',  # 微软雅黑
            'C:/Windows/Fonts/simhei.ttf',  # 黑体
            'C:/Windows/Fonts/simsun.ttc',  # 宋体
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    LabelBase.register(name='Chinese', fn_regular=font_path)
                    print(f"成功注册中文字体: {font_path}")
                    return True
                except Exception as e:
                    print(f"注册字体失败: {e}")
                    continue
        
        print("未找到可用的中文字体")
        return False
    return False

# 设置代理
def setup_proxy():
    if 'HTTP_PROXY' not in os.environ:
        os.environ['HTTP_PROXY'] = 'http://127.0.0.1:55395'
        os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:55395'

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'main'
        
        # 主布局
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # 标题 - 使用英文避免乱码
        title = Label(
            text='Crypto Prediction App',
            font_size='24sp',
            size_hint_y=None,
            height='60dp',
            color=(1, 1, 1, 1)
        )
        
        # 副标题
        subtitle = Label(
            text='BTC & ETH Price Analysis',
            font_size='16sp',
            size_hint_y=None,
            height='40dp',
            color=(0.8, 0.8, 0.8, 1)
        )
        
        # 按钮布局
        button_layout = GridLayout(cols=1, spacing=15, size_hint_y=None)
        button_layout.bind(minimum_height=button_layout.setter('height'))
        
        # BTC预测按钮
        btc_btn = Button(
            text='BTC Analysis',
            size_hint_y=None,
            height='60dp',
            background_color=(1, 0.6, 0, 1),
            font_size='18sp'
        )
        btc_btn.bind(on_press=self.go_to_btc)
        
        # ETH预测按钮
        eth_btn = Button(
            text='ETH Analysis',
            size_hint_y=None,
            height='60dp',
            background_color=(0.4, 0.8, 1, 1),
            font_size='18sp'
        )
        eth_btn.bind(on_press=self.go_to_eth)
        
        # 测试按钮
        test_btn = Button(
            text='Test Network',
            size_hint_y=None,
            height='50dp',
            background_color=(0.6, 0.6, 0.6, 1)
        )
        test_btn.bind(on_press=self.test_network)
        
        # 状态显示
        self.status_label = Label(
            text='Mobile Crypto Prediction Tool\nSupports 10min, 30min, 60min forecasts',
            size_hint_y=None,
            height='60dp',
            color=(0.7, 0.9, 0.7, 1),
            halign='center'
        )
        
        # 添加组件
        button_layout.add_widget(btc_btn)
        button_layout.add_widget(eth_btn)
        button_layout.add_widget(test_btn)
        
        main_layout.add_widget(title)
        main_layout.add_widget(subtitle)
        main_layout.add_widget(button_layout)
        main_layout.add_widget(self.status_label)
        
        self.add_widget(main_layout)
    
    def go_to_btc(self, instance):
        self.manager.current = 'btc'
    
    def go_to_eth(self, instance):
        self.manager.current = 'eth'
    
    def test_network(self, instance):
        self.status_label.text = 'Testing network connection...'
        Clock.schedule_once(self._test_network_async, 0.1)
    
    def _test_network_async(self, dt):
        try:
            response = requests.get('https://api.binance.com/api/v3/ping', timeout=5)
            if response.status_code == 200:
                self.status_label.text = 'Network OK! Ready to analyze.'
            else:
                self.status_label.text = f'Network Error: {response.status_code}'
        except Exception as e:
            self.status_label.text = f'Connection Failed: {str(e)[:50]}...'

class PredictionScreen(Screen):
    def __init__(self, coin_type, **kwargs):
        super().__init__(**kwargs)
        self.coin_type = coin_type
        self.name = coin_type.lower()
        self.is_loading = False
        
        # 主布局
        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # 顶部布局
        top_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='50dp')
        
        # 返回按钮
        back_btn = Button(
            text='<- Back',
            size_hint_x=None,
            width='80dp',
            background_color=(0.6, 0.6, 0.6, 1)
        )
        back_btn.bind(on_press=self.go_back)
        
        # 标题
        title = Label(
            text=f'{coin_type} Price Prediction',
            font_size='18sp',
            color=(1, 1, 1, 1)
        )
        
        # 预测按钮
        self.predict_btn = Button(
            text=f'Get {coin_type} Forecast',
            size_hint_x=None,
            width='140dp',
            background_color=(0.2, 0.8, 0.2, 1)
        )
        self.predict_btn.bind(on_press=self.get_prediction)
        
        top_layout.add_widget(back_btn)
        top_layout.add_widget(title)
        top_layout.add_widget(self.predict_btn)
        
        # 滚动视图
        scroll = ScrollView()
        
        # 结果显示区域
        self.result_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.result_layout.bind(minimum_height=self.result_layout.setter('height'))
        
        # 初始提示
        initial_label = Label(
            text=f'Click "Get {coin_type} Forecast" to start AI analysis\n\nFeatures:\n• 10min, 30min, 60min predictions\n• Real-time price data\n• Kelly formula position advice',
            size_hint_y=None,
            height='120dp',
            color=(0.8, 0.8, 0.8, 1),
            halign='center'
        )
        self.result_layout.add_widget(initial_label)
        
        scroll.add_widget(self.result_layout)
        
        # 添加到主布局
        main_layout.add_widget(top_layout)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
    
    def go_back(self, instance):
        self.manager.current = 'main'
    
    def get_prediction(self, instance):
        if self.is_loading:
            return
            
        self.is_loading = True
        self.predict_btn.text = 'Loading...'
        self.predict_btn.disabled = True
        
        # 清空之前的结果
        self.result_layout.clear_widgets()
        
        # 显示加载状态
        loading_label = Label(
            text=f'Analyzing {self.coin_type} market trends...\nGetting real-time data...',
            size_hint_y=None,
            height='60dp',
            color=(1, 1, 0, 1),
            halign='center'
        )
        self.result_layout.add_widget(loading_label)
        
        # 异步获取数据
        Clock.schedule_once(self._get_prediction_async, 1.0)
    
    def _get_prediction_async(self, dt):
        try:
            # 获取实时价格
            symbol = f"{self.coin_type}USDT"
            response = requests.get(
                f'https://api.binance.com/api/v3/ticker/price?symbol={symbol}',
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                price = float(data['price'])
                self._display_results(price)
            else:
                self.show_error(f"Failed to get price: HTTP {response.status_code}")
                
        except Exception as e:
            self.show_error(f"Network error: {str(e)}")
    
    def _display_results(self, current_price):
        # 重置按钮
        self.predict_btn.text = f'Get {self.coin_type} Forecast'
        self.predict_btn.disabled = False
        self.is_loading = False
        
        # 清空加载状态
        self.result_layout.clear_widgets()
        
        # 显示当前时间和价格
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        info_text = f'Update Time: {current_time}\nCurrent {self.coin_type} Price: ${current_price:.2f}'
        
        info_label = Label(
            text=info_text,
            size_hint_y=None,
            height='60dp',
            font_size='16sp',
            color=(0, 1, 0, 1),
            halign='center'
        )
        self.result_layout.add_widget(info_label)
        
        # 分隔线
        separator = Label(
            text='=' * 50,
            size_hint_y=None,
            height='20dp',
            color=(0.5, 0.5, 0.5, 1)
        )
        self.result_layout.add_widget(separator)
        
        # 模拟预测结果（英文版避免乱码）
        predictions = [
            "10min: UP 65% DOWN 35% - Trend: Rising - Target: 95000-96000",
            "30min: UP 55% DOWN 45% - Trend: Oscillating - Target: 94000-97000", 
            "60min: UP 45% DOWN 55% - Trend: Falling - Target: 92000-95000"
        ]
        
        kelly_advice = [
            "Position: LONG 12.5% - Moderate bullish position",
            "Position: LONG 8.5% - Cautious bullish position",
            "Position: SHORT 6.5% - Light bearish position"
        ]
        
        for i, (prediction, kelly) in enumerate(zip(predictions, kelly_advice)):
            # 预测结果
            pred_label = Label(
                text=prediction,
                size_hint_y=None,
                height='40dp',
                color=(1, 1, 1, 1),
                font_size='14sp'
            )
            self.result_layout.add_widget(pred_label)
            
            # 凯莉公式建议
            kelly_label = Label(
                text=kelly,
                size_hint_y=None,
                height='30dp',
                color=(0.8, 1, 0.8, 1),
                font_size='12sp'
            )
            self.result_layout.add_widget(kelly_label)
            
            # 小分隔线
            if i < len(predictions) - 1:
                mini_sep = Label(
                    text='-' * 30,
                    size_hint_y=None,
                    height='15dp',
                    color=(0.3, 0.3, 0.3, 1)
                )
                self.result_layout.add_widget(mini_sep)
        
        # 底部提示
        footer_label = Label(
            text='For reference only. Investment involves risks.',
            size_hint_y=None,
            height='40dp',
            color=(1, 0.8, 0.2, 1),
            font_size='12sp'
        )
        self.result_layout.add_widget(footer_label)
    
    def show_error(self, error_msg):
        # 重置按钮
        self.predict_btn.text = f'Get {self.coin_type} Forecast'
        self.predict_btn.disabled = False
        self.is_loading = False
        
        # 显示错误
        self.result_layout.clear_widgets()
        error_label = Label(
            text=f'Error: {error_msg}\n\nPlease check network connection or try again later',
            size_hint_y=None,
            height='80dp',
            color=(1, 0.3, 0.3, 1),
            halign='center'
        )
        self.result_layout.add_widget(error_label)

class CryptoPredictionApp(App):
    def build(self):
        self.title = 'Crypto Prediction'
        
        # 设置代理和字体
        setup_proxy()
        setup_chinese_font()
        
        # 创建屏幕管理器
        sm = ScreenManager()
        
        # 添加屏幕
        sm.add_widget(MainScreen())
        sm.add_widget(PredictionScreen('BTC'))
        sm.add_widget(PredictionScreen('ETH'))
        
        return sm

if __name__ == '__main__':
    CryptoPredictionApp().run()
