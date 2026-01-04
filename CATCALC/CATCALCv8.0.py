#!/usr/bin/env python3

import os
import math
import cmath
import random
from decimal import Decimal, getcontext

os.system('clear&figlet CATCALC')

# ------------------ 猫娘彩色工具 ------------------
class T:
    HEADER = '\033[95m'; OKBLUE = '\033[94m'; OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'; WARNING = '\033[93m'; FAIL = '\033[91m'; ENDC = '\033[0m'; BOLD = '\033[1m'

def color(txt, code): return f"{code}{txt}{T.ENDC}"

# ------------------ 猫娘表情库 ------------------
class CatgirlEmoji:
    HAPPY = "(*≧▽≦)"; EXCITED = "☆*: .｡. o(≧▽≦)o .｡.:*☆"
    SAD = "(｡•́︿•̀｡)"; BLUSHING = "(*///▽///*)"; WINK = "(￣▽￣)ノ"
    SLEEPY = "(￣o￣) zzZ"; PRAYING = "(｡>﹏<｡)"; CELEBRATING = "♪(´▽｀)"

# ------------------ 猫娘对话系统 ------------------
class CatgirlDialog:
    @staticmethod
    def greet():
        return random.choice([
            f"喵呜~ 猫娘计算器启动喵！{CatgirlEmoji.HAPPY}",
            f"主人好呀~ 猫娘来帮你计算了喵！{CatgirlEmoji.EXCITED}",
            f"喵~ 今天也要开心计算哦！{CatgirlEmoji.WINK}"
        ])
    
    @staticmethod
    def encourage():
        return f"{random.choice(['计算得好棒喵！', '主人真厉害喵！', '太棒了喵！'])} {CatgirlEmoji.HAPPY}"
    
    @staticmethod
    def comfort():
        return f"{random.choice(['没关系的喵~', '重新来过就好了喵~', '猫娘相信主人可以的喵~'])} {CatgirlEmoji.PRAYING}"

# ------------------ 基础运算表（数字选择）------------------
BASIC_OPS = {
    1: ('+', '加法', lambda a,b: a+b),
    2: ('-', '减法', lambda a,b: a-b),
    3: ('*', '乘法', lambda a,b: a*b),
    4: ('/', '除法', lambda a,b: a/b),
    5: ('**', '乘方', lambda a,b: a**b),
    6: ('√', '开根', lambda a: math.sqrt(a), False),
    7: ('sin', '正弦', lambda a,rad=True: math.sin(a if rad else math.radians(a)), False, True),
    8: ('cos', '余弦', lambda a,rad=True: math.cos(a if rad else math.radians(a)), False, True),
    9: ('tan', '正切', lambda a,rad=True: math.tan(a if rad else math.radians(a)), False, True),
    10: ('log', '对数', lambda a: math.log10(a), False),
    11: ('ln', '自然对数', lambda a: math.log(a), False),
    12: ('!', '阶乘', lambda a: math.factorial(int(a)) if a>=0 and a==int(a) else math.gamma(a+1), False),
    13: ('abs', '绝对值', lambda a: abs(a), False),
    14: ('pi', '圆周率π', lambda: math.pi, False, False, True),
    15: ('e', '自然常数e', lambda: math.e, False, False, True),
}

# ------------------ 猫娘历史记录 ------------------
HISTORY = []
def record(expr, val):
    HISTORY.append(f"{expr} = {val}")
    if len(HISTORY) > 20: HISTORY.pop(0)

def show_history():
    if not HISTORY:
        print(color(f"历史记录还是空空的喵~{CatgirlEmoji.SAD}", T.WARNING))
        return
    print(color(f"===== 猫娘的历史记录 ===== {CatgirlEmoji.HAPPY}", T.HEADER))
    for idx, line in enumerate(HISTORY, 1):
        print(f"{idx:02d}. {line}")

# ------------------ 猫娘数字格式化 ------------------
PREC = 6
def fmt_num(n):
    if isinstance(n, complex):
        if abs(n.imag) < 1e-15: n = n.real
        elif abs(n.real) < 1e-15: n = n.imag*1j
    if isinstance(n, complex):
        return f"{n.real:.{PREC}f} + {n.imag:.{PREC}f}i"
    return f"{n:.{PREC}f}".rstrip('0').rstrip('.')

# ------------------ 猫娘输入助手 ------------------
def get_number(prompt):
    while True:
        try:
            txt = input(color(prompt, T.OKCYAN)).strip()
            if txt.lower() == 'pi':
                print(f"{CatgirlEmoji.EXCITED} 哇，是π喵！")
                return math.pi
            if txt.lower() == 'e':
                print(f"{CatgirlEmoji.EXCITED} 是自然常数e喵！")
                return math.e
            return float(txt)
        except ValueError:
            print(color(f"喵？这个不是有效数字喵，重新输入好不好喵~{CatgirlEmoji.BLUSHING}", T.WARNING))

def choose_operation():
    """数字选择运算符喵~"""
    print(color("\n=== 选择运算类型喵 ===", T.HEADER))
    for num, (op, name, *_) in BASIC_OPS.items():
        print(f"{num:2d}. {name} ({op})")
    print(" 0. 查看历史记录喵")
    print("99. 退出程序喵")
    
    while True:
        try:
            choice = int(input(color("请选择数字喵 (1-15): ", T.BOLD)))
            if choice in BASIC_OPS or choice in [0, 99]:
                return choice
            print(color(f"请输入1-15之间的数字喵，或者0/99喵~{CatgirlEmoji.CONFUSED}", T.WARNING))
        except ValueError:
            print(color(f"输入的不是数字喵，重新输入好不好喵~{CatgirlEmoji.CONFUSED}", T.WARNING))

def angle_mode():
    while True:
        m = input("弧度(r)还是角度(d)喵？[r/d]: ").strip().lower()
        if m in ('r','rad','弧度'):
            print(f"{CatgirlEmoji.HAPPY} 好的喵，用弧度喵~")
            return True
        if m in ('d','deg','角度','°'):
            print(f"{CatgirlEmoji.HAPPY} 好的喵，用角度喵~")
            return False
        print(color(f"输入 r 或者 d 喵~{CatgirlEmoji.BLUSHING}", T.WARNING))

# ------------------ 基础计算（简化版）------------------
def basic_calculation():
    """猫娘基础计算喵~"""
    choice = choose_operation()
    
    if choice == 0:
        show_history()
        return
    if choice == 99:
        print(color(f"猫娘要休息了喵，再见喵主人~{CatgirlEmoji.SLEEPY}", T.OKBLUE))
        sys.exit(0)
    
    op, name, func, *args = BASIC_OPS[choice]
    is_binary = args[0] if args else True
    need_rad = args[1] if len(args) > 1 else False
    is_const = args[2] if len(args) > 2 else False
    
    # 常数直接返回
    if is_const:
        val = func()
        print(color(f"{name} = {fmt_num(val)} {CatgirlEmoji.EXCITED}", T.OKGREEN))
        record(name, val)
        print(CatgirlDialog.encourage())
        return
    
    # 单目运算
    if not is_binary:
        a = get_number("输入数字喵: ")
        if need_rad and op in ['sin', 'cos', 'tan']:
            rad = angle_mode()
            result = func(a, rad)
        else:
            result = func(a)
        expr = f"{op}({a})"
    
    # 双目运算
    else:
        a = get_number("输入第一个数字喵: ")
        b = get_number("输入第二个数字喵: ")
        result = func(a, b)
        expr = f"{a} {op} {b}"
    
    print(color(f"结果: {expr} = {fmt_num(result)} {CatgirlEmoji.EXCITED}", T.OKGREEN))
    record(expr, result)
    print(CatgirlDialog.encourage())

# ------------------ 猫娘主循环 ------------------
def main():
    print(color(rf"""
 /\_/\  
( o.o ) 
 > ^ <   猫娘计算器 v8.0 超简洁萌版喵！
 输入 99 退出，0 查看历史喵~
 💕 超简洁，超萌，超易用喵！
    """, T.HEADER))
    
    print(color(CatgirlDialog.greet(), T.OKGREEN))
    
    while True:
        try:
            basic_calculation()
        except KeyboardInterrupt:
            print(color(f"\n主人强行撸猫，猫娘要休息了喵~{CatgirlEmoji.SLEEPY}", T.WARNING))
            break
        except Exception as e:
            print(color(f"喵娘遇到了小错误喵: {e} {CatgirlEmoji.SAD}", T.FAIL))
            print(CatgirlDialog.comfort())
            if input("要详细错误信息喵？(y/n): ").lower() == 'y':
                traceback.print_exc()

if __name__ == '__main__':
    main()
