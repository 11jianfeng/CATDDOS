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
import threading
import queue
import time
import concurrent.futures
from decimal import Decimal, getcontext
from datetime import datetime
import re
import signal

os.system('clear')
os.system('figlet CATCALC')

# ------------------ SymPy 符号计算库 ------------------
try:
    import sympy as sp
    from sympy import symbols, solve, diff, integrate, limit, simplify, expand, factor
    from sympy import sin, cos, tan, exp, log, sqrt, pi, E, I, oo, Matrix
    from sympy import Function, Eq, dsolve, laplace_transform, fourier_transform
    from sympy.plotting import plot, plot3d
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False
    print("SymPy库未安装，部分高级功能不可用。请运行: pip install sympy")

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

# ------------------ 多线程任务管理器 ------------------
class TaskManager:
    """多线程任务管理器"""
    def __init__(self, max_workers=4):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.tasks = {}  # task_id -> future
        self.results = {}  # task_id -> result
        self.task_counter = 0
        self.lock = threading.Lock()
    
    def submit_task(self, func, *args, **kwargs):
        """提交任务"""
        with self.lock:
            self.task_counter += 1
            task_id = self.task_counter
        
        future = self.executor.submit(func, *args, **kwargs)
        self.tasks[task_id] = future
        
        # 启动结果监控线程
        monitor_thread = threading.Thread(target=self._monitor_task, args=(task_id,))
        monitor_thread.daemon = True
        monitor_thread.start()
        
        return task_id
    
    def _monitor_task(self, task_id):
        """监控任务执行"""
        future = self.tasks[task_id]
        try:
            result = future.result(timeout=60)  # 60秒超时
            with self.lock:
                self.results[task_id] = ('completed', result)
        except concurrent.futures.TimeoutError:
            with self.lock:
                self.results[task_id] = ('timeout', None)
        except Exception as e:
            with self.lock:
                self.results[task_id] = ('error', str(e))
    
    def get_result(self, task_id):
        """获取任务结果"""
        with self.lock:
            if task_id in self.results:
                status, result = self.results[task_id]
                if status == 'completed':
                    return True, result
                elif status == 'timeout':
                    return False, "任务超时"
                elif status == 'error':
                    return False, f"任务错误: {result}"
            elif task_id in self.tasks:
                return None, "任务进行中..."
            else:
                return False, "任务ID不存在"
    
    def get_task_status(self, task_id):
        """获取任务状态"""
        with self.lock:
            if task_id in self.results:
                return self.results[task_id][0]
            elif task_id in self.tasks:
                return 'running'
            else:
                return 'not_found'
    
    def cleanup_completed(self):
        """清理已完成的任务"""
        with self.lock:
            completed_tasks = [tid for tid, (status, _) in self.results.items() 
                             if status in ['completed', 'timeout', 'error']]
            for tid in completed_tasks:
                if tid in self.tasks:
                    del self.tasks[tid]
                del self.results[tid]

