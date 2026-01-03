#!/usr/bin/env python3

import math
import cmath
import os
import sys
import operator
import pprint
import traceback
import random
import statistics
import json
from decimal import Decimal, getcontext
from functools import lru_cache
from datetime import datetime
import re

os.system('clear')
os.system('figlet CATCALC')

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

# ------------------ 统计计算模块 ------------------
class StatsCalculator:
    """统计计算器"""
    def __init__(self):
        self.data = []
    
    def add_data(self, values):
        """添加数据"""
        self.data.extend([float(x) for x in values])
    
    def clear(self):
        """清空数据"""
        self.data = []
    
    def calculate_all(self):
        """计算所有统计值"""
        if not self.data:
            return None
        
        n = len(self.data)
        mean = statistics.mean(self.data)
        median = statistics.median(self.data)
        try:
            mode = statistics.mode(self.data)
        except statistics.StatisticsError:
            mode = "无众数"
        
        std_dev = statistics.stdev(self.data) if n > 1 else 0
        variance = statistics.variance(self.data) if n > 1 else 0
        min_val = min(self.data)
        max_val = max(self.data)
        range_val = max_val - min_val
        
        return {
            '样本数': n,
            '平均值': mean,
            '中位数': median,
            '众数': mode,
            '标准差': std_dev,
            '方差': variance,
            '最小值': min_val,
            '最大值': max_val,
            '极差': range_val
        }

# ------------------ 进制转换器 ------------------
class BaseConverter:
    """进制转换器"""
    @staticmethod
    def convert_number(number, from_base, to_base):
        """转换进制"""
        try:
            # 先转换为十进制
            if from_base != 10:
                if isinstance(number, str):
                    decimal_num = int(number, from_base)
                else:
                    decimal_num = int(number)
            else:
                decimal_num = int(number)
            
            # 再从十进制转换到目标进制
            if to_base == 10:
                return str(decimal_num)
            elif to_base == 2:
                return bin(decimal_num)
            elif to_base == 8:
                return oct(decimal_num)
            elif to_base == 16:
                return hex(decimal_num)
            else:
                # 转换为任意进制
                return BaseConverter._base_n(decimal_num, to_base)
        except ValueError as e:
            return f"错误: {e}"
    
    @staticmethod
    def _base_n(num, base):
        """转换为任意进制"""
        digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        if num == 0:
            return "0"
        result = ""
        while num > 0:
            result = digits[num % base] + result
            num //= base
        return result

# ------------------ 单位换算器 ------------------
class UnitConverter:
    """单位换算器"""
    CONVERSIONS = {
        # 长度
        '长度': {
            'mm': 0.001, 'cm': 0.01, 'm': 1, 'km': 1000, 'in': 0.0254, 'ft': 0.3048, 'yd': 0.9144, 'mile': 1609.34
        },
        # 重量
        '重量': {
            'mg': 0.000001, 'g': 0.001, 'kg': 1, 't': 1000, 'oz': 0.0283495, 'lb': 0.453592
        },
        # 温度
        '温度': {
            'C': lambda x: x, 'F': lambda x: (x - 32) * 5/9, 'K': lambda x: x - 273.15
        },
        # 面积
        '面积': {
            'mm2': 0.000001, 'cm2': 0.0001, 'm2': 1, 'km2': 1000000, 'acre': 4046.86, 'ha': 10000
        },
        # 体积
        '体积': {
            'ml': 0.001, 'l': 1, 'm3': 1000, 'gal': 3.78541, 'qt': 0.946353
        },
        # 速度
        '速度': {
            'm/s': 1, 'km/h': 0.277778, 'mph': 0.44704, 'ft/s': 0.3048
        }
    }
    
    @staticmethod
    def convert(value, from_unit, to_unit, category):
        """单位转换"""
        try:
            if category == '温度':
                # 特殊处理温度
                if from_unit == 'C' and to_unit == 'F':
                    return value * 9/5 + 32
                elif from_unit == 'F' and to_unit == 'C':
                    return (value - 32) * 5/9
                elif from_unit == 'C' and to_unit == 'K':
                    return value + 273.15
                elif from_unit == 'K' and to_unit == 'C':
                    return value - 273.15
                elif from_unit == 'F' and to_unit == 'K':
                    return (value - 32) * 5/9 + 273.15
                elif from_unit == 'K' and to_unit == 'F':
                    return (value - 273.15) * 9/5 + 32
                else:
                    return value
            
            conversions = UnitConverter.CONVERSIONS[category]
            if from_unit in conversions and to_unit in conversions:
                # 先转换为标准单位，再转换到目标单位
                standard_value = value * conversions[from_unit] if isinstance(conversions[from_unit], (int, float)) else conversions[from_unit](value)
                if isinstance(conversions[to_unit], (int, float)):
                    result = standard_value / conversions[to_unit]
                else:
                    # 如果目标单位也是函数，需要反向转换
                    if to_unit == 'C' and from_unit != 'C':
                        result = standard_value  # 已经是摄氏度
                    else:
                        result = standard_value
                return result
            else:
                return f"不支持的单位转换: {from_unit} -> {to_unit}"
        except Exception as e:
            return f"转换错误: {e}"

