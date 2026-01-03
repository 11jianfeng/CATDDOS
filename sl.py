#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python版本的sl命令模拟器
模拟蒸汽火车穿过终端屏幕的动画效果
"""

import os
import sys
import time
import random
import shutil
from typing import List

class SteamLocomotive:
    def __init__(self):
        self.width, self.height = shutil.get_terminal_size()
        self.position = self.width
        self.speed = 0.2  # 动画速度
        
        # 火车车厢设计
        self.locomotive = [
            "      ====        ________                ___________",
            "  _D _|  |_______/        \\__I_I_____===__|_________|",
            "   |(_)---  |   H\\________/ |   |        =|___ ___|  ",
            "   /     |  |   H  |  |     |   |         ||_| |_||  ",
            "  |      |  |   H  |__--------------------| [___] |  ",
            "  | ________|___H__/__|_____/[][]~\\_______|       |  ",
            "  |/ |   |-----------I_____I [][] []  D   |=======|_ ",
        ]
        
        self.carriage = [
            "  ___/|  |\\__/  |  |  |  |  |  |  |  |  |  |  |  |  |",
            " |_____|_/__\\___|__|__|__|__|__|__|__|__|__|__|__|  ",
            "  |   |   |   |   |   |   |   |   |   |   |   |   |  ",
            "  |___|___|___|___|___|___|___|___|___|___|___|___|  ",
        ]
        
        self.wheels = ["○", "◔", "◑", "◕", "●"]
        self.wheel_index = 0
        
    def clear_screen(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_wheel(self):
        """获取旋转的车轮"""
        wheel = self.wheels[self.wheel_index]
        self.wheel_index = (self.wheel_index + 1) % len(self.wheels)
        return wheel
    
    def draw_train(self, offset):
        """绘制火车"""
        output = []
        
        # 绘制机车
        for i, line in enumerate(self.locomotive):
            # 替换车轮字符
            line = line.replace("D", self.get_wheel())
            line = line.replace("○", self.get_wheel())
            
            # 添加偏移
            if offset < len(line):
                visible_part = line[max(0, -offset):]
                if visible_part:
                    output.append(" " * max(0, offset) + visible_part)
        
        # 绘制车厢
        for i, line in enumerate(self.carriage):
            # 添加偏移
            if offset < len(line) + 20:  # 20是机车和车厢的间距
                carriage_offset = offset - 20
                if carriage_offset < len(line):
                    visible_part = line[max(0, -carriage_offset):]
                    if visible_part:
                        output.append(" " * max(0, carriage_offset) + visible_part)
        
        return output
    
    def draw_smoke(self, offset):
        """绘制烟雾效果"""
        smoke_patterns = [
            "    (  ) (  ) (  )   ",
            "   (    ) (    )     ",
            "  (       )          ",
            " (                  )",
        ]
        
        smoke_output = []
        for i, pattern in enumerate(smoke_patterns):
            smoke_offset = offset - 10 - i * 3
            if smoke_offset < len(pattern):
                visible_part = pattern[max(0, -smoke_offset):]
                if visible_part:
                    smoke_output.append(" " * max(0, smoke_offset) + visible_part)
        
        return smoke_output
    
    def animate(self):
        """运行动画"""
        try:
            self.clear_screen()
            
            while self.position > -100:  # 火车完全离开屏幕
                self.clear_screen()
                
                # 绘制烟雾
                smoke_lines = self.draw_smoke(self.position)
                for line in smoke_lines:
                    print(line)
                
                # 绘制火车
                train_lines = self.draw_train(self.position)
                for line in train_lines:
                    print(line)
                
                # 绘制轨道
                track_offset = max(0, self.position - 30)
                track = "═" * (self.width - track_offset)
                print(" " * track_offset + track)
                
                # 移动位置
                self.position -= 2
                
                # 控制速度
                time.sleep(self.speed)
                
        except KeyboardInterrupt:
            print("\n\n火车到站了！欢迎乘坐Python蒸汽火车！")
    
    def run(self):
        """运行sl命令"""
        print("Python蒸汽火车即将发车...")
        time.sleep(1)
        self.animate()

def main():
    """主函数"""
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print("用法: python sl.py [选项]")
            print("选项:")
            print("  -h, --help     显示帮助信息")
            print("  -a             显示意外情况（这个版本暂不支持）")
            print("  -l             显示小火车")
            return
        elif sys.argv[1] == '-l':
            # 小版本模式
            print("小型火车版本开发中...")
            return
    
    # 创建并运行火车动画
    train = SteamLocomotive()
    train.run()

if __name__ == "__main__":
    main()
