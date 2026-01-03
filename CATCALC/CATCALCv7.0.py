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

# ------------------ SymPy 符号计算库 ------------------
try:
    import sympy as sp
    from sympy import symbols, solve, diff, integrate, limit, simplify, expand, factor
    from sympy import sin, cos, tan, exp, log, sqrt, pi, E, I, oo, Matrix
    from sympy.plotting import plot, plot3d
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False
    print("SymPy库未安装喵~，部分高级功能不可用喵。请运行: pip install sympy喵！")

# ------------------ 猫娘彩色工具 ------------------
class T:
    """猫娘彩色终端很好玩的喵~"""
    HEADER = '\033[95m'      # 粉色 - 猫娘的可爱
    OKBLUE = '\033[94m'      # 蓝色 - 猫娘的冷静
    OKCYAN = '\033[96m'      # 青色 - 猫娘的清新
    OKGREEN = '\033[92m'     # 绿色 - 猫娘的活力
    WARNING = '\033[93m'     # 黄色 - 猫娘的提醒
    FAIL = '\033[91m'        # 红色 - 猫娘的担心
    ENDC = '\033[0m'         # 结束
    BOLD = '\033[1m'         # 粗体 - 猫娘的强调
    UNDERLINE = '\033[4m'    # 下划线 - 猫娘的重点

def color(txt, code): return f"{code}{txt}{T.ENDC}"

# ------------------ 猫娘表情库 ------------------
class CatgirlEmoji:
    """猫娘专用表情库喵~"""
    HAPPY = "(*≧▽≦)"
    EXCITED = "☆*: .｡. o(≧▽≦)o .｡.:*☆"
    THINKING = "(￣ω￣;)"
    SURPRISED = "（゜ロ゜）"
    SAD = "(｡•́︿•̀｡)"
    BLUSHING = "(*///▽///*)"
    CONFUSED = "(￣ω￣;)"
    DETERMINED = "（￣︶￣）↗"
    SLEEPY = "(￣o￣) zzZ"
    WINK = "(￣▽￣)ノ"
    LOVING = "(づ￣ ³￣)づ"
    PRAYING = "(｡>﹏<｡)"
    CELEBRATING = "♪(´▽｀)"
    CALCULATING = "(￣ー￣)ノ~~~~〜☆"
    COMFORT = "(｡>﹏<｡)♡"

# ------------------ 猫娘插件加载器 ------------------
PLUGINS = {}
def load_plugins():
    """猫娘动态加载插件喵~"""
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
                print(color(f"[插件] 加载 {fname} 失败了喵：{e}", T.WARNING))
    sys.path.remove(plug_dir)

# ------------------ 猫娘多线程任务管理器 ------------------
class CatgirlTaskManager:
    """猫娘多线程任务管理器喵~"""
    def __init__(self, max_workers=4):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.tasks = {}  # task_id -> future
        self.results = {}  # task_id -> result
        self.task_counter = 0
        self.lock = threading.Lock()
    
    def submit_task(self, func, *args, **kwargs):
        """提交任务喵~"""
        with self.lock:
            self.task_counter += 1
            task_id = self.task_counter
        
        future = self.executor.submit(func, *args, **kwargs)
        self.tasks[task_id] = future
        
        # 启动结果监控线程喵~
        monitor_thread = threading.Thread(target=self._monitor_task, args=(task_id,))
        monitor_thread.daemon = True
        monitor_thread.start()
        
        return task_id
    
    def _monitor_task(self, task_id):
        """监控任务执行的喵~"""
        future = self.tasks[task_id]
        try:
            result = future.result(timeout=60)  # 60秒超时喵~
            with self.lock:
                self.results[task_id] = ('completed', result)
        except concurrent.futures.TimeoutError:
            with self.lock:
                self.results[task_id] = ('timeout', None)
        except Exception as e:
            with self.lock:
                self.results[task_id] = ('error', str(e))
    
    def get_result(self, task_id):
        """获取任务结果喵~"""
        with self.lock:
            if task_id in self.results:
                status, result = self.results[task_id]
                if status == 'completed':
                    return True, result
                elif status == 'timeout':
                    return False, "任务超时了喵~"
                elif status == 'error':
                    return False, f"任务出错了喵~: {result}"
            elif task_id in self.tasks:
                return None, "任务还在努力进行中喵~..."
            else:
                return False, "找不到这个任务ID喵~"
    
    def get_task_status(self, task_id):
        """获取任务状态喵~"""
        with self.lock:
            if task_id in self.results:
                return self.results[task_id][0]
            elif task_id in self.tasks:
                return 'running'
            else:
                return 'not_found'
    
    def cleanup_completed(self):
        """清理已完成的任务喵~"""
        with self.lock:
            completed_tasks = [tid for tid, (status, _) in self.results.items() 
                             if status in ['completed', 'timeout', 'error']]
            for tid in completed_tasks:
                if tid in self.tasks:
                    del self.tasks[tid]
                del self.results[tid]

