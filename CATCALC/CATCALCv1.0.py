#!/usr/bin python

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
def pow_(x, y):
    # 捕获复数/溢出等异常，让主循环统一处理
    return operator.pow(x, y)

# 运算表：符号 + 对应函数
OPS = {
    '+':  ('加法', add),
    '-':  ('减法', sub),
    '*':  ('乘法', mul),
    '/':  ('除法', div),
    '**': ('乘方', pow_),
}

def get_number(prompt):
    """反复读取直到拿到合法浮点数"""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("喵？这似乎不是数字，再试一次~")

def get_op():
    """读取并校验运算符"""
    symbols = ' '.join(OPS.keys())
    while True:
        op = input(f"选择运算符 ({symbols}): ").strip()
        if op in OPS:
            return op
        print("喵？不认识这个符号，再试一次~")

def calc_once():
    """单轮计算"""
    op_sym = get_op()
    a = get_number("输入第一个数字喵: ")
    b = get_number("输入第二个数字喵: ")

    name, func = OPS[op_sym]
    try:
        result = func(a, b)
    except ZeroDivisionError as e:
        print("错误喵呜：", e)
        return
    except OverflowError:
        print("结果太大，猫咪装不下啦！")
        return
    except Exception as e:
        # 捕获 math domain error 等
        print("计算出错呜：", e)
        return

    print(f"结果: {a} {op_sym} {b} = {result}\n")

def main():
    print(r"""
 /\_/\  
( o.o ) 
 > ^ <   CATCALC v1.0 开工啦~
""")
    while True:
        calc_once()
        again = input("继续算吗喵？(y/n): ").strip().lower()
        if again not in ('y', 'yes', '是', '继续'):
            print("猫咪下班，喵~")
            break

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        # Ctrl-C / Ctrl-D 优雅退出 彩蛋
        print("\n喵呜，被强行撸猫，拜拜~")
        sys.exit(0)