# ------------------ SymPy 符号计算器 ------------------
class SymPyCalculator:
    """SymPy 符号计算器"""
    
    def __init__(self):
        self.symbols_dict = {}
        self.expressions = {}
    
    def create_symbols(self, symbol_names):
        """创建符号变量"""
        try:
            symbols_list = symbols(symbol_names)
            if isinstance(symbols_list, tuple):
                for sym in symbols_list:
                    self.symbols_dict[str(sym)] = sym
            else:
                self.symbols_dict[str(symbols_list)] = symbols_list
            return True, f"已创建符号: {symbol_names}"
        except Exception as e:
            return False, f"创建符号失败: {e}"
    
    def solve_equation(self, equation_str, variable_str):
        """求解方程"""
        try:
            if variable_str not in self.symbols_dict:
                return False, f"符号 {variable_str} 未定义"
            
            var = self.symbols_dict[variable_str]
            # 解析方程
            equation = self.parse_expression(equation_str)
            solutions = solve(equation, var)
            
            return True, solutions
        except Exception as e:
            return False, f"求解方程失败: {e}"
    
    def solve_equation_system(self, equations, variables):
        """求解方程组"""
        try:
            eq_list = []
            for eq_str in equations:
                eq = self.parse_expression(eq_str)
                if isinstance(eq, Eq):
                    eq_list.append(eq)
                else:
                    # 假设方程形式为 expr = 0
                    eq_list.append(Eq(eq, 0))
            
            var_list = [self.symbols_dict[var] for var in variables if var in self.symbols_dict]
            solutions = solve(eq_list, var_list)
            
            return True, solutions
        except Exception as e:
            return False, f"求解方程组失败: {e}"
    
    def calculate_derivative(self, expr_str, variable_str, order=1):
        """计算导数"""
        try:
            if variable_str not in self.symbols_dict:
                return False, f"符号 {variable_str} 未定义"
            
            expr = self.parse_expression(expr_str)
            var = self.symbols_dict[variable_str]
            
            derivative = diff(expr, var, order)
            return True, derivative
        except Exception as e:
            return False, f"计算导数失败: {e}"
    
    def calculate_integral(self, expr_str, variable_str, definite=None):
        """计算积分"""
        try:
            if variable_str not in self.symbols_dict:
                return False, f"符号 {variable_str} 未定义"
            
            expr = self.parse_expression(expr_str)
            var = self.symbols_dict[variable_str]
            
            if definite:
                # 定积分
                a, b = definite
                result = integrate(expr, (var, a, b))
            else:
                # 不定积分
                result = integrate(expr, var)
            
            return True, result
        except Exception as e:
            return False, f"计算积分失败: {e}"
    
    def calculate_limit(self, expr_str, variable_str, point):
        """计算极限"""
        try:
            if variable_str not in self.symbols_dict:
                return False, f"符号 {variable_str} 未定义"
            
            expr = self.parse_expression(expr_str)
            var = self.symbols_dict[variable_str]
            
            limit_result = limit(expr, var, point)
            return True, limit_result
        except Exception as e:
            return False, f"计算极限失败: {e}"
    
    def simplify_expression(self, expr_str):
        """简化表达式"""
        try:
            expr = self.parse_expression(expr_str)
            simplified = simplify(expr)
            return True, simplified
        except Exception as e:
            return False, f"简化表达式失败: {e}"
    
    def expand_expression(self, expr_str):
        """展开表达式"""
        try:
            expr = self.parse_expression(expr_str)
            expanded = expand(expr)
            return True, expanded
        except Exception as e:
            return False, f"展开表达式失败: {e}"
    
    def factor_expression(self, expr_str):
        """因式分解"""
        try:
            expr = self.parse_expression(expr_str)
            factored = factor(expr)
            return True, factored
        except Exception as e:
            return False, f"因式分解失败: {e}"
    
    def plot_function(self, expr_str, variable_str, range_x=(-10, 10)):
        """绘制函数图像"""
        try:
            if not SYMPY_AVAILABLE:
                return False, "SymPy绘图功能不可用"
            
            if variable_str not in self.symbols_dict:
                return False, f"符号 {variable_str} 未定义"
            
            expr = self.parse_expression(expr_str)
            var = self.symbols_dict[variable_str]
            
            # 创建图像
            p = plot(expr, (var, range_x[0], range_x[1]), show=False)
            p.show()
            return True, "图像已显示"
        except Exception as e:
            return False, f"绘制图像失败: {e}"
    
    def matrix_operations(self, operation, *matrix_data):
        """矩阵运算"""
        try:
            if operation == 'create':
                rows, cols = matrix_data[0], matrix_data[1]
                elements = matrix_data[2]
                matrix = Matrix(rows, cols, elements)
                return True, matrix
            
            elif operation == 'det':
                matrix = matrix_data[0]
                det = matrix.det()
                return True, det
            
            elif operation == 'inv':
                matrix = matrix_data[0]
                inv = matrix.inv()
                return True, inv
            
            elif operation == 'eigen':
                matrix = matrix_data[0]
                eigenvals = matrix.eigenvals()
                return True, eigenvals
            
            elif operation == 'multiply':
                matrix1, matrix2 = matrix_data[0], matrix_data[1]
                result = matrix1 * matrix2
                return True, result
            
        except Exception as e:
            return False, f"矩阵运算失败: {e}"
    
    def parse_expression(self, expr_str):
        """解析表达式字符串"""
        # 替换常用数学函数
        expr_str = expr_str.replace('^', '**')
        expr_str = expr_str.replace('sin', 'sp.sin')
        expr_str = expr_str.replace('cos', 'sp.cos')
        expr_str = expr_str.replace('tan', 'sp.tan')
        expr_str = expr_str.replace('log', 'sp.log')
        expr_str = expr_str.replace('exp', 'sp.exp')
        expr_str = expr_str.replace('sqrt', 'sp.sqrt')
        expr_str = expr_str.replace('pi', 'sp.pi')
        expr_str = expr_str.replace('e', 'sp.E')
        
        # 安全评估表达式
        safe_dict = {**self.symbols_dict, 'sp': sp}
        return eval(expr_str, {"__builtins__": {}}, safe_dict)
    
    def series_expansion(self, expr_str, variable_str, point=0, n=6):
        """泰勒级数展开"""
        try:
            if variable_str not in self.symbols_dict:
                return False, f"符号 {variable_str} 未定义"
            
            expr = self.parse_expression(expr_str)
            var = self.symbols_dict[variable_str]
            
            series_exp = sp.series(expr, var, point, n)
            return True, series_exp
        except Exception as e:
            return False, f"级数展开失败: {e}"

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
        self.lock = threading.Lock()
    
    def add_data(self, values):
        """添加数据"""
        with self.lock:
            self.data.extend([float(x) for x in values])
    
    def clear(self):
        """清空数据"""
        with self.lock:
            self.data = []
    
    def calculate_all(self):
        """计算所有统计值"""
        with self.lock:
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

