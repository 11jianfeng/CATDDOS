#!/usr/bin/env python3

import os
import math
import cmath
import random
import decimal
from decimal import Decimal, getcontext
import sys

os.system('clear&figlet CATCALC')

# ------------------ 猫娘彩色工具 ------------------
class T:
    HEADER = '\033[95m'; OKBLUE = '\033[94m'; OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'; WARNING = '\033[93m'; FAIL = '\033[91m'; ENDC = '\033[0m'; BOLD = '\033[1m'

def color(txt, code): return f"{code}{txt}{T.ENDC}"

# ------------------ 猫娘表情库 ------------------
class CatgirlEmoji:
    HAPPY = "(*≧▽≦)"; EXCITED = "☆*: .｡. o(≧▽≦)o .｡.:*☆"; SURPRISED = "（゜ロ゜）"
    SAD = "(｡•́︿•̀｡)"; BLUSHING = "(*///▽///*)"; WINK = "(￣▽￣)ノ"; LOVING = "(づ￣ ³￣)づ"
    PRAYING = "(｡>﹏<｡)"; CELEBRATING = "♪(´▽｀)"; MAGIC = "（〜^∇^)〜"; SPARKLE = "✧*:･ﾟ✧"
    SLEEPY = "(￣o￣) zzZ"; COMFORT = "(｡>﹏<｡)♡"; CONFUSED = "(￣ω￣;)"

# ------------------ 猫娘对话系统 ------------------
class CatgirlDialog:
    @staticmethod
    def greet():
        return random.choice([
            f"喵呜~ 欢迎来到猫娘常数计算器喵！{CatgirlEmoji.EXCITED}",
            f"主人好呀~ 让猫娘带你探索数学常数的奥秘喵！{CatgirlEmoji.MAGIC}",
            f"数学常数的世界好神奇喵~ 一起看看吧！{CatgirlEmoji.SPARKLE}"
        ])
    
    @staticmethod
    def constant_surprise(name):
        surprises = [
            f"哇！{name} 是个神奇的数字喵！{CatgirlEmoji.SURPRISED}",
            f"{name} 出现了喵！看起来很神秘呢{CatgirlEmoji.EXCITED}",
            f"这就是著名的 {name} 喵！猫娘好激动{CatgirlEmoji.SPARKLE}"
        ]
        return random.choice(surprises)
    
    @staticmethod
    def encourage():
        return f"{random.choice(['发现了神奇的常数喵！', '数学真奇妙喵！', '猫娘又学到了新东西喵！'])} {CatgirlEmoji.HAPPY}"
    
    @staticmethod
    def comfort():
        return f"{random.choice(['没关系的喵，重新来过就好了喵~', '猫娘相信主人一定可以的喵！', '小小的失误不算什么喵~'])} {CatgirlEmoji.COMFORT}"

# ------------------ 数学常数百科全书 ------------------
class MathConstants:
    """数学常数百科全书喵~"""
    
    def __init__(self):
        # 设置高精度计算
        getcontext().prec = 100
        
    @staticmethod
    def pi():
        """圆周率 π 喵~"""
        return math.pi
    
    @staticmethod
    def e():
        """自然常数 e 喵~"""
        return math.e
    
    @staticmethod
    def phi():
        """黄金比例 φ 喵~"""
        return (1 + math.sqrt(5)) / 2
    
    @staticmethod
    def euler_mascheroni():
        """欧拉-马歇罗尼常数 γ 喵~"""
        # 使用调和级数近似计算
        n = 1000000
        gamma = 0.0
        for i in range(1, n+1):
            gamma += 1.0/i
        gamma -= math.log(n)
        return gamma
    
    @staticmethod
    def catalan():
        """卡塔兰常数 G 喵~"""
        # 使用级数求和: G = Σ((-1)^n/(2n+1)^2)
        g = 0.0
        for n in range(100000):
            g += ((-1)**n) / ((2*n + 1)**2)
        return g
    
    @staticmethod
    def apery():
        """阿佩里常数 ζ(3) 喵~"""
        # ζ(3) = Σ(1/n^3)
        zeta3 = 0.0
        for n in range(1, 100000):
            zeta3 += 1.0 / (n**3)
        return zeta3
    
    @staticmethod
    def khinchin():
        """辛钦常数 K₀ 喵~"""
        # 近似值，理论值约为 2.6854520010...
        return 2.6854520010
    
    @staticmethod
    def twin_prime():
        """孪生素数常数 Π₂ 喵~"""
        # 孪生素数常数近似值
        return 0.6601618158
    
    @staticmethod
    def mertens():
        """梅滕斯常数 M 喵~"""
        # 近似值
        return 0.2614972128
    
    @staticmethod
    def glaisher_kinkelin():
        """格莱舍-金克林常数 A 喵~"""
        # 近似值
        return 1.2824271291
    
    @staticmethod
    def conway():
        """康威常数 λ 喵~"""
        # 康威常数，约为 1.3035772690...
        return 1.3035772690
    
    @staticmethod
    def omega():
        """欧米伽常数 Ω 喵~"""
        # 满足 Ωe^Ω = 1 的常数
        # 使用迭代法计算
        omega = 0.5
        for _ in range(100):
            omega = math.exp(-omega)
        return omega
    
    @staticmethod
    def plastic_number():
        """塑料数 ρ 喵~"""
        # 满足 ρ³ = ρ + 1 的实数解
        return ((9 + math.sqrt(69))/18)**(1/3) + ((9 - math.sqrt(69))/18)**(1/3)
    
    @staticmethod
    def silver_ratio():
        """银比 δs 喵~"""
        return 1 + math.sqrt(2)
    
    @staticmethod
    def supergolden_ratio():
        """超黄金比例 ψ 喵~"""
        # 满足 ψ³ = ψ² + 1 的实数解
        return ((29 + 3*math.sqrt(93))/54)**(1/3) + ((29 - 3*math.sqrt(93))/54)**(1/3) + 1/3
    
    @staticmethod
    def erdos_borwein():
        """埃尔德什-博温常数 E 喵~"""
        # E = Σ(1/(2^n - 1))
        e = 0.0
        for n in range(1, 1000):
            e += 1.0 / (2**n - 1)
        return e
    
    @staticmethod
    def laplace_limit():
        """拉普拉斯极限 λ 喵~"""
        # 约为 0.6627434193...
        return 0.6627434193
    
    @staticmethod
    def gauss():
        """高斯常数 G 喵~"""
        # G = 1/agm(1, 1/√2)
        a, b = 1.0, 1.0/math.sqrt(2)
        for _ in range(100):
            a, b = (a + b)/2, math.sqrt(a*b)
        return 1.0/a

# ------------------ 常数菜单 ------------------
CONSTANT_MENU = {
    1: ("π - 圆周率", "世界上最著名的常数喵~", MathConstants.pi),
    2: ("e - 自然常数", "自然对数的底数喵~", MathConstants.e),
    3: ("φ - 黄金比例", "最美的比例喵~", MathConstants.phi),
    4: ("γ - 欧拉常数", "调和级数的秘密喵~", MathConstants.euler_mascheroni),
    5: ("G - 卡塔兰常数", "交错级数的奇迹喵~", MathConstants.catalan),
    6: ("ζ(3) - 阿佩里常数", "黎曼ζ函数的惊喜喵~", MathConstants.apery),
    7: ("K₀ - 辛钦常数", "连分数的奥秘喵~", MathConstants.khinchin),
    8: ("Π₂ - 孪生素数常数", "素数双胞胎的秘密喵~", MathConstants.twin_prime),
    9: ("M - 梅滕斯常数", "数论的宝藏喵~", MathConstants.mertens),
    10: ("A - 格莱舍常数", "无穷乘积的魔法喵~", MathConstants.glaisher_kinkelin),
    11: ("λ - 康威常数", "look-and-say的奥秘喵~", MathConstants.conway),
    12: ("Ω - 欧米伽常数", "超越方程的解喵~", MathConstants.omega),
    13: ("ρ - 塑料数", "比黄金比例更神秘喵~", MathConstants.plastic_number),
    14: ("δs - 银比", "白银比例的美丽喵~", MathConstants.silver_ratio),
    15: ("ψ - 超黄金比例", "超级黄金比例喵~", MathConstants.supergolden_ratio),
    16: ("E - 埃尔德什-博温常数", "无穷级数的奇迹喵~", MathConstants.erdos_borwein),
    17: ("λ - 拉普拉斯极限", "天体力学的边界喵~", MathConstants.laplace_limit),
    18: ("G - 高斯常数", "算术几何平均的魔法喵~", MathConstants.gauss),
}

# ------------------ 猫娘常数计算器 ------------------
class CatgirlConstantCalculator:
    """猫娘常数计算器喵~"""
    
    def __init__(self):
        self.constants = MathConstants()
        self.precision = 50  # 默认精度
        
    def set_precision(self, prec):
        """设置计算精度喵~"""
        self.precision = max(10, min(1000, prec))
        getcontext().prec = self.precision
        print(color(f"精度已设置为 {self.precision} 位喵！{CatgirlEmoji.SPARKLE}", T.OKGREEN))
    
    def calculate_constant(self, choice):
        """计算选定的常数喵~"""
        if choice not in CONSTANT_MENU:
            return None, "无效的选项喵~"
        
        name, description, func = CONSTANT_MENU[choice]
        print(color(f"\n{name}", T.HEADER))
        print(color(f"{description}", T.OKCYAN))
        print(CatgirlDialog.constant_surprise(name.split('-')[0].strip()))
        
        try:
            # 使用decimal提高精度
            with decimal.localcontext() as ctx:
                ctx.prec = self.precision
                result = func()
                
            # 格式化输出
            result_str = self.format_result(result)
            return result, result_str
            
        except Exception as e:
            return None, f"计算出错喵: {e}"
    
    def format_result(self, result):
        """格式化结果喵~"""
        if isinstance(result, (int, float)):
            if abs(result) > 1e10 or abs(result) < 1e-5:
                return f"{result:.{self.precision}e}"
            else:
                return f"{result:.{self.precision}f}".rstrip('0').rstrip('.')
        return str(result)
    
    def show_constant_info(self, choice):
        """显示常数详细信息喵~"""
        if choice not in CONSTANT_MENU:
            return
        
        name, description, func = CONSTANT_MENU[choice]
        result = func()
        
        print(color(f"\n{'='*50}", T.HEADER))
        print(color(f" 数学常数: {name}", T.BOLD))
        print(color(f"{'='*50}", T.HEADER))
        print(color(f"描述: {description}", T.OKCYAN))
        print(color(f"数值: {self.format_result(result)}", T.OKGREEN))
        
        # 添加有趣的数学知识
        self.add_math_trivia(name.split('-')[0].strip())

    def add_math_trivia(self, constant_name):
        """添加数学趣闻喵~"""
        trivia = {
            "π": "π是一个无理数，小数部分无限不循环喵！计算机已经计算了数万亿位呢！",
            "e": "e是自然增长的极限，出现在复利计算、放射性衰变等自然现象中喵~",
            "φ": "黄金比例被认为是最美的比例，在艺术、建筑和自然界中广泛存在喵！",
            "γ": "欧拉常数是否是有理数仍然是数学界未解决的难题之一喵~",
            "G": "卡塔兰常数出现在组合数学和数论的许多问题中喵~",
            "ζ(3)": "阿佩里在1978年证明了ζ(3)是无理数，这个发现震惊了数学界喵！",
            "Ω": "欧米伽常数满足 Ωe^Ω = 1，是超越方程的解喵~",
        }
        
        if constant_name in trivia:
            print(color(f"小知识: {trivia[constant_name]}", T.OKBLUE))
        print()

# ------------------ 历史记录 ------------------
HISTORY = []
def record_calculation(constant_name, value):
    """记录计算历史喵~"""
    HISTORY.append(f"{constant_name} = {value}")
    if len(HISTORY) > 30: HISTORY.pop(0)

def show_history():
    """显示计算历史喵~"""
    if not HISTORY:
        print(color(f"还没有计算过任何常数喵~{CatgirlEmoji.SAD}", T.WARNING))
        return
    print(color(f"===== 猫娘的计算历史 ===== {CatgirlEmoji.HAPPY}", T.HEADER))
    for idx, line in enumerate(HISTORY, 1):
        print(f"{idx:02d}. {line}")
    print()

# ------------------ 主循环 ------------------
def main():
    calculator = CatgirlConstantCalculator()
    
    print(color(rf"""
 /\_/\  
( o.o ) 
 > ^ <   猫娘常数计算器 v9.0 超萌版喵！
 探索数学常数的奇妙世界喵~ {CatgirlEmoji.SPARKLE}
    """, T.HEADER))
    
    print(color(CatgirlDialog.greet(), T.OKGREEN))
    print(color("数学常数是宇宙的密码喵！让猫娘带你一一破解它们喵~", T.OKCYAN))
    
    while True:
        try:
            print(color(f"\n=== 数学常数大观园喵 === {CatgirlEmoji.EXCITED}", T.HEADER))
            for num, (name, desc, _) in CONSTANT_MENU.items():
                print(f"{num:2d}. {name}")
                print(f"    {desc}")
            print()
            
            choice = input(color("主人想探索哪个常数喵？(输入数字，0=历史，77=精度，88=课堂，99=退出): ", T.BOLD)).strip()
            
            if choice == "99":
                print(color(f"猫娘要休息了喵，愿数学常数永远陪伴主人喵~{CatgirlEmoji.SLEEPY}", T.OKBLUE))
                break
            
            elif choice == "0":
                show_history()
            
            elif choice == "77":
                try:
                    prec = int(input("设置精度位数喵 (10-1000): "))
                    calculator.set_precision(prec)
                except ValueError:
                    print(color("请输入有效的数字喵~", T.WARNING))
            
            elif choice == "88":
                knowledge_classroom()
            
            elif choice.isdigit() and 1 <= int(choice) <= 18:
                num = int(choice)
                result, result_str = calculator.calculate_constant(num)
                
                if result is not None:
                    print(color(f"精确值: {result_str}", T.OKGREEN))
                    record_calculation(CONSTANT_MENU[num][0].split('-')[0].strip(), result_str)
                    print(CatgirlDialog.encourage())
                    
                    # 显示详细信息
                    if input(color("想看详细信息和趣闻喵？(y/n): ", T.OKCYAN)).lower() == 'y':
                        calculator.show_constant_info(num)
                else:
                    print(color(f"计算出错了喵: {result_str}", T.FAIL))
                    print(CatgirlDialog.comfort())
            
            else:
                print(color(f"喵娘不明白主人的选择喵，重新选好不好喵~{CatgirlEmoji.CONFUSED}", T.WARNING))
                
        except KeyboardInterrupt:
            print(color(f"\n主人强行撸猫，猫娘要休息了喵~{CatgirlEmoji.SLEEPY}", T.WARNING))
            break
        except Exception as e:
            print(color(f"喵娘遇到了未知错误喵: {e} {CatgirlEmoji.SAD}", T.FAIL))
            print(CatgirlDialog.comfort())
            if input("要详细错误信息喵？(y/n): ").lower() == 'y':
                import traceback
                traceback.print_exc()

if __name__ == '__main__':
    main()
