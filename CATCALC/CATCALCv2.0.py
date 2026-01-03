#!/usr/bin/env python3

import math
import sys
import operator
import os

os.system('clear')
os.system('figlet CATCALC')

# =================== 工具函数 ===================
def add(x, y): return x + y
def sub(x, y): return x - y
def mul(x, y): return x * y
def div(x, y):
    if y == 0:
        raise ZeroDivisionError("除数不能为零喵！")
    return x / y
def pow_(x, y): return operator.pow(x, y)
def root(x):
    if x < 0:
        raise ValueError("负数没有实数根喵！")
    return math.sqrt(x)
def fact(x):
    if x < 0 or x != int(x):
        raise ValueError("阶乘只能算非负整数喵！")
    return math.factorial(int(x))
def sin_(x, rad=True): return math.sin(x if rad else math.radians(x))
def cos_(x, rad=True): return math.cos(x if rad else math.radians(x))
def tan_(x, rad=True): return math.tan(x if rad else math.radians(x))

# 运算表：符号 → (名字, 函数, 需要第二数？, 需要弧度？)
OPS = {
    '+':  ('加法', add, True, False),
    '-':  ('减法', sub, True, False),
    '*':  ('乘法', mul, True, False),
    '/':  ('除法', div, True, False),
    '**': ('乘方', pow_, True, False),
    '√':  ('开根', root, False, False),
    '!':  ('阶乘', fact, False, False),
    'sin':('正弦', sin_, False, True),
    'cos':('余弦', cos_, False, True),
    'tan':('正切', tan_, False, True),
}

def get_number(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("喵？这似乎不是数字，再试一次~")

def get_op():
    symbols = ' '.join(OPS.keys())
    while True:
        op = input(f"选择运算符 ({symbols}): ").strip().lower()
        if op in OPS:
            return op
        print("喵？不认识这个符号，再试一次~")

def angle_mode():
    """询问角度制还是弧度制，仅对三角函数生效"""
    while True:
        mode = input("用弧度(rad)还是角度(°)？(r/d): ").strip().lower()
        if mode in ('r', 'rad', '弧度'):
            return True
        if mode in ('d', 'deg', '°', '角度'):
            return False
        print("输入 r 或 d 喵~")

def calc_once():
    op_sym = get_op()
    name, func, need_second, need_rad = OPS[op_sym]

    a = get_number("输入数字喵: ")
    b = None
    if need_second:
        b = get_number("输入第二个数字喵: ")

    # 三角函数额外问角度/弧度
    if need_rad:
        rad = angle_mode()
        try:
            result = func(a, rad)
        except ValueError as e:
            print("计算出错：", e)
            return
    else:
        try:
            result = func(a, b) if need_second else func(a)
        except (ZeroDivisionError, ValueError, OverflowError) as e:
            print("计算出错：", e)
            return
        except Exception as e:
            print("未知错误：", e)
            return

    # 打印漂亮一点
    if need_second:
        print(f"结果: {a} {op_sym} {b} = {result}\n")
    else:
        print(f"结果: {op_sym}{a} = {result}\n")

def main():
    print(r"""
 /\_/\  
( o.o ) 
 > ^ <   CATCALC v3.0 开工啦~
    支持 + - * / ** √ ! sin cos tan
""")
    while True:
        calc_once()
        again = input("继续算吗？(y/n): ").strip().lower()
        if again not in ('y', 'yes', '是', '继续'):
            print("猫咪下班，喵~")
            break

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n喵呜，被强行撸猫，拜拜~")
        sys.exit(0)
