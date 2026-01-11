#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实时时钟程序 - 每秒刷新显示当前时间
作者：AI Assistant
功能：在终端中显示实时更新的数字时钟
"""

import time
import sys
import os
from datetime import datetime

class DigitalClock:
    def __init__(self):
        self.running = True
        self.format_type = 1  # 1: 24小时制, 2: 12小时制
        
    def clear_screen(self):
        """清屏函数"""
        if os.name == 'nt':  # Windows
            os.system('cls')
        else:  # Linux/Mac/Termux
            os.system('clear')
    
    def get_time_string(self, time_format=1):
        """获取格式化的时间字符串"""
        now = datetime.now()
        
        if time_format == 1:  # 24小时制
            return now.strftime("%H:%M:%S")
        else:  # 12小时制
            return now.strftime("%I:%M:%S %p")
    
    def display_clock(self):
        """显示时钟界面"""
        self.clear_screen()
        
        # 获取当前时间
        current_time = self.get_time_string(self.format_type)
        current_date = datetime.now().strftime("%Y年%m月%d日")
        weekday = datetime.now().strftime("%A")
        
        # 星期中文映射
        weekday_cn = {
            'Monday': '星期一',
            'Tuesday': '星期二', 
            'Wednesday': '星期三',
            'Thursday': '星期四',
            'Friday': '星期五',
            'Saturday': '星期六',
            'Sunday': '星期日'
        }
        
        # 创建时钟显示界面
        clock_display = f"""
╔══════════════════════════════════════╗
║            数字时钟                  ║
╠══════════════════════════════════════╣
║                                      ║
║         {current_time}            ║
║                                      ║
║    {current_date}    ║
║         {weekday_cn.get(weekday, weekday)}           ║
║                                      ║
╚══════════════════════════════════════╝

按 Ctrl+C 退出 | 按 'f' 切换时间格式 | 按 'q' 退出
"""
        
        print(clock_display)
    
    def run(self):
        """运行时钟"""
        print("正在启动实时时钟...")
        time.sleep(1)
        
        try:
            while self.running:
                self.display_clock()
                
                # 检测键盘输入（非阻塞）
                if os.name != 'nt':  # Unix-like系统
                    import select
                    import termios
                    import tty
                    
                    # 设置非阻塞输入
                    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                        key = sys.stdin.read(1)
                        if key.lower() == 'q':
                            self.running = False
                            print("\n时钟已关闭。")
                        elif key.lower() == 'f':
                            self.format_type = 2 if self.format_type == 1 else 1
                else:  # Windows系统
                    if msvcrt.kbhit():
                        key = msvcrt.getch().decode('utf-8').lower()
                        if key == 'q':
                            self.running = False
                            print("\n时钟已关闭。")
                        elif key == 'f':
                            self.format_type = 2 if self.format_type == 1 else 1
                
                time.sleep(1)  # 每秒更新
                
        except KeyboardInterrupt:
            print("\n\n时钟已关闭。")
        except Exception as e:
            print(f"\n发生错误: {e}")

# Windows系统需要导入msvcrt模块
if os.name == 'nt':
    import msvcrt

def main():
    """主函数"""
    print("=" * 50)
    print("        实时数字时钟程序")
    print("=" * 50)
    print("功能说明：")
    print("- 每秒自动更新时间显示")
    print("- 按 'f' 键切换 12/24 小时制")
    print("- 按 'q' 键或 Ctrl+C 退出程序")
    print("-" * 50)
    
    input("按回车键开始运行时钟...")
    
    clock = DigitalClock()
    clock.run()

if __name__ == "__main__":
    main()