# ------------------ SymPy 符号计算模式 ------------------
def sympy_mode():
    """SymPy 符号计算模式"""
    if not SYMPY_AVAILABLE:
        print(color("SymPy库未安装，无法使用符号计算功能", T.FAIL))
        return
    
    sympy_calc = SymPyCalculator()
    
    print(color("=== SymPy 符号计算模式 ===", T.HEADER))
    print("可用功能:")
    print("1. 创建符号变量")
    print("2. 求解方程")
    print("3. 求解方程组")
    print("4. 计算导数")
    print("5. 计算积分")
    print("6. 计算极限")
    print("7. 表达式简化")
    print("8. 表达式展开")
    print("9. 因式分解")
    print("10. 级数展开")
    print("11. 矩阵运算")
    print("12. 绘制函数图像")
    print("13. 查看已定义符号")
    print("14. 返回主菜单")
    
    while True:
        try:
            choice = input("\n选择符号计算功能: ").strip()
            
            if choice == '14':
                break
            
            if choice == '1':
                # 创建符号变量
                symbol_names = input("输入符号名称 (如: x y z): ").strip()
                success, result = sympy_calc.create_symbols(symbol_names)
                print(color(result, T.OKGREEN if success else T.WARNING))
            
            elif choice == '2':
                # 求解方程
                equation = input("输入方程 (如: x**2 - 4 = 0): ").strip()
                variable = input("求解变量: ").strip()
                success, result = sympy_calc.solve_equation(equation, variable)
                if success:
                    print(color(f"解: {result}", T.OKGREEN))
                else:
                    print(color(result, T.WARNING))
            
            elif choice == '3':
                # 求解方程组
                n = int(input("方程个数: "))
                equations = []
                for i in range(n):
                    eq = input(f"第{i+1}个方程: ").strip()
                    equations.append(eq)
                
                variables = input("求解变量 (空格分隔): ").strip().split()
                success, result = sympy_calc.solve_equation_system(equations, variables)
                if success:
                    print(color(f"解: {result}", T.OKGREEN))
                else:
                    print(color(result, T.WARNING))
            
            elif choice == '4':
                # 计算导数
                expr = input("输入表达式: ").strip()
                var = input("求导变量: ").strip()
                order = int(input("求导阶数 (默认1): ") or "1")
                success, result = sympy_calc.calculate_derivative(expr, var, order)
                if success:
                    print(color(f"导数: {result}", T.OKGREEN))
                else:
                    print(color(result, T.WARNING))
            
            elif choice == '5':
                # 计算积分
                expr = input("输入表达式: ").strip()
                var = input("积分变量: ").strip()
                definite = input("定积分范围 (如: 0 1，直接回车为不定积分): ").strip()
                if definite:
                    a, b = map(float, definite.split())
                    success, result = sympy_calc.calculate_integral(expr, var, (a, b))
                else:
                    success, result = sympy_calc.calculate_integral(expr, var)
                
                if success:
                    print(color(f"积分结果: {result}", T.OKGREEN))
                else:
                    print(color(result, T.WARNING))
            
            elif choice == '6':
                # 计算极限
                expr = input("输入表达式: ").strip()
                var = input("变量: ").strip()
                point = input("极限点 (如: 0, oo, -oo): ").strip()
                if point == 'oo':
                    point = oo
                elif point == '-oo':
                    point = -oo
                else:
                    point = float(point)
                
                success, result = sympy_calc.calculate_limit(expr, var, point)
                if success:
                    print(color(f"极限: {result}", T.OKGREEN))
                else:
                    print(color(result, T.WARNING))
            
            elif choice == '7':
                # 表达式简化
                expr = input("输入表达式: ").strip()
                success, result = sympy_calc.simplify_expression(expr)
                if success:
                    print(color(f"简化结果: {result}", T.OKGREEN))
                else:
                    print(color(result, T.WARNING))
            
            elif choice == '8':
                # 表达式展开
                expr = input("输入表达式: ").strip()
                success, result = sympy_calc.expand_expression(expr)
                if success:
                    print(color(f"展开结果: {result}", T.OKGREEN))
                else:
                    print(color(result, T.WARNING))
            
            elif choice == '9':
                # 因式分解
                expr = input("输入表达式: ").strip()
                success, result = sympy_calc.factor_expression(expr)
                if success:
                    print(color(f"因式分解: {result}", T.OKGREEN))
                else:
                    print(color(result, T.WARNING))
            
            elif choice == '10':
                # 级数展开
                expr = input("输入表达式: ").strip()
                var = input("展开变量: ").strip()
                point = float(input("展开点 (默认0): ") or "0")
                n = int(input("展开项数 (默认6): ") or "6")
                success, result = sympy_calc.series_expansion(expr, var, point, n)
                if success:
                    print(color(f"级数展开: {result}", T.OKGREEN))
                else:
                    print(color(result, T.WARNING))
            
            elif choice == '11':
                # 矩阵运算
                print("矩阵运算:")
                print("1. 创建矩阵")
                print("2. 计算行列式")
                print("3. 计算逆矩阵")
                print("4. 计算特征值")
                print("5. 矩阵乘法")
                
                matrix_choice = input("选择矩阵运算: ").strip()
                
                if matrix_choice == '1':
                    rows = int(input("行数: "))
                    cols = int(input("列数: "))
                    print("输入矩阵元素 (按行输入，空格分隔):")
                    elements = []
                    for i in range(rows):
                        row = input(f"第{i+1}行: ").strip().split()
                        elements.extend([float(x) for x in row])
                    
                    success, result = sympy_calc.matrix_operations('create', rows, cols, elements)
                    if success:
                        print(color(f"矩阵:\n{result}", T.OKGREEN))
                
                elif matrix_choice in ['2', '3', '4']:
                    # 需要先创建矩阵
                    rows = int(input("矩阵行数: "))
                    cols = int(input("矩阵列数: "))
                    print("输入矩阵元素:")
                    elements = []
                    for i in range(rows):
                        row = input(f"第{i+1}行: ").strip().split()
                        elements.extend([float(x) for x in row])
                    
                    success, matrix = sympy_calc.matrix_operations('create', rows, cols, elements)
                    if success:
                        if matrix_choice == '2':
                            success, result = sympy_calc.matrix_operations('det', matrix)
                            if success:
                                print(color(f"行列式: {result}", T.OKGREEN))
                        elif matrix_choice == '3':
                            success, result = sympy_calc.matrix_operations('inv', matrix)
                            if success:
                                print(color(f"逆矩阵:\n{result}", T.OKGREEN))
                        elif matrix_choice == '4':
                            success, result = sympy_calc.matrix_operations('eigen', matrix)
                            if success:
                                print(color(f"特征值: {result}", T.OKGREEN))
                
                elif matrix_choice == '5':
                    # 矩阵乘法
                    print("第一个矩阵:")
                    rows1 = int(input("行数: "))
                    cols1 = int(input("列数: "))
                    elements1 = []
                    for i in range(rows1):
                        row = input(f"第{i+1}行: ").strip().split()
                        elements1.extend([float(x) for x in row])
                    
                    print("第二个矩阵:")
                    rows2 = int(input("行数: "))
                    cols2 = int(input("列数: "))
                    elements2 = []
                    for i in range(rows2):
                        row = input(f"第{i+1}行: ").strip().split()
                        elements2.extend([float(x) for x in row])
                    
                    success1, matrix1 = sympy_calc.matrix_operations('create', rows1, cols1, elements1)
                    success2, matrix2 = sympy_calc.matrix_operations('create', rows2, cols2, elements2)
                    
                    if success1 and success2:
                        success, result = sympy_calc.matrix_operations('multiply', matrix1, matrix2)
                        if success:
                            print(color(f"乘积矩阵:\n{result}", T.OKGREEN))
            
            elif choice == '12':
                # 绘制函数图像
                expr = input("输入函数表达式: ").strip()
                var = input("变量名: ").strip()
                x_min = float(input("x最小值 (默认-10): ") or "-10")
                x_max = float(input("x最大值 (默认10): ") or "10")
                success, result = sympy_calc.plot_function(expr, var, (x_min, x_max))
                if success:
                    print(color(result, T.OKGREEN))
                else:
                    print(color(result, T.WARNING))
            
            elif choice == '13':
                # 查看已定义符号
                if sympy_calc.symbols_dict:
                    print(color("已定义符号:", T.OKGREEN))
                    for name, symbol in sympy_calc.symbols_dict.items():
                        print(f"  {name}: {symbol}")
                else:
                    print(color("尚未定义任何符号", T.WARNING))
            
            else:
                print(color("无效选择", T.WARNING))
                
        except Exception as e:
            print(color(f"发生错误: {e}", T.FAIL))

