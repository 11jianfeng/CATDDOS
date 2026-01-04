#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2048游戏 - 完整版
包含得分、计时和成绩记录功能
"""

import os
import sys
import time
import json
import random
import datetime
from typing import List, Optional, Tuple

class Game2048:
    def __init__(self, size: int = 4):
        self.size = size
        self.grid = [[0 for _ in range(size)] for _ in range(size)]
        self.score = 0
        self.start_time = time.time()
        self.best_score = 0
        self.game_time = 0
        self.load_best_score()
        
    def load_best_score(self) -> None:
        """加载最佳成绩"""
        try:
            if os.path.exists('2048_scores.json'):
                with open('2048_scores.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.best_score = data.get('best_score', 0)
        except:
            self.best_score = 0
    
    def save_best_score(self) -> None:
        """保存最佳成绩"""
        try:
            data = {
                'best_score': max(self.score, self.best_score),
                'last_played': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'last_score': self.score,
                'last_time': self.game_time
            }
            with open('2048_scores.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def add_random_tile(self) -> None:
        """在空位置添加一个新的数字方块"""
        empty_cells = [(i, j) for i in range(self.size) for j in range(self.size) if self.grid[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.grid[i][j] = 4 if random.random() < 0.1 else 2
    
    def init_game(self) -> None:
        """初始化游戏"""
        self.grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.score = 0
        self.start_time = time.time()
        self.add_random_tile()
        self.add_random_tile()
    
    def print_grid(self) -> None:
        """打印游戏界面"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # 计算游戏时间
        current_time = time.time()
        self.game_time = int(current_time - self.start_time)
        minutes = self.game_time // 60
        seconds = self.game_time % 60
        
        print("=" * 40)
        print(f"🎮 2048游戏")
        print("=" * 40)
        print(f"当前得分: {self.score:6d}  |  最佳成绩: {self.best_score:6d}")
        print(f"游戏时间: {minutes:02d}:{seconds:02d}")
        print("=" * 40)
        
        # 打印游戏网格
        for row in self.grid:
            print("+------" * self.size + "+")
            print("|", end="")
            for cell in row:
                if cell == 0:
                    print("      |", end="")
                else:
                    print(f"{cell:^6}|", end="")
            print()
        print("+------" * self.size + "+")
        
        print("\n操作说明:")
        print("W/↑ - 上")
        print("S/↓ - 下") 
        print("A/← - 左")
        print("D/→ - 右")
        print("Q - 退出游戏")
        print("R - 重新开始")
    
    def move_left(self) -> bool:
        """向左移动"""
        moved = False
        for i in range(self.size):
            # 提取非零元素
            row = [x for x in self.grid[i] if x != 0]
            # 合并相同数字
            merged_row = []
            j = 0
            while j < len(row):
                if j < len(row) - 1 and row[j] == row[j + 1]:
                    merged_row.append(row[j] * 2)
                    self.score += row[j] * 2
                    j += 2
                else:
                    merged_row.append(row[j])
                    j += 1
            # 补零
            merged_row += [0] * (self.size - len(merged_row))
            # 检查是否移动
            if self.grid[i] != merged_row:
                moved = True
            self.grid[i] = merged_row
        return moved
    
    def move_right(self) -> bool:
        """向右移动"""
        moved = False
        for i in range(self.size):
            # 提取非零元素
            row = [x for x in self.grid[i] if x != 0]
            # 合并相同数字
            merged_row = []
            j = len(row) - 1
            while j >= 0:
                if j > 0 and row[j] == row[j - 1]:
                    merged_row.insert(0, row[j] * 2)
                    self.score += row[j] * 2
                    j -= 2
                else:
                    merged_row.insert(0, row[j])
                    j -= 1
            # 补零
            merged_row = [0] * (self.size - len(merged_row)) + merged_row
            # 检查是否移动
            if self.grid[i] != merged_row:
                moved = True
            self.grid[i] = merged_row
        return moved
    
    def transpose(self) -> None:
        """转置矩阵"""
        self.grid = [[self.grid[j][i] for j in range(self.size)] for i in range(self.size)]
    
    def move_up(self) -> bool:
        """向上移动"""
        self.transpose()
        moved = self.move_left()
        self.transpose()
        return moved
    
    def move_down(self) -> bool:
        """向下移动"""
        self.transpose()
        moved = self.move_right()
        self.transpose()
        return moved
    
    def can_move(self) -> bool:
        """检查是否还能移动"""
        # 检查空位置
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j] == 0:
                    return True
        
        # 检查相邻相同数字
        for i in range(self.size):
            for j in range(self.size):
                current = self.grid[i][j]
                # 检查右边
                if j < self.size - 1 and self.grid[i][j + 1] == current:
                    return True
                # 检查下边
                if i < self.size - 1 and self.grid[i + 1][j] == current:
                    return True
        return False
    
    def has_won(self) -> bool:
        """检查是否获胜（出现2048）"""
        for row in self.grid:
            if 2048 in row:
                return True
        return False
    
    def show_game_over(self) -> None:
        """显示游戏结束界面"""
        print("\n" + "=" * 40)
        if self.has_won():
            print("🎉 恭喜获胜！你成功达到了2048！")
        else:
            print("😔 游戏结束！无法继续移动！")
        
        print(f"最终得分: {self.score}")
        
        if self.score > self.best_score:
            print("🏆 新纪录！你创造了最佳成绩！")
            self.best_score = self.score
        
        minutes = self.game_time // 60
        seconds = self.game_time % 60
        print(f"游戏时长: {minutes:02d}:{seconds:02d}")
        print("=" * 40)
    
    def get_input(self) -> str:
        """获取用户输入"""
        try:
            # 尝试使用getch（Windows）或tty（Unix）
            if os.name == 'nt':
                import msvcrt
                return msvcrt.getch().decode('utf-8').lower()
            else:
                import tty
                import termios
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(sys.stdin.fileno())
                    ch = sys.stdin.read(1).lower()
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                return ch
        except:
            # 降级到普通输入
            return input("\n请输入操作: ").lower()
    
    def play(self) -> None:
        """主游戏循环"""
        self.init_game()
        
        while True:
            self.print_grid()
            
            if not self.can_move():
                self.show_game_over()
                self.save_best_score()
                break
            
            if self.has_won():
                print("\n🎉 恭喜！你成功达到了2048！")
                print("你可以选择继续游戏创造更高分数！")
            
            move = self.get_input()
            
            moved = False
            if move in ['a', '4']:  # 左
                moved = self.move_left()
            elif move in ['d', '6']:  # 右
                moved = self.move_right()
            elif move in ['w', '8']:  # 上
                moved = self.move_up()
            elif move in ['s', '2']:  # 下
                moved = self.move_down()
            elif move == 'q':  # 退出
                print("\n👋 感谢游玩！")
                self.save_best_score()
                break
            elif move == 'r':  # 重新开始
                print("\n🔄 重新开始游戏！")
                self.save_best_score()
                self.init_game()
                continue
            
            if moved:
                self.add_random_tile()

def main():
    """主函数"""
    print("🎮 欢迎来到2048游戏！")
    print("加载中...")
    time.sleep(1)
    
    game = Game2048()
    game.play()
    
    print("\n游戏数据已保存到 2048_scores.json")
    print("按回车键退出...")
    input()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n游戏被中断，数据已自动保存。")
        sys.exit(0)
    except Exception as e:
        print(f"\n游戏出现错误: {e}")
        print("按回车键退出...")
        input()
        sys.exit(1)