# ------------------ 猫娘进度条 ------------------
class CatgirlProgressBar:
    """猫娘专用进度条喵~"""
    def __init__(self, total=100, width=50):
        self.total = total
        self.width = width
        self.current = 0
        self.start_time = None
        self.lock = threading.Lock()
    
    def start(self):
        """开始进度条喵~"""
        self.start_time = time.time()
        self.update(0)
    
    def update(self, current):
        """更新进度喵~"""
        with self.lock:
            self.current = current
            percent = current / self.total
            filled = int(self.width * percent)
            bar = '♡' * filled + '·' * (self.width - filled)
            
            elapsed = time.time() - self.start_time if self.start_time else 0
            eta = (elapsed / current * (self.total - current)) if current > 0 else 0
            
            print(f'\r|{bar}| {percent:.1%} 预计剩余时间: {eta:.1f}秒 ', end='', flush=True)
    
    def finish(self):
        """完成进度条喵~"""
        self.update(self.total)
        print()  # 换行
        elapsed = time.time() - self.start_time if self.start_time else 0
        print(f"完成喵~! 用时: {elapsed:.2f}秒 {CatgirlEmoji.CELEBRATING}")

# ------------------ 猫娘异步计算装饰器 ------------------
def async_calculation_with_moe(description="计算中喵~"):
    """带萌感的异步计算装饰器喵~"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # 创建猫娘进度条
            progress = CatgirlProgressBar(total=100)
            
            def calc_with_moe_progress():
                print(f"{CatgirlEmoji.CALCULATING} 开始{description}...")
                progress.start()
                # 模拟进度更新喵~
                for i in range(0, 101, 10):
                    time.sleep(0.1 + random.uniform(0, 0.1))  # 随机时间增加萌感
                    progress.update(i)
                progress.finish()
                return func(*args, **kwargs)
            
            return calc_with_moe_progress()
        return wrapper
    return decorator

# ------------------ 猫娘高性能计算 ------------------
class CatgirlHighPerformanceCalculator:
    """猫娘高性能计算器喵~"""
    
    @staticmethod
    @async_calculation_with_moe("计算大数阶乘喵~")
    def large_factorial(n):
        """大数阶乘计算喵~"""
        if n < 0:
            return cmath.gamma(n + 1)
        result = 1
        for i in range(1, int(n) + 1):
            result *= i
            if i % 1000 == 0:  # 每1000步让出CPU喵~
                time.sleep(0.001)
        return result
    
    @staticmethod
    @async_calculation_with_moe("计算斐波那契数列喵~")
    def fibonacci_sequence(n):
        """计算斐波那契数列喵~"""
        if n <= 0:
            return []
        elif n == 1:
            return [0]
        elif n == 2:
            return [0, 1]
        
        sequence = [0, 1]
        for i in range(2, n):
            next_num = sequence[i-1] + sequence[i-2]
            sequence.append(next_num)
            if i % 100 == 0:  # 每100步让出CPU喵~
                time.sleep(0.001)
        return sequence
    
    @staticmethod
    @async_calculation_with_moe("计算素数喵~")
    def prime_numbers(limit):
        """计算素数喵~"""
        if limit < 2:
            return []
        
        primes = []
        for num in range(2, limit + 1):
            is_prime = True
            for i in range(2, int(math.sqrt(num)) + 1):
                if num % i == 0:
                    is_prime = False
                    break
            if is_prime:
                primes.append(num)
            
            if num % 1000 == 0:  # 每1000个数让出CPU喵~
                time.sleep(0.001)
        
        return primes
    
    @staticmethod
    @async_calculation_with_moe("计算π的近似值喵~")
    def calculate_pi(precision):
        """使用莱布尼茨公式计算π喵~"""
        pi_approx = 0
        sign = 1
        
        for i in range(precision):
            term = sign / (2 * i + 1)
            pi_approx += term
            sign *= -1
            
            if i % 10000 == 0 and i > 0:  # 每10000步让出CPU喵~
                time.sleep(0.001)
        
        return pi_approx * 4

# ------------------ 猫娘SymPy符号计算器 ------------------
class CatgirlSymPyCalculator:
    """猫娘SymPy符号计算器喵~"""
    
    def __init__(self):
        self.symbols_dict = {}
        self.expressions = {}
    
    def create_symbols(self, symbol_names):
        """创建符号变量喵~"""
        try:
            symbols_list = symbols(symbol_names)
            if isinstance(symbols_list, tuple):
                for sym in symbols_list:
                    self.symbols_dict[str(sym)] = sym
            else:
                self.symbols_dict[str(symbols_list)] = symbols_list
            return True, f"已经创建好符号了喵: {symbol_names} {CatgirlEmoji.HAPPY}"
        except Exception as e:
            return False, f"创建符号失败了喵...: {e} {CatgirlEmoji.SAD}"
    
    def solve_equation(self, equation_str, variable_str):
        """求解方程喵~"""
        try:
            if variable_str not in self.symbols_dict:
                return False, f"符号 {variable_str} 还没有定义喵... {CatgirlEmoji.CONFUSED}"
            
            var = self.symbols_dict[variable_str]
            # 解析方程
            equation = self.parse_expression(equation_str)
            solutions = solve(equation, var)
            
            return True, solutions
        except Exception as e:
            return False, f"求解方程遇到了困难喵...: {e} {CatgirlEmoji.THINKING}"
    
    def solve_equation_system(self, equations, variables):
        """求解方程组喵~"""
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
            return False, f"求解方程组失败了喵...: {e} {CatgirlEmoji.SAD}"
    
    def calculate_derivative(self, expr_str, variable_str, order=1):
        """计算导数喵~"""
        try:
            if variable_str not in self.symbols_dict:
                return False, f"符号 {variable_str} 还没有定义喵... {CatgirlEmoji.CONFUSED}"
            
            expr = self.parse_expression(expr_str)
            var = self.symbols_dict[variable_str]
            
            derivative = diff(expr, var, order)
            return True, derivative
        except Exception as e:
            return False, f"计算导数出错了喵...: {e} {CatgirlEmoji.THINKING}"
    
    def calculate_integral(self, expr_str, variable_str, definite=None):
        """计算积分喵~"""
        try:
            if variable_str not in self.symbols_dict:
                return False, f"符号 {variable_str} 还没有定义喵... {CatgirlEmoji.CONFUSED}"
            
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
            return False, f"计算积分遇到了问题喵...: {e} {CatgirlEmoji.SAD}"
    
    def calculate_limit(self, expr_str, variable_str, point):
        """计算极限喵~"""
        try:
            if variable_str not in self.symbols_dict:
                return False, f"符号 {variable_str} 还没有定义喵... {CatgirlEmoji.CONFUSED}"
            
            expr = self.parse_expression(expr_str)
            var = self.symbols_dict[variable_str]
            
            limit_result = limit(expr, var, point)
            return True, limit_result
        except Exception as e:
            return False, f"计算极限失败了喵...: {e} {CatgirlEmoji.THINKING}"
    
    def simplify_expression(self, expr_str):
        """简化表达式喵~"""
        try:
            expr = self.parse_expression(expr_str)
            simplified = simplify(expr)
            return True, simplified
        except Exception as e:
            return False, f"简化表达式出错了喵...: {e} {CatgirlEmoji.SAD}"
    
    def expand_expression(self, expr_str):
        """展开表达式喵~"""
        try:
            expr = self.parse_expression(expr_str)
            expanded = expand(expr)
            return True, expanded
        except Exception as e:
            return False, f"展开表达式失败了喵...: {e} {CatgirlEmoji.SAD}"
    
    def factor_expression(self, expr_str):
        """因式分解喵~"""
        try:
            expr = self.parse_expression(expr_str)
            factored = factor(expr)
            return True, factored
        except Exception as e:
            return False, f"因式分解遇到了问题喵...: {e} {CatgirlEmoji.THINKING}"
    
    def plot_function(self, expr_str, variable_str, range_x=(-10, 10)):
        """绘制函数图像喵~"""
        try:
            if not SYMPY_AVAILABLE:
                return False, "SymPy绘图功能不可用喵..."
            
            if variable_str not in self.symbols_dict:
                return False, f"符号 {variable_str} 还没有定义喵... {CatgirlEmoji.CONFUSED}"
            
            expr = self.parse_expression(expr_str)
            var = self.symbols_dict[variable_str]
            
            # 创建图像
            p = plot(expr, (var, range_x[0], range_x[1]), show=False)
            p.show()
            return True, f"图像已经显示出来了喵~ {CatgirlEmoji.HAPPY}"
        except Exception as e:
            return False, f"绘制图像失败了喵...: {e} {CatgirlEmoji.SAD}"
    
    def series_expansion(self, expr_str, variable_str, point=0, n=6):
        """泰勒级数展开喵~"""
        try:
            if variable_str not in self.symbols_dict:
                return False, f"符号 {variable_str} 还没有定义喵... {CatgirlEmoji.CONFUSED}"
            
            expr = self.parse_expression(expr_str)
            var = self.symbols_dict[variable_str]
            
            series_exp = sp.series(expr, var, point, n)
            return True, series_exp
        except Exception as e:
            return False, f"级数展开出错了喵...: {e} {CatgirlEmoji.THINKING}"
    
    def parse_expression(self, expr_str):
        """解析表达式字符串喵~"""
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

# ------------------ 猫娘统计计算器 ------------------
class CatgirlStatsCalculator:
    """猫娘统计计算器喵~"""
    def __init__(self):
        self.data = []
        self.lock = threading.Lock()
    
    def add_data(self, values):
        """添加数据喵~"""
        with self.lock:
            self.data.extend([float(x) for x in values])
    
    def clear(self):
        """清空数据喵~"""
        with self.lock:
            self.data = []
    
    def calculate_all(self):
        """计算所有统计值喵~"""
        with self.lock:
            if not self.data:
                return None
            
            n = len(self.data)
            mean = statistics.mean(self.data)
            median = statistics.median(self.data)
            try:
                mode = statistics.mode(self.data)
            except statistics.StatisticsError:
                mode = "没有众数喵~"
            
            std_dev = statistics.stdev(self.data) if n > 1 else 0
            variance = statistics.variance(self.data) if n > 1 else 0
            min_val = min(self.data)
            max_val = max(self.data)
            range_val = max_val - min_val
            
            return {
                '数据个数': n,
                '平均值': mean,
                '中位数': median,
                '众数': mode,
                '标准差': std_dev,
                '方差': variance,
                '最小值': min_val,
                '最大值': max_val,
                '极差': range_val
            }

# ------------------ 猫娘对话系统 ------------------
class CatgirlDialog:
    """猫娘对话系统喵~"""
    
    @staticmethod
    def greet():
        """打招呼喵~"""
        greetings = [
            f"喵呜~ 欢迎来到猫娘计算器喵！{CatgirlEmoji.HAPPY}",
            f"主人好呀~ 猫娘来帮你计算了喵！{CatgirlEmoji.EXCITED}",
            f"喵~ 今天也要好好计算哦！{CatgirlEmoji.WINK}",
            f"猫娘计算器启动成功喵！{CatgirlEmoji.CELEBRATING}"
        ]
        return random.choice(greetings)
    
    @staticmethod
    def encourage():
        """鼓励用语喵~"""
        encouragements = [
            f"计算得很棒喵！{CatgirlEmoji.HAPPY}",
            f"主人真厉害喵！{CatgirlEmoji.EXCITED}",
            f"一起加油喵！{CatgirlEmoji.DETERMINED}",
            f"猫娘为你加油喵！{CatgirlEmoji.PRAYING}"
        ]
        return random.choice(encouragements)
    
    @staticmethod
    def comfort():
        """安慰用语喵~"""
        comforts = [
            f"没关系的喵，重新来过就好了喵~{CatgirlEmoji.COMFORT}",
            f"猫娘相信主人一定可以的喵！{CatgirlEmoji.PRAYING}",
            f"小小的失误不算什么喵~{CatgirlEmoji.WINK}",
            f"猫娘会一直陪伴主人的喵~{CatgirlEmoji.LOVING}"
        ]
        return random.choice(comforts)
    
    @staticmethod
    def sleepy():
        """困倦用语喵~"""
        sleepys = [
            f"猫娘有点困了喵...{CatgirlEmoji.SLEEPY}",
            f"喵呜~ 需要休息一会喵...{CatgirlEmoji.SLEEPY}",
            f"计算得好累喵，让猫娘休息一下喵~{CatgirlEmoji.SLEEPY}"
        ]
        return random.choice(sleepys)

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

# ------------------ 猫娘历史记录 ------------------
HISTORY = []
HISTORY_LOCK = threading.Lock()

def record(expr, val):
    with HISTORY_LOCK:
        HISTORY.append(f"{expr} = {val}")
        if len(HISTORY) > 50: 
            HISTORY.pop(0)

def show_history():
    if not HISTORY:
        print(color(f"历史记录还是空空的喵~{CatgirlEmoji.SAD}", T.WARNING))
        return
    print(color(f"===== 猫娘的历史记录 ===== {CatgirlEmoji.HAPPY}", T.HEADER))
    for idx, line in enumerate(HISTORY, 1):
        print(f"{idx:02d}. {line}")
    print(color("======================", T.HEADER))

# ------------------ 猫娘输入输出 ------------------
PREC = 6
PREC_LOCK = threading.Lock()

def set_precision():
    """设置精度喵~"""
    global PREC
    try:
        new_prec = int(input("要保留几位小数喵？(0-15): "))
        with PREC_LOCK:
            PREC = new_prec
            getcontext().prec = PREC + 2
        print(color(f"精度已经设置为 {PREC} 位了喵！{CatgirlEmoji.HAPPY}", T.OKGREEN))
    except ValueError:
        print(color(f"输入的不是有效数字喵，保持默认6位喵~{CatgirlEmoji.SAD}", T.WARNING))

def fmt_num(n):
    """猫娘风格数字格式化喵~"""
    with PREC_LOCK:
        current_prec = PREC
    
    if isinstance(n, complex):
        if abs(n.imag) < 1e-15: n = n.real
        elif abs(n.real) < 1e-15: n = n.imag*1j
    if isinstance(n, complex):
        return f"{n.real:.{current_prec}f} + {n.imag:.{current_prec}f}i"
    else:
        return f"{n:.{current_prec}f}".rstrip('0').rstrip('.')

def get_number(prompt):
    """猫娘风格获取数字喵~"""
    while True:
        try:
            txt = input(color(prompt, T.OKCYAN)).strip()
            if txt.lower() == 'pi':
                print(f"{CatgirlEmoji.EXCITED} 哇，是π喵！")
                return math.pi
            if txt.lower() == 'e':
                print(f"{CatgirlEmoji.EXCITED} 是自然常数e喵！")
                return math.e
            if txt.lower() == 'phi':
                print(f"{CatgirlEmoji.EXCITED} 是黄金比例φ喵！")
                return (1 + math.sqrt(5)) / 2
            return float(txt)
        except ValueError:
            print(color(f"喵？这个不是有效数字喵，重新输入好不好喵~{CatgirlEmoji.CONFUSED}", T.WARNING))

def get_op():
    """猫娘风格获取运算符喵~"""
    symbols = ' '.join(OPS.keys())
    while True:
        op = input(color(f"选择运算符喵 ({symbols}) 或者输入 hist 查看历史喵: ", T.OKCYAN)).strip().lower()
        if op == 'hist':
            show_history()
            continue
        if op in OPS:
            return op
        print(color(f"喵娘不认识这个符号喵，重新试试好不好喵~{CatgirlEmoji.CONFUSED}", T.WARNING))

def angle_mode():
    """猫娘风格角度模式选择喵~"""
    while True:
        m = input("要选择弧度(r)还是角度(d)喵？[r/d]: ").strip().lower()
        if m in ('r','rad','弧度'):
            print(f"{CatgirlEmoji.HAPPY} 好的喵，用弧度喵~")
            return True
        if m in ('d','deg','角度','°'):
            print(f"{CatgirlEmoji.HAPPY} 好的喵，用角度喵~")
            return False
        print(color(f"输入 r 或者 d 喵，主人最可爱了喵~{CatgirlEmoji.BLUSHING}", T.WARNING))

# ------------------ 基础计算模式 ------------------
def calc_once():
    """单轮计算（猫娘版）喵~"""
    op = get_op()
    name, func, need_second, need_rad = OPS[op]
    # 常数直接返回
    if op in ('pi','e','tau','phi','rand'):
        val = func()
        print(color(f"常数 {name} = {fmt_num(val)} {CatgirlEmoji.EXCITED}", T.OKGREEN))
        record(name, val)
        return

    a = get_number("输入第一个数字喵: ")
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
        print(color(f"出错了喵: {e} {CatgirlEmoji.SAD}", T.FAIL))
        print(CatgirlDialog.comfort())
        return

    # 打印与记录
    expr = f"{a} {op} {b}" if need_second else f"{op}{a}"
    print(color(f"结果: {expr} = {fmt_num(result)} {CatgirlEmoji.EXCITED}", T.OKGREEN))
    record(expr, result)
    print(CatgirlDialog.encourage())

# ------------------ 统计计算模式 ------------------
def stats_mode():
    """统计计算模式（猫娘版）喵~"""
    stats_calc = CatgirlStatsCalculator()
    print(color(f"=== 猫娘统计计算模式 === {CatgirlEmoji.EXCITED}", T.HEADER))
    print("输入数据喵 (用空格分隔，输入空行结束):")
    
    while True:
        data_input = input("数据喵: ").strip()
        if not data_input:
            break
        try:
            values = [float(x) for x in data_input.split()]
            stats_calc.add_data(values)
            print(f"已添加 {len(values)} 个数据点喵~")
        except ValueError:
            print(color(f"请输入有效的数字喵~{CatgirlEmoji.CONFUSED}", T.WARNING))
    
    if not stats_calc.data:
        print(color(f"没有输入数据喵~{CatgirlEmoji.SAD}", T.WARNING))
        return
    
    results = stats_calc.calculate_all()
    if results:
        print(color(f"=== 猫娘的统计结果 === {CatgirlEmoji.HAPPY}", T.OKGREEN))
        for key, value in results.items():
            print(f"{key}: {fmt_num(value)}")

# ------------------ 进制转换模式 ------------------
def base_convert_mode():
    """进制转换模式（猫娘版）喵~"""
    print(color(f"=== 猫娘进制转换模式 === {CatgirlEmoji.EXCITED}", T.HEADER))
    
    while True:
        print("\n可以选的操作喵:")
        print("1. 十进制 → 其他进制喵")
        print("2. 其他进制 → 十进制喵") 
        print("3. 任意进制互转喵")
        print("4. 返回主菜单喵")
        
        choice = input("选择操作喵: ").strip()
        
        if choice == '4':
            print(f"{CatgirlEmoji.WINK} 好的喵，返回主菜单喵~")
            break
        
        if choice in ['1', '2', '3']:
            try:
                if choice == '1':
                    number = int(input("输入十进制数喵: "))
                    target_base = int(input("目标进制喵 (2-36): "))
                    result = BaseConverter.convert_number(number, 10, target_base)
                    print(f"结果喵: {result}")
                
                elif choice == '2':
                    number = input("输入数字喵: ").strip()
                    source_base = int(input("源进制喵 (2-36): "))
                    result = BaseConverter.convert_number(number, source_base, 10)
                    print(f"结果喵: {result}")
                
                elif choice == '3':
                    number = input("输入数字喵: ").strip()
                    source_base = int(input("源进制喵 (2-36): "))
                    target_base = int(input("目标进制喵 (2-36): "))
                    result = BaseConverter.convert_number(number, source_base, target_base)
                    print(f"结果喵: {result}")
            
            except ValueError as e:
                print(color(f"输入错误了喵: {e} {CatgirlEmoji.SAD}", T.WARNING))
        else:
            print(color(f"喵娘不明白这个选择喵，重新选好不好喵~{CatgirlEmoji.CONFUSED}", T.WARNING))

# ------------------ 单位换算模式 ------------------
def unit_convert_mode():
    """单位换算模式（猫娘版）喵~"""
    print(color(f"=== 猫娘单位换算模式 === {CatgirlEmoji.EXCITED}", T.HEADER))
    converter = UnitConverter()
    
    categories = list(converter.CONVERSIONS.keys())
    
    while True:
        print("\n可以选的类别喵:")
        for i, category in enumerate(categories, 1):
            print(f"{i}. {category}喵")
        print(f"{len(categories)+1}. 返回主菜单喵")
        
        try:
            choice = input("选择类别喵: ").strip()
            if choice == str(len(categories)+1):
                print(f"{CatgirlEmoji.WINK} 好的喵，返回主菜单喵~")
                break
            
            category_idx = int(choice) - 1
            if 0 <= category_idx < len(categories):
                category = categories[category_idx]
                print(f"\n=== {category} 单位喵 ===")
                
                units = list(converter.CONVERSIONS[category].keys())
                print("可用单位喵:", ', '.join(units))
                
                value = float(input("输入数值喵: "))
                from_unit = input("从哪个单位喵？: ").strip()
                to_unit = input("到哪个单位喵？: ").strip()
                
                result = converter.convert(value, from_unit, to_unit, category)
                if isinstance(result, (int, float)):
                    print(f"{value} {from_unit} = {fmt_num(result)} {to_unit} {CatgirlEmoji.HAPPY}")
                else:
                    print(color(result, T.WARNING))
            else:
                print(color(f"无效选择喵，重新选好不好喵~{CatgirlEmoji.CONFUSED}", T.WARNING))
        except (ValueError, KeyError) as e:
            print(color(f"输入错误了喵: {e} {CatgirlEmoji.SAD}", T.WARNING))

# ------------------ 方程求解模式 ------------------
def equation_mode():
    """方程求解模式（猫娘版）喵~"""
    print(color(f"=== 猫娘方程求解模式 === {CatgirlEmoji.EXCITED}", T.HEADER))
    
    while True:
        print("\n可以选的方程类型喵:")
        print("1. 线性方程喵 (ax + b = 0)")
        print("2. 二次方程喵 (ax² + bx + c = 0)")
        print("3. 返回主菜单喵")
        
        choice = input("选择方程类型喵: ").strip()
        
        if choice == '3':
            print(f"{CatgirlEmoji.WINK} 好的喵，返回主菜单喵~")
            break
        
        try:
            if choice == '1':
                a = float(input("输入 a 喵: "))
                b = float(input("输入 b 喵: "))
                result = EquationSolver.solve_linear(a, b)
                print(color(result, T.OKGREEN))
                
            elif choice == '2':
                a = float(input("输入 a 喵: "))
                b = float(input("输入 b 喵: "))
                c = float(input("输入 c 喵: "))
                result = EquationSolver.solve_quadratic(a, b, c)
                print(color(result, T.OKGREEN))
            else:
                print(color(f"无效选择喵，重新选好不好喵~{CatgirlEmoji.CONFUSED}", T.WARNING))
                
        except ValueError:
            print(color(f"请输入有效的数字喵~{CatgirlEmoji.SAD}", T.WARNING))

# ------------------ 矩阵计算模式 ------------------
def matrix_mode():
    """矩阵计算模式（猫娘版）喵~"""
    print(color(f"=== 猫娘矩阵计算模式 === {CatgirlEmoji.EXCITED}", T.HEADER))
    matrix_calc = MatrixCalculator()
    
    while True:
        print("\n可以选的操作喵:")
        print("1. 矩阵加法喵")
        print("2. 矩阵乘法喵")
        print("3. 计算行列式喵")
        print("4. 返回主菜单喵")
        
        choice = input("选择操作喵: ").strip()
        
        if choice == '4':
            print(f"{CatgirlEmoji.WINK} 好的喵，返回主菜单喵~")
            break
        
        try:
            if choice in ['1', '2']:
                rows = int(input("矩阵行数喵: "))
                cols = int(input("矩阵列数喵: "))
                
                print("第一个矩阵喵:")
                matrix1 = matrix_calc.create_matrix(rows, cols)
                
                print("第二个矩阵喵:")
                matrix2 = matrix_calc.create_matrix(rows, cols)
                
                if choice == '1':
                    result = matrix_calc.matrix_add(matrix1, matrix2)
                else:
                    result = matrix_calc.matrix_multiply(matrix1, matrix2)
                
                if isinstance(result, str):
                    print(color(result, T.WARNING))
                else:
                    print(color("结果矩阵喵:", T.OKGREEN))
                    for row in result:
                        print([fmt_num(x) for x in row])
                        print(CatgirlDialog.encourage())
                        
            elif choice == '3':
                size = int(input("方阵大小喵 (2或3): "))
                matrix = matrix_calc.create_matrix(size, size)
                result = matrix_calc.matrix_determinant(matrix)
                
                if isinstance(result, str):
                    print(color(result, T.WARNING))
                else:
                    print(color(f"行列式 = {fmt_num(result)} {CatgirlEmoji.HAPPY}", T.OKGREEN))
            else:
                print(color(f"无效选择喵，重新选好不好喵~{CatgirlEmoji.CONFUSED}", T.WARNING))
                
        except ValueError as e:
            print(color(f"输入错误了喵: {e} {CatgirlEmoji.SAD}", T.WARNING))

# ------------------ 异步计算模式 ------------------
def async_calculation_mode(task_manager):
    """异步计算模式（猫娘版）喵~"""
    print(color(f"=== 猫娘异步计算模式 === {CatgirlEmoji.EXCITED}", T.HEADER))
    print("可以用的异步计算喵:")
    print("1. 大数阶乘喵")
    print("2. 斐波那契数列喵")
    print("3. 素数计算喵")
    print("4. π的近似值喵")
    print("5. 查看任务状态喵")
    print("6. 返回主菜单喵")
    
    while True:
        choice = input("\n选择异步计算类型喵: ").strip()
        
        if choice == '6':
            print(f"{CatgirlEmoji.WINK} 好的喵，返回主菜单喵~")
            break
        
        if choice == '5':
            # 查看任务状态
            task_id = input("输入任务ID喵: ").strip()
            try:
                task_id = int(task_id)
                completed, result = task_manager.get_result(task_id)
                if completed is None:
                    print(color(f"任务{task_id}: {result}", T.WARNING))
                elif completed:
                    print(color(f"任务{task_id}结果喵: {fmt_num(result)} {CatgirlEmoji.HAPPY}", T.OKGREEN))
                else:
                    print(color(f"任务{task_id}错误喵: {result}", T.FAIL))
            except ValueError:
                print(color(f"无效的任务ID喵~{CatgirlEmoji.CONFUSED}", T.WARNING))
            continue
        
        try:
            if choice == '1':
                n = float(input("输入阶乘数字喵: "))
                print(color("提交大数阶乘计算任务喵...", T.OKCYAN))
                task_id = task_manager.submit_task(CatgirlHighPerformanceCalculator.large_factorial, n)
                print(color(f"任务已提交，ID: {task_id} {CatgirlEmoji.HAPPY}", T.OKGREEN))
                
            elif choice == '2':
                n = int(input("输入斐波那契数列长度喵: "))
                print(color("提交斐波那契数列计算任务喵...", T.OKCYAN))
                task_id = task_manager.submit_task(CatgirlHighPerformanceCalculator.fibonacci_sequence, n)
                print(color(f"任务已提交，ID: {task_id} {CatgirlEmoji.HAPPY}", T.OKGREEN))
                
            elif choice == '3':
                limit = int(input("输入素数上限喵: "))
                print(color("提交素数计算任务喵...", T.OKCYAN))
                task_id = task_manager.submit_task(CatgirlHighPerformanceCalculator.prime_numbers, limit)
                print(color(f"任务已提交，ID: {task_id} {CatgirlEmoji.HAPPY}", T.OKGREEN))
                
            elif choice == '4':
                precision = int(input("输入π的计算精度喵 (步数): "))
                print(color("提交π计算任务喵...", T.OKCYAN))
                task_id = task_manager.submit_task(CatgirlHighPerformanceCalculator.calculate_pi, precision)
                print(color(f"任务已提交，ID: {task_id} {CatgirlEmoji.HAPPY}", T.OKGREEN))
            else:
                print(color(f"喵娘不明白这个选择喵，重新选好不好喵~{CatgirlEmoji.CONFUSED}", T.WARNING))
                
        except ValueError:
            print(color(f"请输入有效的数字喵~{CatgirlEmoji.SAD}", T.WARNING))

# ------------------ 猫娘主菜单 ------------------
def show_main_menu():
    """显示猫娘主菜单喵~"""
    sympy_status = "✓" if SYMPY_AVAILABLE else "✗"
    menu = f"""
