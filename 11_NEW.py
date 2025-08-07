import sys
import json
import requests
import threading
import re
import os
import time
from datetime import datetime, timedelta

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
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QTextEdit, QLineEdit, QPushButton, 
                            QLabel, QComboBox, QProgressBar, QMessageBox,
                            QStackedWidget, QSplitter)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QFont, QIcon, QTextCursor


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
    def get_price_change(symbol):

        try:
            url = f"{BINANCE_API['base_url']}/api/v3/ticker/24hr"
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
                price_change_percent = float(data['priceChangePercent'])
                last_price = float(data['lastPrice'])
                return price_change_percent, last_price
            else:
                return None, None
        except Exception as e:
            print(f"获取价格变动出错: {str(e)}")
            return None, None
    
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

class WorkerSignals(QObject):

    error = pyqtSignal(str, int)  
    result = pyqtSignal(str, int)  
    finished = pyqtSignal()  

class Worker(QObject):

    def __init__(self, coin_type="BTC"):
        super().__init__()
        self.coin_type = coin_type
        self.signals = WorkerSignals()
        
    def run(self):

        max_retries = 2
        retry_count = 0
        index = 0 if self.coin_type == "BTC" else 1
        
        while retry_count <= max_retries:
            try:

                symbol = f"{self.coin_type}USDT"

                market_data = BinanceAPI.get_price_summary(symbol, interval='1m', limit=1440)
                market_info = ""
                
                if market_data:
                    market_info = f"""
最新价格: {market_data['latest_price']:.2f} USDT
3小时价格变动: {market_data['price_change_percent']:.2f}%
最高价: {market_data['highest_price']:.2f} USDT
最低价: {market_data['lowest_price']:.2f} USDT
波动性: {market_data['volatility_percent']:.2f}%
平均成交量: {market_data['avg_volume']:.2f}
数据范围: {market_data['start_time']} 至 {market_data['end_time']}
"""
                

                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f"Bearer {API_CONFIG['token']}"
                }
                

                prompt = ""
                if self.coin_type == "BTC":
                    prompt = f"""Analyze the current BTC price trend and predict price trends for the next 10 minutes, 30 minutes, and 60 minutes.

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
                else:
                    prompt = f"""Analyze the current ETH price trend and predict price trends for the next 10 minutes, 30 minutes, and 60 minutes.

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
                
                data = {
                    'model': DEFAULT_MODEL['id'],
                    'messages': [{'role': 'user', 'content': prompt}],
                    'temperature': DEFAULT_MODEL['temperature'],
                    'stream': False
                }
                

                session = requests.Session()

                # 设置代理（如果环境变量中有的话）
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
                
                if response.status_code != 200:
                    error_text = f"API错误: HTTP状态码 {response.status_code}"

                    try:
                        error_data = response.json()
                        if 'error' in error_data and 'message' in error_data['error']:
                            error_text += f" - {error_data['error']['message']}"
                    except:
                        pass
                        
                    if retry_count < max_retries:
                        retry_count += 1
                        continue
                    self.signals.error.emit(error_text, index)
                    break
                
                result = response.json()
                prediction = result['choices'][0]['message']['content']
                

                prediction = re.sub(r'<[^>]*>', '', prediction)  # 移除开始标签
                prediction = re.sub(r'</[^>]*>', '', prediction)  # 移除结束标签
                

                lines = prediction.strip().split('\n')
                cleaned_prediction = ""
                
                for line in lines:
                    if any(period in line for period in ["10分钟", "30分钟", "60分钟"]) and any(symbol in line for symbol in ["⬆️", "⬇️"]):
                        cleaned_prediction += line + "\n"
                
                self.signals.result.emit(cleaned_prediction, index)
                break  
                
            except requests.exceptions.ProxyError as e:
                if retry_count < max_retries:
                    retry_count += 1
                    continue
                self.signals.error.emit(f"代理服务器错误: 请检查您的网络代理设置或关闭代理。详细信息: {str(e)}", index)
                break
            except requests.exceptions.ConnectionError as e:
                if retry_count < max_retries:
                    retry_count += 1
                    continue
                self.signals.error.emit(f"连接错误: 无法连接到API服务器。请检查您的网络连接或API服务器地址是否正确。详细信息: {str(e)}", index)
                break
            except requests.exceptions.Timeout as e:
                if retry_count < max_retries:
                    retry_count += 1
                    continue
                self.signals.error.emit(f"请求超时: 服务器响应时间过长。请稍后再试。详细信息: {str(e)}", index)
                break
            except requests.exceptions.RequestException as e:
                if retry_count < max_retries:
                    retry_count += 1
                    continue
                error_detail = str(e)
                self.signals.error.emit(f"网络请求错误: {error_detail}", index)
                break
            except json.JSONDecodeError as e:
                self.signals.error.emit(f"JSON解析错误: 服务器返回了无效的JSON格式。详细信息: {str(e)}", index)
                break
            except Exception as e:
                error_detail = str(e)
                self.signals.error.emit(f"处理错误: {error_detail}", index)
                break
        
        self.signals.finished.emit()

class PredictionWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):

        self.setWindowTitle('加密货币趋势预测')
        self.setGeometry(100, 100, 1200, 600)  # 增加窗口宽度以适应左右布局
        
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        

        main_layout = QVBoxLayout(central_widget)
        

        title_layout = QHBoxLayout()
        

        btc_title = QLabel("BTC预测")
        btc_title.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        btc_title.setAlignment(Qt.AlignCenter)
        

        eth_title = QLabel("ETH预测")
        eth_title.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        eth_title.setAlignment(Qt.AlignCenter)
        

        title_layout.addWidget(btc_title)
        title_layout.addWidget(eth_title)
        

        self.splitter = QSplitter(Qt.Horizontal)
        

        self.btc_page = QTextEdit()
        self.btc_page.setReadOnly(True)
        self.btc_page.setFont(QFont("Microsoft YaHei", 10))
        

        self.eth_page = QTextEdit()
        self.eth_page.setReadOnly(True)
        self.eth_page.setFont(QFont("Microsoft YaHei", 10))
        

        self.splitter.addWidget(self.btc_page)
        self.splitter.addWidget(self.eth_page)
        self.splitter.setSizes([600, 600]) 
        

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximumHeight(5)
        self.progress_bar.hide()
        

        bottom_controls = QHBoxLayout()
        

        self.btc_button = QPushButton("BTC预测")
        self.btc_button.setMinimumHeight(50)
        self.btc_button.clicked.connect(self.predict_btc)
        

        self.eth_button = QPushButton("ETH预测")
        self.eth_button.setMinimumHeight(50)
        self.eth_button.clicked.connect(self.predict_eth)
        

        bottom_controls.addWidget(self.btc_button)
        bottom_controls.addWidget(self.eth_button)
        

        main_layout.addLayout(title_layout)
        main_layout.addWidget(self.splitter, 7)
        main_layout.addWidget(self.progress_bar)
        main_layout.addLayout(bottom_controls, 1)
        

        self.btc_page.append('点击下方"BTC预测"按钮获取预测结果')
        self.eth_page.append('点击下方"ETH预测"按钮获取预测结果')
    
    def show_error(self, error_msg, index=0):

        if index == 0:
            current_page = self.btc_page
        else:
            current_page = self.eth_page
        
        current_page.append(f"发生错误: {error_msg}")
        self.api_request_finished(index)

    def api_request_started(self, index=0):


        if index == 0:
            self.btc_button.setEnabled(False)
        else:
            self.eth_button.setEnabled(False)
        

        self.progress_bar.show()
        self.progress_bar.setRange(0, 0)  # 设置为无限进度条

    def api_request_finished(self, index=0):


        if index == 0:
            self.btc_button.setEnabled(True)
        else:
            self.eth_button.setEnabled(True)
            
        self.progress_bar.hide()
        self.progress_bar.setRange(0, 100)  # 恢复正常进度条
        
    def scroll_to_bottom(self, index=0):

        if index == 0:
            current_page = self.btc_page
        else:
            current_page = self.eth_page
            
        current_page.verticalScrollBar().setValue(
            current_page.verticalScrollBar().maximum()
        )

    def calculate_kelly(self, win_probability, win_amount=0.8, loss_amount=1.0):

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
    
    def extract_probability(self, prediction_line):


        up_pattern = r'⬆️(\d+)%'
        up_match = re.search(up_pattern, prediction_line)
        
        if up_match:
            up_probability = float(up_match.group(1)) / 100
            return up_probability
        
        return None
    
    def extract_trend(self, prediction_line):

        trend_pattern = r'趋势: ([^\s-]+)'
        trend_match = re.search(trend_pattern, prediction_line)
        
        if trend_match:
            return trend_match.group(1)
        
        return None
    
    def extract_target_price(self, prediction_line):

        price_pattern = r'目标价: ([0-9-]+)'
        price_match = re.search(price_pattern, prediction_line)
        
        if price_match:
            return price_match.group(1)
        
        return None
    
    def get_kelly_recommendation(self, prediction_line):

        up_probability = self.extract_probability(prediction_line)
        
        if up_probability is None:
            return "【仓位: 无法计算】"
        

        time_pattern = r'(\d+分钟)'
        time_match = re.search(time_pattern, prediction_line)
        time_period = time_match.group(1) if time_match else "当前时间段"
        

        trend = self.extract_trend(prediction_line)
        target_price = self.extract_target_price(prediction_line)
        

        long_kelly = self.calculate_kelly(up_probability)
        short_kelly = self.calculate_kelly(1 - up_probability)
        

        if long_kelly > short_kelly:
            direction = "做多📈"
            kelly = long_kelly
            action_text = "买入看涨"
            win_probability = up_probability
        else:
            direction = "做空📉"
            kelly = short_kelly
            action_text = "买入看跌"
            win_probability = 1 - up_probability
        

        if kelly < 0.01:
            return f"【{time_period}仓位: 不建议交易❌ - 胜率太低】\n  理由: 预测胜率不足，风险大于收益。"
        

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
        

        reason = ""
        if trend:
            if direction == "做多📈":
                if trend == "上升":
                    reason = f"理由: 上涨概率{win_percent:.0f}%且趋势{trend}，信号一致看涨"
                elif trend == "震荡":
                    reason = f"理由: 上涨概率{win_percent:.0f}%较高，虽趋势{trend}，仍有上行机会"
                else:  # 下跌
                    reason = f"理由: 上涨概率{win_percent:.0f}%高于下跌，但趋势{trend}，建议谨慎"
            else:  # 做空
                if trend == "下跌":
                    reason = f"理由: 下跌概率{win_percent:.0f}%且趋势{trend}，信号一致看跌"
                elif trend == "震荡":
                    reason = f"理由: 下跌概率{win_percent:.0f}%较高，虽趋势{trend}，仍有下行风险"
                else:  # 上升
                    reason = f"理由: 下跌概率{win_percent:.0f}%高于上涨，但趋势{trend}，建议谨慎"
        else:
            reason = f"理由: {direction.replace('📈', '').replace('📉', '')}胜率{win_percent:.0f}%"
            
        if target_price:
            reason += f"，目标价位{target_price}"
        

        recommendation = f"【{time_period}仓位: {direction} {kelly_percent:.1f}% {strength}】\n"
        recommendation += f"  建议: {confidence}{action_text}，资金比例{kelly_percent:.1f}%\n"
        recommendation += f"  {reason}"
        
        return recommendation

    def predict_btc(self):


        self.btc_page.clear()
        

        self.api_request_started(0)
        

        self.btc_page.append("正在分析BTC趋势，请稍候...")
        

        self.btc_thread = QThread()
        self.btc_worker = Worker(coin_type="BTC")
        self.btc_worker.moveToThread(self.btc_thread)
        

        self.btc_thread.started.connect(self.btc_worker.run)
        self.btc_worker.signals.error.connect(lambda error_msg: self.show_error(error_msg, 0))
        self.btc_worker.signals.result.connect(lambda result: self.display_btc_prediction(result))
        self.btc_worker.signals.finished.connect(self.btc_thread.quit)
        self.btc_worker.signals.finished.connect(self.btc_worker.deleteLater)
        self.btc_thread.finished.connect(self.btc_thread.deleteLater)
        self.btc_thread.finished.connect(lambda: self.api_request_finished(0))
        

        self.btc_thread.start()

    def predict_eth(self):
        """ETH预测功能"""

        self.eth_page.clear()
        

        self.api_request_started(1)
        

        self.eth_page.append("正在分析ETH趋势，请稍候...")
        

        self.eth_thread = QThread()
        self.eth_worker = Worker(coin_type="ETH")
        self.eth_worker.moveToThread(self.eth_thread)
        

        self.eth_thread.started.connect(self.eth_worker.run)
        self.eth_worker.signals.error.connect(lambda error_msg: self.show_error(error_msg, 1))
        self.eth_worker.signals.result.connect(lambda result: self.display_eth_prediction(result))
        self.eth_worker.signals.finished.connect(self.eth_thread.quit)
        self.eth_worker.signals.finished.connect(self.eth_worker.deleteLater)
        self.eth_thread.finished.connect(self.eth_thread.deleteLater)
        self.eth_thread.finished.connect(lambda: self.api_request_finished(1))
        

        self.eth_thread.start()

    def display_btc_prediction(self, prediction, index=0):
        """显示BTC预测结果"""

        self.btc_page.clear()
        

        price_change, latest_price = BinanceAPI.get_price_change("BTCUSDT")
        

        if latest_price is None:
            latest_price = BinanceAPI.get_latest_price("BTCUSDT")
            price_change = None
        

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.btc_page.append(f"更新时间: {current_time}")
        

        if latest_price:
            self.btc_page.append(f"当前BTC价格: {latest_price:.2f} USDT")
        

        self.btc_page.append("BTC价格趋势预测")
        self.btc_page.append("") 
        
 
        self.btc_page.append("【凯莉公式仓位推荐】对应各时间段合约，盈亏比为 胜:赚0.8倍，负:亏1倍")
        self.btc_page.append("") 
        

        lines = prediction.strip().split('\n')
        for line in lines:
            if line.strip():

                kelly_recommendation = self.get_kelly_recommendation(line)
                

                self.btc_page.append(line)
                

                self.btc_page.append(kelly_recommendation)
                self.btc_page.append("")  
        

        periods = {"10分钟", "30分钟", "60分钟"}
        found_periods = set()
        
        for line in lines:
            for period in periods:
                if period in line:
                    found_periods.add(period)
        
        missing_periods = periods - found_periods
        for period in missing_periods:
            self.btc_page.append(f"{period}: 分析中...")
            self.btc_page.append("")  #
        

        self.btc_page.verticalScrollBar().setValue(0)

    def display_eth_prediction(self, prediction, index=1):


        self.eth_page.clear()
        

        price_change, latest_price = BinanceAPI.get_price_change("ETHUSDT")
        

        if latest_price is None:
            latest_price = BinanceAPI.get_latest_price("ETHUSDT")
            price_change = None
        

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.eth_page.append(f"更新时间: {current_time}")
        

        if latest_price:
            self.eth_page.append(f"当前ETH价格: {latest_price:.2f} USDT")
        

        self.eth_page.append("ETH价格趋势预测")
        self.eth_page.append("")  # 添加空行
        

        self.eth_page.append("【凯莉公式仓位推荐】对应各时间段合约，盈亏比为 胜:赚0.8倍，负:亏1倍")
        self.eth_page.append("")  # 添加空行
        

        lines = prediction.strip().split('\n')
        for line in lines:
            if line.strip():

                kelly_recommendation = self.get_kelly_recommendation(line)
                

                self.eth_page.append(line)
                

                self.eth_page.append(kelly_recommendation)
                self.eth_page.append("")  # 添加空行分隔
        

        periods = {"10分钟", "30分钟", "60分钟"}
        found_periods = set()
        
        for line in lines:
            for period in periods:
                if period in line:
                    found_periods.add(period)
        
        missing_periods = periods - found_periods
        for period in missing_periods:
            self.eth_page.append(f"{period}: 分析中...")
            self.eth_page.append("")  # 添加空行分隔
        

        self.eth_page.verticalScrollBar().setValue(0)

def main():
    app = QApplication(sys.argv)
    window = PredictionWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 