# ------------------ 方程求解器 ------------------
class EquationSolver:
    """简单方程求解器"""
    @staticmethod
    def solve_quadratic(a, b, c):
        """求解二次方程 ax² + bx + c = 0"""
        try:
            a, b, c = float(a), float(b), float(c)
            discriminant = b**2 - 4*a*c
            
            if discriminant > 0:
                x1 = (-b + cmath.sqrt(discriminant)) / (2*a)
                x2 = (-b - cmath.sqrt(discriminant)) / (2*a)
                return f"两个实数根: x₁ = {fmt_num(x1)}, x₂ = {fmt_num(x2)}"
            elif discriminant == 0:
                x = -b / (2*a)
                return f"一个实数根: x = {fmt_num(x)}"
            else:
                x1 = (-b + cmath.sqrt(discriminant)) / (2*a)
                x2 = (-b - cmath.sqrt(discriminant)) / (2*a)
                return f"两个复数根: x₁ = {fmt_num(x1)}, x₂ = {fmt_num(x2)}"
        except Exception as e:
            return f"求解错误: {e}"
    
    @staticmethod
    def solve_linear(a, b):
        """求解线性方程 ax + b = 0"""
        try:
            a, b = float(a), float(b)
            if a == 0:
                if b == 0:
                    return "无限多解"
                else:
                    return "无解"
            x = -b / a
            return f"解: x = {fmt_num(x)}"
        except Exception as e:
            return f"求解错误: {e}"

# ------------------ 矩阵计算器 ------------------
class MatrixCalculator:
    """简单矩阵计算器"""
    @staticmethod
    def create_matrix(rows, cols):
        """创建矩阵"""
        matrix = []
        print(f"输入 {rows}x{cols} 矩阵:")
        for i in range(rows):
            while True:
                try:
                    row = input(f"第 {i+1} 行 (用空格分隔): ").strip().split()
                    if len(row) != cols:
                        print(color(f"需要 {cols} 个数字，你输入了 {len(row)} 个", T.WARNING))
                        continue
                    matrix.append([float(x) for x in row])
                    break
                except ValueError:
                    print(color("请输入有效的数字", T.WARNING))
        return matrix
    
    @staticmethod
    def matrix_add(a, b):
        """矩阵加法"""
        if len(a) != len(b) or len(a[0]) != len(b[0]):
            return "矩阵维度不匹配"
        result = []
        for i in range(len(a)):
            row = []
            for j in range(len(a[0])):
                row.append(a[i][j] + b[i][j])
            result.append(row)
        return result
    
    @staticmethod
    def matrix_multiply(a, b):
        """矩阵乘法"""
        if len(a[0]) != len(b):
            return "矩阵维度不匹配"
        result = []
        for i in range(len(a)):
            row = []
            for j in range(len(b[0])):
                sum_val = 0
                for k in range(len(a[0])):
                    sum_val += a[i][k] * b[k][j]
                row.append(sum_val)
            result.append(row)
        return result
    
    @staticmethod
    def matrix_determinant(matrix):
        """计算行列式（仅支持2x2和3x3）"""
        if len(matrix) != len(matrix[0]):
            return "仅支持方阵"
        if len(matrix) == 2:
            return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
        elif len(matrix) == 3:
            a, b, c = matrix[0]
            d, e, f = matrix[1]
            g, h, i = matrix[2]
            return a*(e*i - f*h) - b*(d*i - f*g) + c*(d*h - e*g)
        else:
            return "仅支持2x2和3x3矩阵"