=== 猫娘计算器 v7.0 超萌模式 === {CatgirlEmoji.EXCITED}
SymPy符号计算: {sympy_status} (pip install sympy喵~)
 1. 基础计算模式 (喵呜~)
 2. 统计计算模式 (多线程加速喵~)
 3. 进制转换模式 (喵喵~)
 4. 单位换算模式 (喵呜喵呜~)
 5. 方程求解模式 (喵~)
 6. 矩阵计算模式 (喵呜~)
 7. 异步计算模式 (超快喵~)
 8. SymPy符号计算 (新功能喵~)
 9. 设置精度 (喵呜~)
10. 查看历史记录 (喵~)
11. 帮助信息 (喵呜喵呜~)
 0. 退出程序 (不要走喵~)
===================================== {CatgirlEmoji.PRAYING}
    """
    print(color(menu, T.HEADER))

def show_help():
    """显示猫娘帮助信息喵~"""
    sympy_features = f"""
SymPy符号计算模式喵:
- 符号变量创建和管理喵~
- 代数方程求解（包括方程组）喵~
- 微积分运算（导数、积分、极限）喵~
- 表达式简化、展开、因式分解喵~
- 泰勒级数展开喵~
- 矩阵运算（行列式、逆矩阵、特征值）喵~
- 函数图像绘制喵~""" if SYMPY_AVAILABLE else ""
    
    help_text = f"""
