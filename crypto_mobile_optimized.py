#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
加密货币预测移动应用 - 移动端优化版
支持弹窗提示和震动功能
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
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import platform

# 设置移动端窗口大小和属性
def setup_mobile_window():
    """设置移动端窗口属性"""
    if platform == 'android':
        # Android平台设置
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.VIBRATE, Permission.INTERNET])
    else:
        # 桌面端模拟手机屏幕
        Window.size = (360, 640)  # 模拟手机屏幕比例 9:16
    
    # 设置窗口属性
    Window.softinput_mode = "below_target"
    Window.keyboard_anim_args = {'d': 0.2, 't': 'in_out_expo'}

# 震动功能
def vibrate(duration=0.1):
    """震动功能"""
    try:
        if platform == 'android':
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            Context = autoclass('android.content.Context')
            activity = PythonActivity.mActivity
            vibrator = activity.getSystemService(Context.VIBRATOR_SERVICE)
            vibrator.vibrate(int(duration * 1000))
        else:
            # 桌面端模拟震动（打印提示）
            print(f"📳 震动 {duration}秒")
    except Exception as e:
        print(f"震动功能不可用: {e}")

# 弹窗提示类
class CustomPopup:
    @staticmethod
    def show_info(title, message, callback=None):
        """显示信息弹窗"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        # 消息文本
        msg_label = Label(
            text=message,
            text_size=(dp(280), None),
            halign='center',
            valign='middle',
            color=(1, 1, 1, 1)
        )
        
        # 确定按钮
        ok_btn = Button(
            text='确定',
            size_hint_y=None,
            height=dp(40),
            background_color=(0.2, 0.8, 0.2, 1)
        )
        
        content.add_widget(msg_label)
        content.add_widget(ok_btn)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        
        def on_ok(instance):
            popup.dismiss()
            vibrate(0.05)  # 轻微震动
            if callback:
                callback()
        
        ok_btn.bind(on_press=on_ok)
        popup.open()
        vibrate(0.1)  # 弹窗出现时震动
        
        return popup
    
    @staticmethod
    def show_confirm(title, message, on_yes=None, on_no=None):
        """显示确认弹窗"""
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        
        # 消息文本
        msg_label = Label(
            text=message,
            text_size=(dp(280), None),
            halign='center',
            valign='middle',
            color=(1, 1, 1, 1)
        )
        
        # 按钮布局
        btn_layout = BoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(40))
        
        # 取消按钮
        no_btn = Button(
            text='取消',
            background_color=(0.8, 0.3, 0.3, 1)
        )
        
        # 确定按钮
        yes_btn = Button(
            text='确定',
            background_color=(0.2, 0.8, 0.2, 1)
        )
        
        btn_layout.add_widget(no_btn)
        btn_layout.add_widget(yes_btn)
        
        content.add_widget(msg_label)
        content.add_widget(btn_layout)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        
        def on_yes_click(instance):
            popup.dismiss()
            vibrate(0.05)
            if on_yes:
                on_yes()
        
        def on_no_click(instance):
            popup.dismiss()
            vibrate(0.05)
            if on_no:
                on_no()
        
        yes_btn.bind(on_press=on_yes_click)
        no_btn.bind(on_press=on_no_click)
        popup.open()
        vibrate(0.1)
        
        return popup

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
        
        # 主布局 - 适配移动端
        main_layout = BoxLayout(
            orientation='vertical', 
            padding=[dp(20), dp(30), dp(20), dp(20)],  # 顶部留更多空间
            spacing=dp(15)
        )
        
        # 标题区域
        title_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120))
        
        title = Label(
            text='🚀 加密货币预测',
            font_size=dp(24),
            size_hint_y=None,
            height=dp(60),
            color=(1, 1, 1, 1),
            font_name='Chinese'
        )
        
        subtitle = Label(
            text='AI智能分析 • 移动端专版',
            font_size=dp(14),
            size_hint_y=None,
            height=dp(40),
            color=(0.8, 0.8, 0.8, 1),
            font_name='Chinese'
        )
        
        title_layout.add_widget(title)
        title_layout.add_widget(subtitle)
        
        # 按钮区域 - 移动端优化
        button_layout = BoxLayout(
            orientation='vertical', 
            spacing=dp(15),
            size_hint_y=None
        )
        button_layout.bind(minimum_height=button_layout.setter('height'))
        
        # BTC按钮 - 移动端尺寸
        btc_btn = Button(
            text='₿ BTC预测分析',
            size_hint_y=None,
            height=dp(60),
            background_color=(1, 0.6, 0, 1),
            font_size=dp(16),
            font_name='Chinese'
        )
        btc_btn.bind(on_press=self.go_to_btc)
        
        # ETH按钮
        eth_btn = Button(
            text='⟠ ETH预测分析',
            size_hint_y=None,
            height=dp(60),
            background_color=(0.4, 0.8, 1, 1),
            font_size=dp(16),
            font_name='Chinese'
        )
        eth_btn.bind(on_press=self.go_to_eth)
        
        # 设置按钮
        settings_btn = Button(
            text='⚙️ 设置',
            size_hint_y=None,
            height=dp(50),
            background_color=(0.6, 0.6, 0.6, 1),
            font_size=dp(14),
            font_name='Chinese'
        )
        settings_btn.bind(on_press=self.show_settings)
        
        # 测试按钮
        test_btn = Button(
            text='🔗 网络测试',
            size_hint_y=None,
            height=dp(50),
            background_color=(0.8, 0.4, 0.8, 1),
            font_size=dp(14),
            font_name='Chinese'
        )
        test_btn.bind(on_press=self.test_network)
        
        # 状态显示区域
        status_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80))
        
        self.status_label = Label(
            text='📱 移动端加密货币预测工具\n支持10分钟、30分钟、60分钟预测',
            size_hint_y=None,
            height=dp(60),
            color=(0.7, 0.9, 0.7, 1),
            halign='center',
            font_size=dp(12),
            font_name='Chinese'
        )
        
        status_layout.add_widget(self.status_label)
        
        # 添加组件到按钮布局
        button_layout.add_widget(btc_btn)
        button_layout.add_widget(eth_btn)
        button_layout.add_widget(settings_btn)
        button_layout.add_widget(test_btn)
        
        # 添加到主布局
        main_layout.add_widget(title_layout)
        main_layout.add_widget(button_layout)
        main_layout.add_widget(status_layout)
        
        self.add_widget(main_layout)
    
    def go_to_btc(self, instance):
        vibrate(0.05)  # 按钮点击震动
        self.manager.current = 'btc'
    
    def go_to_eth(self, instance):
        vibrate(0.05)
        self.manager.current = 'eth'
    
    def show_settings(self, instance):
        vibrate(0.05)
        CustomPopup.show_info(
            "设置", 
            "设置功能开发中...\n\n当前版本支持:\n• BTC/ETH预测\n• 实时价格获取\n• 凯莉公式建议"
        )
    
    def test_network(self, instance):
        vibrate(0.05)
        self.status_label.text = '🔄 正在测试网络连接...'
        Clock.schedule_once(self._test_network_async, 0.1)
    
    def _test_network_async(self, dt):
        try:
            response = requests.get('https://api.binance.com/api/v3/ping', timeout=5)
            if response.status_code == 200:
                self.status_label.text = '✅ 网络连接正常！'
                CustomPopup.show_info("网络测试", "✅ 网络连接正常！\n可以正常获取市场数据")
                vibrate(0.2)  # 成功震动
            else:
                self.status_label.text = f'❌ 网络连接异常: {response.status_code}'
                CustomPopup.show_info("网络测试", f"❌ 网络连接异常\n状态码: {response.status_code}")
        except Exception as e:
            error_msg = str(e)[:50] + "..." if len(str(e)) > 50 else str(e)
            self.status_label.text = f'❌ 连接失败: {error_msg}'
            CustomPopup.show_info("网络测试", f"❌ 连接失败\n错误信息: {error_msg}")
            vibrate(0.3)  # 错误震动

class PredictionScreen(Screen):
    def __init__(self, coin_type, **kwargs):
        super().__init__(**kwargs)
        self.coin_type = coin_type
        self.name = coin_type.lower()
        self.is_loading = False

        # 主布局 - 移动端优化
        main_layout = BoxLayout(
            orientation='vertical',
            padding=[dp(15), dp(10), dp(15), dp(10)],
            spacing=dp(8)
        )

        # 顶部导航栏 - 移动端样式
        top_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )

        # 返回按钮
        back_btn = Button(
            text='← 返回',
            size_hint_x=None,
            width=dp(70),
            background_color=(0.6, 0.6, 0.6, 1),
            font_size=dp(14),
            font_name='Chinese'
        )
        back_btn.bind(on_press=self.go_back)

        # 标题
        title = Label(
            text=f'{coin_type}价格预测',
            font_size=dp(18),
            color=(1, 1, 1, 1),
            font_name='Chinese'
        )

        # 预测按钮
        self.predict_btn = Button(
            text=f'🔄 分析',
            size_hint_x=None,
            width=dp(80),
            background_color=(0.2, 0.8, 0.2, 1),
            font_size=dp(14),
            font_name='Chinese'
        )
        self.predict_btn.bind(on_press=self.get_prediction)

        top_layout.add_widget(back_btn)
        top_layout.add_widget(title)
        top_layout.add_widget(self.predict_btn)

        # 滚动视图 - 移动端优化
        scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            scroll_type=['content']
        )

        # 结果显示区域
        self.result_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint_y=None,
            padding=[dp(5), 0, dp(5), 0]
        )
        self.result_layout.bind(minimum_height=self.result_layout.setter('height'))

        # 初始提示 - 移动端友好
        initial_label = Label(
            text=f'📊 点击"分析"开始{coin_type}预测\n\n功能特色:\n• 10分钟、30分钟、60分钟预测\n• 实时价格数据\n• 凯莉公式仓位建议\n• 智能震动提醒',
            size_hint_y=None,
            height=dp(120),
            color=(0.8, 0.8, 0.8, 1),
            halign='center',
            font_size=dp(12),
            font_name='Chinese'
        )
        self.result_layout.add_widget(initial_label)

        scroll.add_widget(self.result_layout)

        # 添加到主布局
        main_layout.add_widget(top_layout)
        main_layout.add_widget(scroll)

        self.add_widget(main_layout)

    def go_back(self, instance):
        vibrate(0.05)
        self.manager.current = 'main'

    def get_prediction(self, instance):
        if self.is_loading:
            return

        # 确认弹窗
        def start_analysis():
            self._start_prediction()

        CustomPopup.show_confirm(
            "开始分析",
            f"是否开始{self.coin_type}市场分析？\n\n将获取实时数据并进行AI预测",
            on_yes=start_analysis
        )

    def _start_prediction(self):
        self.is_loading = True
        self.predict_btn.text = '⏳ 分析中'
        self.predict_btn.disabled = True

        # 清空之前的结果
        self.result_layout.clear_widgets()

        # 显示加载状态 - 移动端优化
        loading_label = Label(
            text=f'🤖 正在分析{self.coin_type}市场趋势...\n📈 获取实时数据中\n⏰ 请稍候...',
            size_hint_y=None,
            height=dp(80),
            color=(1, 1, 0, 1),
            halign='center',
            font_size=dp(14),
            font_name='Chinese'
        )
        self.result_layout.add_widget(loading_label)

        # 震动提示开始分析
        vibrate(0.15)

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
                # 成功获取数据的震动
                vibrate(0.2)
            else:
                self.show_error(f"获取价格失败: HTTP {response.status_code}")

        except Exception as e:
            self.show_error(f"网络错误: {str(e)}")

    def _display_results(self, current_price):
        # 重置按钮
        self.predict_btn.text = '🔄 分析'
        self.predict_btn.disabled = False
        self.is_loading = False

        # 清空加载状态
        self.result_layout.clear_widgets()

        # 显示当前时间和价格 - 移动端布局
        current_time = datetime.now().strftime("%m-%d %H:%M")

        # 价格信息卡片
        price_card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(80))

        time_label = Label(
            text=f'📅 {current_time}',
            size_hint_y=None,
            height=dp(25),
            font_size=dp(12),
            color=(0.7, 0.7, 0.7, 1),
            font_name='Chinese'
        )

        price_label = Label(
            text=f'💰 {self.coin_type}: ${current_price:.2f}',
            size_hint_y=None,
            height=dp(40),
            font_size=dp(16),
            color=(0, 1, 0, 1),
            font_name='Chinese'
        )

        price_card.add_widget(time_label)
        price_card.add_widget(price_label)
        self.result_layout.add_widget(price_card)

        # 分隔线
        separator = Label(
            text='━' * 30,
            size_hint_y=None,
            height=dp(20),
            color=(0.5, 0.5, 0.5, 1),
            font_size=dp(10)
        )
        self.result_layout.add_widget(separator)

        # 预测结果标题
        title_label = Label(
            text='🤖 AI预测结果',
            size_hint_y=None,
            height=dp(35),
            font_size=dp(16),
            color=(1, 1, 1, 1),
            font_name='Chinese'
        )
        self.result_layout.add_widget(title_label)

        # 模拟预测结果 - 移动端优化显示
        predictions = [
            ("10分钟", "⬆️65% ⬇️35%", "上升", "95000-96000", "技术指标显示短期看涨"),
            ("30分钟", "⬆️55% ⬇️45%", "震荡", "94000-97000", "市场情绪谨慎，预期震荡"),
            ("60分钟", "⬆️45% ⬇️55%", "下跌", "92000-95000", "获利回吐压力增加")
        ]

        kelly_advice = ["做多📈 12.5%", "做多📈 8.5%", "做空📉 6.5%"]

        for i, ((period, prob, trend, target, reason), kelly) in enumerate(zip(predictions, kelly_advice)):
            # 预测卡片
            pred_card = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100))

            # 时间段和概率
            period_label = Label(
                text=f'{period}: {prob}',
                size_hint_y=None,
                height=dp(25),
                color=(1, 1, 1, 1),
                font_size=dp(13),
                font_name='Chinese'
            )

            # 趋势和目标价
            trend_label = Label(
                text=f'趋势: {trend} | 目标: {target}',
                size_hint_y=None,
                height=dp(25),
                color=(0.9, 0.9, 0.9, 1),
                font_size=dp(12),
                font_name='Chinese'
            )

            # 凯莉建议
            kelly_label = Label(
                text=f'仓位建议: {kelly}',
                size_hint_y=None,
                height=dp(25),
                color=(0.8, 1, 0.8, 1),
                font_size=dp(12),
                font_name='Chinese'
            )

            # 理由
            reason_label = Label(
                text=f'理由: {reason}',
                size_hint_y=None,
                height=dp(25),
                color=(0.8, 0.8, 0.8, 1),
                font_size=dp(11),
                font_name='Chinese'
            )

            pred_card.add_widget(period_label)
            pred_card.add_widget(trend_label)
            pred_card.add_widget(kelly_label)
            pred_card.add_widget(reason_label)

            self.result_layout.add_widget(pred_card)

            # 分隔线
            if i < len(predictions) - 1:
                mini_sep = Label(
                    text='- ' * 15,
                    size_hint_y=None,
                    height=dp(15),
                    color=(0.3, 0.3, 0.3, 1),
                    font_size=dp(8)
                )
                self.result_layout.add_widget(mini_sep)

        # 底部提示
        footer_label = Label(
            text='💡 仅供参考，投资有风险，决策需谨慎',
            size_hint_y=None,
            height=dp(40),
            color=(1, 0.8, 0.2, 1),
            font_size=dp(11),
            font_name='Chinese'
        )
        self.result_layout.add_widget(footer_label)

        # 显示完成提示
        CustomPopup.show_info("分析完成", f"✅ {self.coin_type}市场分析完成！\n\n已为您生成3个时间段的预测结果和仓位建议")

    def show_error(self, error_msg):
        # 重置按钮
        self.predict_btn.text = '🔄 分析'
        self.predict_btn.disabled = False
        self.is_loading = False

        # 显示错误
        self.result_layout.clear_widgets()
        error_label = Label(
            text=f'❌ {error_msg}\n\n请检查网络连接或稍后重试',
            size_hint_y=None,
            height=dp(80),
            color=(1, 0.3, 0.3, 1),
            halign='center',
            font_size=dp(12),
            font_name='Chinese'
        )
        self.result_layout.add_widget(error_label)

        # 错误震动和弹窗
        vibrate(0.3)
        CustomPopup.show_info("分析失败", f"❌ {error_msg}\n\n请检查网络连接后重试")

class CryptoPredictionApp(App):
    def build(self):
        self.title = '加密货币预测'

        # 设置移动端窗口
        setup_mobile_window()

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