# ------------------ 历史记录 ------------------
HISTORY = []
HISTORY_LOCK = threading.Lock()

def record(expr, val):
    with HISTORY_LOCK:
        HISTORY.append(f"{expr} = {val}")
        if len(HISTORY) > 50: 
            HISTORY.pop(0)

def show_history():
    if not HISTORY:
        print(color("历史为空喵~", T.WARNING)); return
    print(color("===== 历史记录 =====", T.HEADER))
    for idx, line in enumerate(HISTORY, 1):
        print(f"{idx:02d}. {line}")
    print(color("====================", T.HEADER))

# ------------------ 输入/输出 ------------------
PREC = 6
PREC_LOCK = threading.Lock()

def set_precision():
    global PREC
    try:
        new_prec = int(input("保留小数位(0-15): "))
        with PREC_LOCK:
            PREC = new_prec
            getcontext().prec = PREC + 2
        print(color(f"精度已设置为 {PREC} 位", T.OKGREEN))
    except ValueError:
        print(color("非法数字，保持默认 6 位", T.WARNING))

def fmt_num(n):
    """漂亮地打印实数/复数（线程安全）"""
    with PREC_LOCK:
        current_prec = PREC
    
    if isinstance(n, complex):
        if abs(n.imag) < 1e-15: n = n.real
        elif abs(n.real) < 1e-15: n = n.imag*1j
    if isinstance(n, complex):
        return f"{n.real:.{current_prec}f} + {n.imag:.{current_prec}f}j"
    else:
        return f"{n:.{current_prec}f}".rstrip('0').rstrip('.')