=== 猫娘帮助信息喵~ === {CatgirlEmoji.HAPPY}
基础计算模式喵: 支持各种数学运算、三角函数、复数运算等喵~
统计计算模式喵: 多线程加速计算统计值喵~
进制转换模式喵: 支持2-36进制之间的任意转换喵~
单位换算模式喵: 支持长度、重量、温度、面积、体积、速度换算喵~
方程求解模式喵: 求解线性和二次方程喵~
矩阵计算模式喵: 支持矩阵加减乘法和行列式计算喵~
异步计算模式喵: 大数阶乘、斐波那契、素数计算、π计算等喵~
{sympy_features}

多线程特性喵:
- 后台异步计算，不阻塞主界面喵~
- 实时进度条显示喵~
- 任务状态查询喵~
- 并行加速统计计算喵~

猫娘特色喵:
- 全程猫娘语音陪伴喵~
- 萌系表情和语气词喵~
- 随机卖萌和鼓励喵~
- 猫娘专属进度条喵~

特殊命令喵:
  prec - 设置显示精度喵~
  hist - 查看历史记录喵~
  help - 显示帮助信息喵~
====================== {CatgirlEmoji.LOVING}
"""
    print(color(help_text, T.OKCYAN))

# ------------------ 猫娘主循环 ------------------
def main():
    # 创建猫娘任务管理器
    task_manager = CatgirlTaskManager(max_workers=4)
    
    sympy_notice = f"\n🧮 SymPy符号计算已经启用喵！" if SYMPY_AVAILABLE else f"\n⚠️  SymPy没有安装，符号计算功能不可用喵..."
    
    print(color(rf"""
 /\_/\  
