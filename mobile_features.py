#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
移动端功能增强模块
提供震动、通知、声音等移动端特性
"""

from kivy.utils import platform
from kivy.logger import Logger

class MobileFeatures:
    """移动端功能管理器"""
    
    def __init__(self):
        self.platform = platform
        self.vibrator_available = False
        self.notification_available = False
        self.audio_available = False
        
        self._init_features()
    
    def _init_features(self):
        """初始化移动端功能"""
        try:
            if self.platform == 'android':
                # Android平台初始化
                self._init_android_features()
            else:
                # 桌面端模拟
                Logger.info("MobileFeatures: 运行在桌面端，使用模拟功能")
        except Exception as e:
            Logger.error(f"MobileFeatures: 初始化失败 - {e}")
    
    def _init_android_features(self):
        """初始化Android功能"""
        try:
            # 请求权限
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.VIBRATE,
                Permission.INTERNET,
                Permission.WAKE_LOCK,
                Permission.WRITE_EXTERNAL_STORAGE
            ])
            
            # 初始化震动
            from jnius import autoclass
            self.PythonActivity = autoclass('org.kivy.android.PythonActivity')
            self.Context = autoclass('android.content.Context')
            self.vibrator_available = True
            
            # 初始化通知
            try:
                from plyer import notification
                self.notification_available = True
            except ImportError:
                Logger.warning("MobileFeatures: plyer不可用，通知功能禁用")
            
            Logger.info("MobileFeatures: Android功能初始化完成")
            
        except Exception as e:
            Logger.error(f"MobileFeatures: Android初始化失败 - {e}")
    
    def vibrate(self, duration=0.1, pattern=None):
        """
        震动功能
        
        Args:
            duration: 震动时长（秒）
            pattern: 震动模式 [停止, 震动, 停止, 震动, ...]
        """
        try:
            if self.platform == 'android' and self.vibrator_available:
                activity = self.PythonActivity.mActivity
                vibrator = activity.getSystemService(self.Context.VIBRATOR_SERVICE)
                
                if pattern:
                    # 使用震动模式
                    pattern_ms = [int(x * 1000) for x in pattern]
                    vibrator.vibrate(pattern_ms, -1)
                else:
                    # 简单震动
                    vibrator.vibrate(int(duration * 1000))
                    
                Logger.info(f"MobileFeatures: 震动 {duration}秒")
            else:
                # 桌面端模拟
                print(f"📳 震动 {duration}秒")
                
        except Exception as e:
            Logger.error(f"MobileFeatures: 震动失败 - {e}")
    
    def show_notification(self, title, message, timeout=10):
        """
        显示系统通知
        
        Args:
            title: 通知标题
            message: 通知内容
            timeout: 显示时长（秒）
        """
        try:
            if self.notification_available:
                from plyer import notification
                notification.notify(
                    title=title,
                    message=message,
                    timeout=timeout,
                    app_name="AI聊天助手"
                )
                Logger.info(f"MobileFeatures: 显示通知 - {title}")
            else:
                # 桌面端模拟
                print(f"🔔 通知: {title} - {message}")
                
        except Exception as e:
            Logger.error(f"MobileFeatures: 通知失败 - {e}")
    
    def play_sound(self, sound_type="default"):
        """
        播放提示音
        
        Args:
            sound_type: 声音类型 (default, success, error, warning)
        """
        try:
            if self.platform == 'android':
                # Android系统声音
                from jnius import autoclass
                MediaPlayer = autoclass('android.media.MediaPlayer')
                RingtoneManager = autoclass('android.media.RingtoneManager')
                
                # 获取系统提示音
                if sound_type == "success":
                    sound_uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION)
                elif sound_type == "error":
                    sound_uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)
                else:
                    sound_uri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION)
                
                # 播放声音
                ringtone = RingtoneManager.getRingtone(
                    self.PythonActivity.mActivity, sound_uri
                )
                ringtone.play()
                
                Logger.info(f"MobileFeatures: 播放声音 - {sound_type}")
            else:
                # 桌面端模拟
                print(f"🔊 播放声音: {sound_type}")
                
        except Exception as e:
            Logger.error(f"MobileFeatures: 播放声音失败 - {e}")
    
    def keep_screen_on(self, keep_on=True):
        """
        保持屏幕常亮
        
        Args:
            keep_on: True=保持常亮, False=允许息屏
        """
        try:
            if self.platform == 'android':
                from jnius import autoclass
                WindowManager = autoclass('android.view.WindowManager$LayoutParams')
                activity = self.PythonActivity.mActivity
                
                if keep_on:
                    activity.getWindow().addFlags(WindowManager.FLAG_KEEP_SCREEN_ON)
                    Logger.info("MobileFeatures: 屏幕保持常亮")
                else:
                    activity.getWindow().clearFlags(WindowManager.FLAG_KEEP_SCREEN_ON)
                    Logger.info("MobileFeatures: 允许屏幕息屏")
            else:
                print(f"💡 屏幕常亮: {'开启' if keep_on else '关闭'}")
                
        except Exception as e:
            Logger.error(f"MobileFeatures: 屏幕常亮设置失败 - {e}")
    
    def get_device_info(self):
        """获取设备信息"""
        info = {
            'platform': self.platform,
            'vibrator_available': self.vibrator_available,
            'notification_available': self.notification_available,
            'audio_available': self.audio_available
        }
        
        try:
            if self.platform == 'android':
                from jnius import autoclass
                Build = autoclass('android.os.Build')
                info.update({
                    'device_model': Build.MODEL,
                    'android_version': Build.VERSION.RELEASE,
                    'manufacturer': Build.MANUFACTURER
                })
        except Exception as e:
            Logger.error(f"MobileFeatures: 获取设备信息失败 - {e}")
        
        return info

# 全局移动功能实例
mobile_features = MobileFeatures()

# 便捷函数
def vibrate(duration=0.1, pattern=None):
    """震动"""
    mobile_features.vibrate(duration, pattern)

def notify(title, message, timeout=10):
    """通知"""
    mobile_features.show_notification(title, message, timeout)

def play_sound(sound_type="default"):
    """播放声音"""
    mobile_features.play_sound(sound_type)

def keep_screen_on(keep_on=True):
    """屏幕常亮"""
    mobile_features.keep_screen_on(keep_on)