# ------------------ 主菜单 ------------------
def show_main_menu():
    """显示主菜单"""
    sympy_status = "✓" if SYMPY_AVAILABLE else "✗"
    print(color(f"""
=== CATCALC v6.0 超级SymPy符号计算猫 ===
SymPy支持: {sympy_status}  (pip install sympy)
 1. 基础计算模式
 2. 统计计算模式 (多线程加速)
 3. 进制转换模式
 4. 单位换算模式
 5. 方程求解模式
 6. 矩阵计算模式
 7. 异步计算模式
 8. SymPy符号计算 (新!)
 9. 设置精度
10. 查看历史
11. 帮助信息
 0. 退出程序
=========================================
    """, T.HEADER))

def show_help():
    """显示帮助信息"""
    sympy_features = """
SymPy符号计算模式:
- 符号变量创建和管理
- 代数方程求解（包括方程组）
- 微积分运算（导数、积分、极限）
- 表达式简化、展开、因式分解
- 泰勒级数展开
- 矩阵运算（行列式、逆矩阵、特征值）
- 函数图像绘制""" if SYMPY_AVAILABLE else ""
    
    print(color(f"""
=== 帮助信息 ===
基础计算模式: 支持各种数学运算、三角函数、复数运算等
统计计算模式: 多线程加速计算统计值
进制转换模式: 支持2-36进制之间的任意转换
单位换算模式: 支持长度、重量、温度、面积、体积、速度换算
方程求解模式: 求解线性和二次方程
矩阵计算模式: 支持矩阵加减乘法和行列式计算
异步计算模式: 大数阶乘、斐波那契、素数计算、π计算等
{sympy_features}

多线程特性:
- 后台异步计算，不阻塞主界面
- 实时进度条显示
- 任务状态查询
- 并行加速统计计算

特殊命令:
  prec - 设置显示精度
  hist - 查看历史记录
  help - 显示帮助信息
================""", T.OKCYAN))

