#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加密货币预测应用 - Kivy版本测试
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import requests
import os

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'main'
        
        # 主布局
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # 标题
        title = Label(
            text='加密货币趋势预测',
            font_size='24sp',
            size_hint_y=None,
            height='60dp',
            color=(1, 1, 1, 1)
        )
        
        # 按钮布局
        button_layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        button_layout.bind(minimum_height=button_layout.setter('height'))
        
        # BTC预测按钮
        btc_btn = Button(
            text='BTC预测',
            size_hint_y=None,
            height='60dp',
            background_color=(0.2, 0.6, 1, 1)
        )
        btc_btn.bind(on_press=self.go_to_btc)
        
        # ETH预测按钮
        eth_btn = Button(
            text='ETH预测',
            size_hint_y=None,
            height='60dp',
            background_color=(0.4, 0.8, 0.4, 1)
        )
        eth_btn.bind(on_press=self.go_to_eth)
        
        # 测试网络按钮
        test_btn = Button(
            text='测试网络连接',
            size_hint_y=None,
            height='60dp',
            background_color=(1, 0.6, 0.2, 1)
        )
        test_btn.bind(on_press=self.test_network)
        
        # 状态显示
        self.status_label = Label(
            text='欢迎使用加密货币预测应用！',
            size_hint_y=None,
            height='40dp',
            color=(0.8, 0.8, 0.8, 1)
        )
        
        # 添加组件
        button_layout.add_widget(btc_btn)
        button_layout.add_widget(eth_btn)
        button_layout.add_widget(test_btn)
        
        main_layout.add_widget(title)
        main_layout.add_widget(button_layout)
        main_layout.add_widget(self.status_label)
        
        self.add_widget(main_layout)
    
    def go_to_btc(self, instance):
        self.manager.current = 'btc'
    
    def go_to_eth(self, instance):
        self.manager.current = 'eth'
    
    def test_network(self, instance):
        self.status_label.text = '正在测试网络连接...'
        Clock.schedule_once(self._test_network_async, 0.1)
    
    def _test_network_async(self, dt):
        try:
            # 测试币安API连接
            response = requests.get('https://api.binance.com/api/v3/ping', timeout=5)
            if response.status_code == 200:
                self.status_label.text = '✅ 网络连接正常！'
            else:
                self.status_label.text = f'❌ 网络连接异常: {response.status_code}'
        except Exception as e:
            self.status_label.text = f'❌ 网络连接失败: {str(e)}'

class PredictionScreen(Screen):
    def __init__(self, coin_type, **kwargs):
        super().__init__(**kwargs)
        self.coin_type = coin_type
        self.name = coin_type.lower()
        
        # 主布局
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # 顶部布局
        top_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height='60dp')
        
        # 返回按钮
        back_btn = Button(
            text='← 返回',
            size_hint_x=None,
            width='100dp',
            background_color=(0.6, 0.6, 0.6, 1)
        )
        back_btn.bind(on_press=self.go_back)
        
        # 标题
        title = Label(
            text=f'{coin_type}价格预测',
            font_size='20sp',
            color=(1, 1, 1, 1)
        )
        
        # 预测按钮
        predict_btn = Button(
            text=f'获取{coin_type}预测',
            size_hint_x=None,
            width='150dp',
            background_color=(0.2, 0.8, 0.2, 1)
        )
        predict_btn.bind(on_press=self.get_prediction)
        
        top_layout.add_widget(back_btn)
        top_layout.add_widget(title)
        top_layout.add_widget(predict_btn)
        
        # 滚动视图
        scroll = ScrollView()
        
        # 结果显示区域
        self.result_layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.result_layout.bind(minimum_height=self.result_layout.setter('height'))
        
        # 初始提示
        initial_label = Label(
            text=f'点击"获取{coin_type}预测"按钮开始分析',
            size_hint_y=None,
            height='40dp',
            color=(0.8, 0.8, 0.8, 1)
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
        # 清空之前的结果
        self.result_layout.clear_widgets()
        
        # 显示加载状态
        loading_label = Label(
            text=f'正在分析{self.coin_type}趋势，请稍候...',
            size_hint_y=None,
            height='40dp',
            color=(1, 1, 0, 1)
        )
        self.result_layout.add_widget(loading_label)
        
        # 异步获取数据
        Clock.schedule_once(self._get_prediction_async, 0.1)
    
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
                
                # 清空加载状态
                self.result_layout.clear_widgets()
                
                # 显示价格信息
                price_label = Label(
                    text=f'当前{self.coin_type}价格: ${price:.2f}',
                    size_hint_y=None,
                    height='50dp',
                    font_size='18sp',
                    color=(0, 1, 0, 1)
                )
                self.result_layout.add_widget(price_label)
                
                # 模拟预测结果
                predictions = [
                    "10分钟: ⬆️65% ⬇️35% - 趋势: 上升 - 目标价: 95000-96000 - 理由: 技术指标显示短期看涨",
                    "30分钟: ⬆️55% ⬇️45% - 趋势: 震荡 - 目标价: 94000-97000 - 理由: 市场情绪谨慎，预期震荡整理",
                    "60分钟: ⬆️45% ⬇️55% - 趋势: 下跌 - 目标价: 92000-95000 - 理由: 获利回吐压力增加"
                ]
                
                for i, prediction in enumerate(predictions):
                    pred_label = Label(
                        text=prediction,
                        size_hint_y=None,
                        height='60dp',
                        text_size=(None, None),
                        halign='left',
                        color=(1, 1, 1, 1)
                    )
                    self.result_layout.add_widget(pred_label)
                    
                    # 添加凯莉公式建议
                    kelly_text = f"【{['10分钟', '30分钟', '60分钟'][i]}仓位: 做多📈 12.5%】\n  建议: 适量建仓买入看涨，资金比例12.5%"
                    kelly_label = Label(
                        text=kelly_text,
                        size_hint_y=None,
                        height='50dp',
                        color=(0.8, 1, 0.8, 1)
                    )
                    self.result_layout.add_widget(kelly_label)
                
            else:
                self.show_error(f"获取价格失败: HTTP {response.status_code}")
                
        except Exception as e:
            self.show_error(f"网络错误: {str(e)}")
    
    def show_error(self, error_msg):
        self.result_layout.clear_widgets()
        error_label = Label(
            text=f'❌ {error_msg}',
            size_hint_y=None,
            height='40dp',
            color=(1, 0, 0, 1)
        )
        self.result_layout.add_widget(error_label)

class CryptoPredictionApp(App):
    def build(self):
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
