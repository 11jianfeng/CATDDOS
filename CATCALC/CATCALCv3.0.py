#!/usr/bin/env python3

import math
import cmath
import os
import sys
import operator
import pprint
import traceback
from decimal import Decimal, getcontext
from functools import lru_cache

# ------------------ 彩色工具 ------------------
class T:
    """彩色终端很好玩的"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def color(txt, code): return f"{code}{txt}{T.ENDC}"

# ------------------ 插件加载器 ------------------
PLUGINS = {}
def load_plugins():
    """动态加载 plugins/ 目录下的 *.py"""
    plug_dir = os.path.join(os.path.dirname(__file__), "plugins")
    if not os.path.isdir(plug_dir):
        return
    sys.path.insert(0, plug_dir)
    for fname in os.listdir(plug_dir):
        if fname.endswith(".py") and not fname.startswith("_"):
            mod_name = fname[:-3]
            try:
                mod = __import__(mod_name)
                # 约定:模块里 dict FUNC={符号:(名字,函数,需第二数?,需弧度?)}
                PLUGINS.update(getattr(mod, "FUNC", {}))
            except Exception as e:
                print(color(f"[插件] 加载 {fname} 失败：{e}", T.WARNING))
    sys.path.remove(plug_dir)

# ------------------ 核心运算表 ------------------
OPS = {
    # 四则
    '+':  ('加法', operator.add, True, False),
    '-':  ('减法', operator.sub, True, False),
    '*':  ('乘法', operator.mul, True, False),
    '/':  ('除法', operator.truediv, True, False),
    '**': ('乘方', operator.pow, True, False),
    '%':  ('取模', operator.mod, True, False),
    # 单目
    '√':  ('开根', lambda x: cmath.sqrt(x), False, False),
    '!':  ('阶乘', lambda x: math.factorial(int(x)) if x>=0 and x==int(x) else math.gamma(x+1), False, False),
    'ln': ('自然对数', cmath.log, False, False),
    'log':('常用对数', lambda x: cmath.log10(x), False, False),
    'sin':('正弦', lambda x,rad=True: cmath.sin(x if rad else math.radians(x)), False, True),
    'cos':('余弦', lambda x,rad=True: cmath.cos(x if rad else math.radians(x)), False, True),
    'tan':('正切', lambda x,rad=True: cmath.tan(x if rad else math.radians(x)), False, True),
    'asin':('反正弦', lambda x,rad=True: (cmath.asin(x) if rad else math.degrees(cmath.asin(x))), False, True),
    'acos':('反余弦', lambda x,rad=True: (cmath.acos(x) if rad else math.degrees(cmath.acos(x))), False, True),
    'atan':('反正切', lambda x,rad=True: (cmath.atan(x) if rad else math.degrees(cmath.atan(x))), False, True),
    'sinh':('双曲正弦', cmath.sinh, False, False),
    'cosh':('双曲余弦', cmath.cosh, False, False),
    'tanh':('双曲正切', cmath.tanh, False, False),
    'rad':('角度→弧度', math.radians, False, False),
    'deg':('弧度→角度', math.degrees, False, False),
    # 常数
    'pi': ('π', lambda: math.pi, False, False),
    'e':  ('自然常数e', lambda: math.e, False, False),
}
# 合并插件
load_plugins()
OPS.update(PLUGINS)

# ------------------ 历史记录 ------------------
HISTORY = []

def record(expr, val):
    HISTORY.append(f"{expr} = {val}")
    if len(HISTORY) > 50: HISTORY.pop(0)

def show_history():
    if not HISTORY:
        print(color("历史为空喵~", T.WARNING)); return
    print(color("===== 历史记录 =====", T.HEADER))
    for idx, line in enumerate(HISTORY, 1):
        print(f"{idx:02d}. {line}")
    print(color("====================", T.HEADER))

# ------------------ 输入/输出 ------------------
PREC = 6
def set_precision():
    global PREC
    try:
        PREC = int(input("保留小数位(0-15): "))
        getcontext().prec = PREC + 2
    except ValueError:
        print(color("非法数字，保持默认 6 位", T.WARNING))

def fmt_num(n):
    """漂亮地打印实数/复数"""
    if isinstance(n, complex):
        if abs(n.imag) < 1e-15: n = n.real
        elif abs(n.real) < 1e-15: n = n.imag*1j
    if isinstance(n, complex):
        return f"{n.real:.{PREC}f} + {n.imag:.{PREC}f}j"
    else:
        return f"{n:.{PREC}f}".rstrip('0').rstrip('.')

def get_number(prompt):
    while True:
        try:
            txt = input(prompt).strip()
            if txt.lower() == 'pi': return math.pi
            if txt.lower() == 'e': return math.e
            return float(txt)
        except ValueError:
            print(color("喵？这不是合法数字，再试~", T.WARNING))

def get_op():
    symbols = ' '.join(OPS.keys())
    while True:
        op = input(color(f"选择运算符 ({symbols}) 或 hist 查看历史: ", T.OKCYAN)).strip().lower()
        if op == 'hist':
            show_history(); continue
        if op in OPS: return op
        print(color("不认识这个符号喵~", T.WARNING))

def angle_mode():
    while True:
        m = input("弧度(r)还是角度(d)？[r/d]: ").strip().lower()
        if m in ('r','rad','弧度'): return True
        if m in ('d','deg','角度','°'): return False
        print(color("输入 r 或 d 喵~", T.WARNING))

# ------------------ 单轮计算 ------------------
def calc_once():
    op = get_op()
    name, func, need_second, need_rad = OPS[op]
    # 常数直接返回
    if op in ('pi','e'):
        val = func()
        print(color(f"常数 {name} = {fmt_num(val)}", T.OKGREEN))
        record(name, val); return

    a = get_number("输入数字喵: ")
    b = None
    if need_second:
        b = get_number("输入第二个数字喵: ")

    # 三角函数额外问
    rad = True
    if need_rad and op in ('sin','cos','tan','asin','acos','atan'):
        rad = angle_mode()

    try:
        result = func(a, b) if need_second else (func(a, rad) if need_rad else func(a))
    except Exception as e:
        print(color(f"出错: {e}", T.FAIL))
        return

    # 打印与记录
    expr = f"{a} {op} {b}" if need_second else f"{op}{a}"
    print(color(f"结果: {expr} = {fmt_num(result)}", T.OKGREEN))
    record(expr, result)

# ------------------ 主循环 ------------------
def main():
    print(color(r"""
 /\_/\  
( o.o ) 
 > ^ <   CATCALC v3.0 万能猫上线！
 输入 prec 可改精度，hist 查看历史
 支持复数、插件、常数、角度转换
    """, T.HEADER))
    while True:
        try:
            cmd = input(color(">>> ", T.BOLD)).strip().lower()
            if cmd in ('q','quit','exit','bye'):
                print(color("猫咪下班，喵呜~", T.OKBLUE)); break
            if cmd == 'prec':
                set_precision(); continue
            if cmd == 'hist':
                show_history(); continue
            # 回车直接开始一次计算
            calc_once()
        except (KeyboardInterrupt, EOFError):
            print(color("\n被强行撸猫，拜拜~", T.WARNING)); break
        except Exception as e:
            print(color(f"未知异常: {e}", T.FAIL))
            if input("打印详细堆栈？(y/n): ").lower()=='y':
                traceback.print_exc()

if __name__ == '__main__':
    main()