# ------------------ 主循环 ------------------
def main():
    # 创建任务管理器
    task_manager = TaskManager(max_workers=4)
    
    sympy_notice = "\n🧮 SymPy符号计算已启用！" if SYMPY_AVAILABLE else "\n⚠️  SymPy未安装，符号计算功能不可用"
    
    print(color(rf"""
 /\_/\  
( o.o ) 
 > ^ <   CATCALC v6.0 超级SymPy符号计算猫上线！
 输入 help 查看所有功能，q 退出
 💪 支持异步计算、多线程加速、符号计算！{sympy_notice}
    """, T.HEADER))
    
    # 定期清理已完成任务
    def cleanup_task():
        while True:
            time.sleep(60)  # 每分钟清理一次
            task_manager.cleanup_completed()
    
    cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()
    
    while True:
        try:
            show_main_menu()
            cmd = input(color("请选择功能: ", T.BOLD)).strip().lower()
            
            if cmd in ('0', 'q','quit','exit','bye'):
                print(color("猫咪下班，喵呜~ 正在清理后台任务...", T.OKBLUE))
                task_manager.executor.shutdown(wait=True)
                break
            
            if cmd == '1' or cmd == '':
                calc_once()
            elif cmd == '2':
                stats_mode_threaded()
            elif cmd == '3':
                base_convert_mode()
            elif cmd == '4':
                unit_convert_mode()
            elif cmd == '5':
                equation_mode()
            elif cmd == '6':
                matrix_mode()
            elif cmd == '7':
                async_calculation_mode(task_manager)
            elif cmd == '8':
                sympy_mode()
            elif cmd == '9':
                set_precision()
            elif cmd == '10':
                show_history()
            elif cmd == '11' or cmd == 'help':
                show_help()
            else:
                print(color("无效选择，请输入 0-11", T.WARNING))
                
        except (KeyboardInterrupt, EOFError):
            print(color("\n被强行撸猫，拜拜~", T.WARNING))
            task_manager.executor.shutdown(wait=True)
            break
        except Exception as e:
            print(color(f"未知异常: {e}", T.FAIL))
            if input("打印详细堆栈？(y/n): ").lower()=='y':
                traceback.print_exc()

if __name__ == '__main__':
    main()