( o.o ) 
 > ^ <   猫娘计算器 v7.0 超萌模式启动喵！
 输入 help 查看所有功能，q 退出喵~
 💪 支持异步计算、多线程加速、符号计算喵！{sympy_notice}
    """, T.HEADER))
    
    print(color(CatgirlDialog.greet(), T.OKGREEN))
    
    # 定期清理已完成任务喵~
    def cleanup_task():
        while True:
            time.sleep(60)  # 每分钟清理一次喵~
            task_manager.cleanup_completed()
    
    cleanup_thread = threading.Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()
    
    while True:
        try:
            show_main_menu()
            cmd = input(color("主人要选择什么功能喵？(输入数字喵): ", T.BOLD)).strip().lower()
            
            if cmd in ('0', 'q','quit','exit','bye'):
                print(color(f"猫娘要休息了喵，再见喵主人~{CatgirlEmoji.SLEEPY}", T.OKBLUE))
                task_manager.executor.shutdown(wait=True)
                break
            
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
                async_calculation_mode(task_manager)
            elif cmd == '8':
                sympy_catgirl_mode()
            elif cmd == '9':
                set_precision()
            elif cmd == '10':
                show_history()
            elif cmd == '11' or cmd == 'help':
                show_help()
            else:
                print(color(f"喵娘不明白主人的选择喵，重新选好不好喵~{CatgirlEmoji.CONFUSED}", T.WARNING))
                
        except (KeyboardInterrupt, EOFError):
            print(color(f"\n主人强行撸猫，猫娘要休息了喵~{CatgirlEmoji.SLEEPY}", T.WARNING))
            task_manager.executor.shutdown(wait=True)
            break
        except Exception as e:
            print(color(f"喵娘遇到了未知错误喵: {e} {CatgirlEmoji.SAD}", T.FAIL))
            print(CatgirlDialog.comfort())
            if input("要打印详细错误信息喵？(y/n): ").lower()=='y':
                traceback.print_exc()

if __name__ == '__main__':
    main()