# ------------------ 核心运算表 ------------------
OPS = {
    # 四则
    '+':  ('加法', operator.add, True, False),
    '-':  ('减法', operator.sub, True, False),
    '*':  ('乘法', operator.mul, True, False),
    '/':  ('除法', operator.truediv, True, False),
    '**': ('乘方', operator.pow, True, False),
    '%':  ('取模', operator.mod, True, False),
    '//': ('整除', operator.floordiv, True, False),
    # 单目
    '√':  ('开根', lambda x: cmath.sqrt(x), False, False),
    '!':  ('阶乘', lambda x: math.factorial(int(x)) if x>=0 and x==int(x) else math.gamma(x+1), False, False),
    'ln': ('自然对数', cmath.log, False, False),
    'log':('常用对数', lambda x: cmath.log10(x), False, False),
    'log2':('二进制对数', lambda x: cmath.log2(x), False, False),
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
    'abs':('绝对值', abs, False, False),
    'round':('四舍五入', round, False, False),
    'ceil':('向上取整', math.ceil, False, False),
    'floor':('向下取整', math.floor, False, False),
    'sign':('符号函数', lambda x: 1 if x > 0 else -1 if x < 0 else 0, False, False),
    # 复数函数
    'real':('实部', lambda x: x.real if isinstance(x, complex) else x, False, False),
    'imag':('虚部', lambda x: x.imag if isinstance(x, complex) else 0, False, False),
    'conj':('共轭', lambda x: x.conjugate() if isinstance(x, complex) else x, False, False),
    'arg':('辐角', lambda x: cmath.phase(x) if isinstance(x, complex) else 0, False, False),
    # 高级数学
    'gamma':('伽马函数', lambda x: math.gamma(x) if x > 0 else cmath.gamma(x), False, False),
    'erf':('误差函数', math.erf, False, False),
    'erfc':('互补误差函数', math.erfc, False, False),
    # 常数
    'pi': ('π', lambda: math.pi, False, False),
    'e':  ('自然常数e', lambda: math.e, False, False),
    'tau': ('τ', lambda: 2 * math.pi, False, False),
    'phi': ('φ', lambda: (1 + math.sqrt(5)) / 2, False, False),  # 黄金比例
    # 随机数
    'rand': ('随机数', random.random, False, False),
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
            if txt.lower() == 'phi': return (1 + math.sqrt(5)) / 2
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

# ------------------ 统计计算模式 ------------------
def stats_mode():
    """统计计算模式"""
    stats_calc = StatsCalculator()
    print(color("=== 统计计算模式 ===", T.HEADER))
    print("输入数据 (用空格分隔，输入空行结束):")
    
    while True:
        data_input = input("数据: ").strip()
        if not data_input:
            break
        try:
            values = [float(x) for x in data_input.split()]
            stats_calc.add_data(values)
            print(f"已添加 {len(values)} 个数据点")
        except ValueError:
            print(color("请输入有效的数字", T.WARNING))
    
    if not stats_calc.data:
        print(color("没有输入数据", T.WARNING))
        return
    
    results = stats_calc.calculate_all()
    if results:
        print(color("=== 统计结果 ===", T.OKGREEN))
        for key, value in results.items():
            print(f"{key}: {fmt_num(value)}")

# ------------------ 进制转换模式 ------------------
def base_convert_mode():
    """进制转换模式"""
    print(color("=== 进制转换模式 ===", T.HEADER))
    
    while True:
        print("\n可选操作:")
        print("1. 十进制 → 其他进制")
        print("2. 其他进制 → 十进制") 
        print("3. 任意进制互转")
        print("4. 返回主菜单")
        
        choice = input("选择操作: ").strip()
        
        if choice == '4':
            break
        
        if choice in ['1', '2', '3']:
            try:
                if choice == '1':
                    number = int(input("输入十进制数: "))
                    target_base = int(input("目标进制 (2-36): "))
                    result = BaseConverter.convert_number(number, 10, target_base)
                    print(f"结果: {result}")
                
                elif choice == '2':
                    number = input("输入数字: ").strip()
                    source_base = int(input("源进制 (2-36): "))
                    result = BaseConverter.convert_number(number, source_base, 10)
                    print(f"结果: {result}")
                
                elif choice == '3':
                    number = input("输入数字: ").strip()
                    source_base = int(input("源进制 (2-36): "))
                    target_base = int(input("目标进制 (2-36): "))
                    result = BaseConverter.convert_number(number, source_base, target_base)
                    print(f"结果: {result}")
            
            except ValueError as e:
                print(color(f"输入错误: {e}", T.WARNING))
        else:
            print(color("无效选择", T.WARNING))

# ------------------ 单位换算模式 ------------------
def unit_convert_mode():
    """单位换算模式"""
    print(color("=== 单位换算模式 ===", T.HEADER))
    converter = UnitConverter()
    
    categories = list(converter.CONVERSIONS.keys())
    
    while True:
        print("\n可选类别:")
        for i, category in enumerate(categories, 1):
            print(f"{i}. {category}")
        print(f"{len(categories)+1}. 返回主菜单")
        
        try:
            choice = input("选择类别: ").strip()
            if choice == str(len(categories)+1):
                break
            
            category_idx = int(choice) - 1
            if 0 <= category_idx < len(categories):
                category = categories[category_idx]
                print(f"\n=== {category} 单位 ===")
                
                units = list(converter.CONVERSIONS[category].keys())
                print("可用单位:", ', '.join(units))
                
                value = float(input("输入数值: "))
                from_unit = input("从单位: ").strip()
                to_unit = input("到单位: ").strip()
                
                result = converter.convert(value, from_unit, to_unit, category)
                if isinstance(result, (int, float)):
                    print(f"{value} {from_unit} = {fmt_num(result)} {to_unit}")
                else:
                    print(color(result, T.WARNING))
            else:
                print(color("无效选择", T.WARNING))
        except (ValueError, KeyError) as e:
            print(color(f"输入错误: {e}", T.WARNING))

# ------------------ 方程求解模式 ------------------
def equation_mode():
    """方程求解模式"""
    print(color("=== 方程求解模式 ===", T.HEADER))
    
    while True:
        print("\n可选方程类型:")
        print("1. 线性方程 (ax + b = 0)")
        print("2. 二次方程 (ax² + bx + c = 0)")
        print("3. 返回主菜单")
        
        choice = input("选择方程类型: ").strip()
        
        if choice == '3':
            break
        
        try:
            if choice == '1':
                a = float(input("输入 a: "))
                b = float(input("输入 b: "))
                result = EquationSolver.solve_linear(a, b)
                print(color(result, T.OKGREEN))
                
            elif choice == '2':
                a = float(input("输入 a: "))
                b = float(input("输入 b: "))
                c = float(input("输入 c: "))
                result = EquationSolver.solve_quadratic(a, b, c)
                print(color(result, T.OKGREEN))
            else:
                print(color("无效选择", T.WARNING))
                
        except ValueError:
            print(color("请输入有效的数字", T.WARNING))

# ------------------ 矩阵计算模式 ------------------
def matrix_mode():
    """矩阵计算模式"""
    print(color("=== 矩阵计算模式 ===", T.HEADER))
    matrix_calc = MatrixCalculator()
    
    while True:
        print("\n可选操作:")
        print("1. 矩阵加法")
        print("2. 矩阵乘法")
        print("3. 计算行列式")
        print("4. 返回主菜单")
        
        choice = input("选择操作: ").strip()
        
        if choice == '4':
            break
        
        try:
            if choice in ['1', '2']:
                rows = int(input("矩阵行数: "))
                cols = int(input("矩阵列数: "))
                
                print("第一个矩阵:")
                matrix1 = matrix_calc.create_matrix(rows, cols)
                
                print("第二个矩阵:")
                matrix2 = matrix_calc.create_matrix(rows, cols)
                
                if choice == '1':
                    result = matrix_calc.matrix_add(matrix1, matrix2)
                else:
                    result = matrix_calc.matrix_multiply(matrix1, matrix2)
                
                if isinstance(result, str):
                    print(color(result, T.WARNING))
                else:
                    print(color("结果矩阵:", T.OKGREEN))
                    for row in result:
                        print([fmt_num(x) for x in row])
                        
            elif choice == '3':
                size = int(input("方阵大小 (2或3): "))
                matrix = matrix_calc.create_matrix(size, size)
                result = matrix_calc.matrix_determinant(matrix)
                
                if isinstance(result, str):
                    print(color(result, T.WARNING))
                else:
                    print(color(f"行列式 = {fmt_num(result)}", T.OKGREEN))
            else:
                print(color("无效选择", T.WARNING))
                
        except ValueError as e:
            print(color(f"输入错误: {e}", T.WARNING))

# ------------------ 单轮计算 ------------------
def calc_once():
    op = get_op()
    name, func, need_second, need_rad = OPS[op]
    # 常数直接返回
    if op in ('pi','e','tau','phi','rand'):
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

# ------------------ 主菜单 ------------------
def show_main_menu():
    """显示主菜单"""
    print(color("""
=== CATCALC v4.0 超级万能猫 ===
 1. 基础计算模式
 2. 统计计算模式
 3. 进制转换模式
 4. 单位换算模式
 5. 方程求解模式
 6. 矩阵计算模式
 7. 设置精度
 8. 查看历史
 9. 帮助信息
 0. 退出程序
================================
    """, T.HEADER))

def show_help():
    """显示帮助信息"""
    print(color("""
=== 帮助信息 ===
基础计算模式: 支持各种数学运算、三角函数、复数运算等
统计计算模式: 计算平均值、中位数、标准差等统计值
进制转换模式: 支持2-36进制之间的任意转换
单位换算模式: 支持长度、重量、温度、面积、体积、速度换算
方程求解模式: 求解线性和二次方程
矩阵计算模式: 支持矩阵加减乘法和行列式计算

特殊命令:
  prec - 设置显示精度
  hist - 查看历史记录
  help - 显示帮助信息
================""", T.OKCYAN))

# ------------------ 主循环 ------------------
def main():
    print(color(r"""
 /\_/\  
( o.o ) 
 > ^ <   CATCALC v4.0 超级万能猫上线！
 输入 help 查看所有功能，q 退出
    """, T.HEADER))
    
    while True:
        try:
            show_main_menu()
            cmd = input(color("请选择功能: ", T.BOLD)).strip().lower()
            
            if cmd in ('0', 'q','quit','exit','bye'):
                print(color("猫咪下班，喵呜~", T.OKBLUE)); break
            
            if cmd == '1' or cmd == '':
                calc_once()
            elif cmd == '2':
                stats_mode()
            elif cmd == '3':
                base_convert_mode()
            elif cmd == '4':
                unit_convert_mode()
            elif cmd == '5':
                equation_mode()
            elif cmd == '6':
                matrix_mode()
            elif cmd == '7':
                set_precision()
            elif cmd == '8':
                show_history()
            elif cmd == '9' or cmd == 'help':
                show_help()
            else:
                print(color("无效选择，请输入 0-9", T.WARNING))
                
        except (KeyboardInterrupt, EOFError):
            print(color("\n被强行撸猫，拜拜~", T.WARNING)); break
        except Exception as e:
            print(color(f"未知异常: {e}", T.FAIL))
            if input("打印详细堆栈？(y/n): ").lower()=='y':
                traceback.print_exc()

if __name__ == '__main__':
    main()
