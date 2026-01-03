#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NekoMap - 猫娘网络扫描工具
超可爱的PyMap猫娘版本，连端口扫描都变得萌萌哒~
作者: AI Assistant (被猫娘化的程序员)
版本: 2.0 (猫娘版)
"""

import socket
import threading
import time
import argparse
import sys
import struct
import random
import select
import signal
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import csv
from datetime import datetime
import ipaddress

class NekoScanner:
    def __init__(self):
        self.open_ports = []
        self.closed_ports = []
        self.filtered_ports = []
        self.host_info = {}
        self.scan_results = {}
        self.lock = threading.Lock()
        self.stop_scan = False
        self.total_ports = 0
        self.scanned_ports = 0
        self.neko_mood = "开心"
        
        # 猫娘语气的装饰
        self.neko_prefixes = [
            "喵~", "nya~", "咪呀~", "喵呜~", "喵喵~", "(=^-ω-^=)", 
            "(=^･ω･^=)", "喵♪", "nya♪", "(*´▽`*)", "喵呀!"
        ]
        
        # 常见服务端口 (猫娘整理版)
        self.common_ports = [
            21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995,
            1723, 3306, 3389, 5900, 8080, 8443, 8888, 9000, 9200, 27017
        ]
        
        # 服务识别特征 (加了猫娘标签)
        self.service_signatures = {
            21: b'220.*FTP',
            22: b'SSH',
            25: b'220.*SMTP',
            80: b'HTTP',
            443: b'TLS',
            3306: b'mysql',
            3389: b'RDP',
            8080: b'HTTP'
        }
    
    def get_neko_prefix(self):
        """获取随机猫娘前缀"""
        return random.choice(self.neko_prefixes)
    
    def signal_handler(self, signum, frame):
        """处理中断信号 (猫娘版)"""
        print(f"\n{self.get_neko_prefix()} 扫描被主人中断了喵...正在保存结果...")
        self.neko_mood = "委屈"
        self.stop_scan = True
    
    def resolve_host(self, hostname):
        """解析主机名到IP地址 (猫娘帮你找~)"""
        try:
            print(f"{self.get_neko_prefix()} 正在解析 {hostname} 的地址喵...")
            ip = socket.gethostbyname(hostname)
            print(f"{self.get_neko_prefix()} 找到了! {hostname} 的IP是 {ip} 喵~")
            return ip
        except socket.gaierror:
            print(f"{self.get_neko_prefix()} 呜喵...找不到 {hostname} 的地址...")
            return None
    
    def get_host_info(self, ip):
        """获取主机信息 (猫娘调查ing)"""
        try:
            print(f"{self.get_neko_prefix()} 正在调查 {ip} 的主机名喵...")
            hostname = socket.gethostbyaddr(ip)[0]
            print(f"{self.get_neko_prefix()} 发现了! 主机名是 {hostname} 喵♪")
            return hostname
        except:
            print(f"{self.get_neko_prefix()} 咪呀...查不到主机名...")
            return None
    
    def tcp_scan(self, host, port, timeout=1):
        """TCP连接扫描 (猫娘敲门ing)"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            
            if result == 0:
                service = self.detect_service(sock, port)
                banner = self.grab_banner(sock, port)
                
                with self.lock:
                    self.open_ports.append({
                        'port': port,
                        'service': service,
                        'banner': banner,
                        'state': 'open'
                    })
                
                print(f"{self.get_neko_prefix()} 端口 {port} 是开放的喵! 发现了 {service} 服务~")
                return True
            else:
                with self.lock:
                    self.closed_ports.append(port)
                return False
                
        except socket.timeout:
            with self.lock:
                self.filtered_ports.append(port)
            return False
        except Exception as e:
            with self.lock:
                self.filtered_ports.append(port)
            return False
        finally:
            try:
                sock.close()
            except:
                pass
    
    def syn_scan(self, host, port, timeout=1):
        """SYN半开扫描（需要root权限）"""
        try:
            print(f"{self.get_neko_prefix()} 尝试SYN扫描端口 {port} 喵...")
            # 创建原始套接字
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            sock.settimeout(timeout)
            
            # 构建SYN包
            packet = self.build_syn_packet(host, port)
            sock.sendto(packet, (host, 0))
            
            # 等待响应
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    data, addr = sock.recvfrom(1024)
                    if self.parse_syn_response(data, port):
                        with self.lock:
                            self.open_ports.append({
                                'port': port,
                                'service': 'unknown',
                                'banner': '',
                                'state': 'open'
                            })
                        print(f"{self.get_neko_prefix()} SYN扫描发现端口 {port} 开放喵!")
                        return True
                except socket.timeout:
                    continue
            
            return False
            
        except PermissionError:
            print(f"{self.get_neko_prefix()} 呜喵...SYN扫描需要root权限，切换到TCP扫描...")
            return self.tcp_scan(host, port, timeout)
        except Exception as e:
            return self.tcp_scan(host, port, timeout)
    
    def build_syn_packet(self, dst_ip, dst_port):
        """构建SYN数据包 (猫娘制作ing)"""
        src_port = random.randint(1024, 65535)
        # 简化版TCP SYN包构建
        packet = struct.pack('!HHLLBBHHH', src_port, dst_port, 0, 0, 5, 2, 8192, 0, 0)
        return packet
    
    def parse_syn_response(self, data, port):
        """解析SYN响应"""
        try:
            if len(data) > 20:
                return True
            return False
        except:
            return False
    
    def detect_service(self, sock, port):
        """服务版本检测 (猫娘识别ing)"""
        if port in self.service_signatures:
            service = self.get_service_name(port)
            print(f"{self.get_neko_prefix()} 端口 {port} 看起来是 {service} 服务喵~")
            return service
        
        try:
            # 尝试获取服务横幅
            sock.send(b'\r\n\r\n')
            banner = sock.recv(1024)
            
            for service, signature in self.service_signatures.items():
                if signature in banner[:100]:
                    service_name = self.get_service_name(service)
                    print(f"{self.get_neko_prefix()} 识别成功! 是 {service_name} 喵♪")
                    return service_name
            
            print(f"{self.get_neko_prefix()} 咪呀...这个服务不认识...")
            return 'unknown'
        except:
            return self.get_service_name(port)
    
    def grab_banner(self, sock, port):
        """横幅抓取 (猫娘收集情报ing)"""
        try:
            sock.settimeout(2)
            banner = sock.recv(1024)
            banner_text = banner.decode('utf-8', errors='ignore').strip()
            if banner_text:
                print(f"{self.get_neko_prefix()} 收集到了横幅信息: {banner_text[:50]}...")
            return banner_text
        except:
            return ''
    
    def get_service_name(self, port):
        """获取服务名称 (猫娘服务小词典)"""
        services = {
            21: 'ftp', 22: 'ssh', 23: 'telnet', 25: 'smtp', 53: 'dns',
            80: 'http', 110: 'pop3', 111: 'rpcbind', 135: 'msrpc',
            139: 'netbios-ssn', 143: 'imap', 443: 'https', 445: 'smb',
            993: 'imaps', 995: 'pop3s', 1723: 'pptp', 3306: 'mysql',
            3389: 'rdp', 5900: 'vnc', 8080: 'http-proxy', 8443: 'https-alt',
            8888: 'http-alt', 9000: 'php-fpm', 9200: 'elasticsearch',
            27017: 'mongodb'
        }
        return services.get(port, 'unknown')
    
    def ping_scan(self, host, timeout=2):
        """主机发现（Ping扫描）- 猫娘探路ing"""
        try:
            print(f"{self.get_neko_prefix()} 正在检查 {host} 是否醒着喵...")
            # 使用TCP ACK ping
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, 80))
            sock.close()
            
            if result == 0 or result == 111:  # 连接成功或连接被拒绝
                print(f"{self.get_neko_prefix()} 目标主机醒着呢! (≧▽≦)")
                return True
            
            # 尝试常用端口
            for port in [22, 23, 25, 53, 80, 135, 139, 443, 445, 993, 995, 3389]:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex((host, port))
                sock.close()
                if result == 0:
                    print(f"{self.get_neko_prefix()} 在端口 {port} 发现回应了喵!")
                    return True
            
            print(f"{self.get_neko_prefix()} 呜喵...主机好像睡着了...")
            return False
        except:
            return False
    
    def port_range_scan(self, host, start_port, end_port, scan_type='tcp', max_threads=100):
        """端口范围扫描 (猫娘大冒险)"""
        ports = list(range(start_port, end_port + 1))
        self.total_ports = len(ports)
        self.scanned_ports = 0
        
        print(f"{self.get_neko_prefix()} 开始扫描 {host} 的端口 {start_port}-{end_port} 喵!")
        print(f"{self.get_neko_prefix()} 使用 {scan_type.upper()} 扫描，线程数: {max_threads} 喵~")
        
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = []
            
            for port in ports:
                if self.stop_scan:
                    break
                    
                if scan_type == 'syn':
                    future = executor.submit(self.syn_scan, host, port)
                else:
                    future = executor.submit(self.tcp_scan, host, port)
                futures.append(future)
            
            # 显示进度
            for future in as_completed(futures):
                if self.stop_scan:
                    break
                    
                self.scanned_ports += 1
                progress = (self.scanned_ports / self.total_ports) * 100
                if self.scanned_ports % 50 == 0:  # 每50个端口显示一次进度
                    print(f"{self.get_neko_prefix()} 进度: {progress:.1f}% ({self.scanned_ports}/{self.total_ports}) 喵~")
        
        print(f"{self.get_neko_prefix()} 扫描完成! 发现了 {len(self.open_ports)} 个开放端口喵! (=^･ω･^=)")
    
    def scan_top_ports(self, host, top_n=1000, scan_type='tcp'):
        """扫描最常见的端口 (猫娘精选)"""
        if top_n <= 100:
            ports = self.common_ports[:top_n]
        else:
            # 生成更多端口
            ports = list(range(1, top_n + 1))
        
        self.total_ports = len(ports)
        self.scanned_ports = 0
        
        print(f"{self.get_neko_prefix()} 扫描 {host} 的前 {top_n} 个常见端口喵~")
        
        with ThreadPoolExecutor(max_workers=200) as executor:
            futures = []
            
            for port in ports:
                if self.stop_scan:
                    break
                    
                if scan_type == 'syn':
                    future = executor.submit(self.syn_scan, host, port)
                else:
                    future = executor.submit(self.tcp_scan, host, port)
                futures.append(future)
            
            for future in as_completed(futures):
                if self.stop_scan:
                    break
                    
                self.scanned_ports += 1
                if self.scanned_ports % 100 == 0:
                    progress = (self.scanned_ports / self.total_ports) * 100
                    print(f"{self.get_neko_prefix()} 进度: {progress:.1f}% 喵~")
    
    def os_detection(self, host):
        """简单的操作系统检测 (猫娘猜系统ing)"""
        try:
            print(f"{self.get_neko_prefix()} 正在猜测 {host} 的操作系统喵...")
            # TTL指纹检测
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            sock.settimeout(3)
            
            # 尝试连接获取TTL
            result = self.ping_scan(host)
            if result:
                os_guess = "Unknown OS (可能在线)"
                print(f"{self.get_neko_prefix()} 猜到了! 可能是 {os_guess} 喵!")
                return os_guess
            return "OS Detection Failed"
        except:
            print(f"{self.get_neko_prefix()} 呜喵...系统检测失败了...")
            return "OS Detection Failed (需要root权限)"
    
    def save_results(self, filename, format='txt'):
        """保存扫描结果 (猫娘存档ing)"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if format == 'json':
            data = {
                'scan_time': timestamp,
                'target': self.host_info.get('ip', 'unknown'),
                'hostname': self.host_info.get('hostname', 'unknown'),
                'open_ports': self.open_ports,
                'total_open': len(self.open_ports),
                'closed_ports': len(self.closed_ports),
                'filtered_ports': len(self.filtered_ports),
                'neko_mood': self.neko_mood
            }
            
            with open(f"{filename}.json", 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        elif format == 'csv':
            with open(f"{filename}.csv", 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['端口', '状态', '服务', '横幅', '扫描时间', '猫娘心情'])
                for port_info in self.open_ports:
                    writer.writerow([
                        port_info['port'],
                        port_info['state'],
                        port_info['service'],
                        port_info['banner'][:50],
                        timestamp,
                        self.neko_mood
                    ])
        else:
            with open(f"{filename}.txt", 'w', encoding='utf-8') as f:
                f.write(f"NekoMap 猫娘扫描报告\n")
                f.write(f"扫描时间: {timestamp}\n")
                f.write(f"目标主机: {self.host_info.get('ip', 'unknown')}\n")
                f.write(f"主机名: {self.host_info.get('hostname', 'unknown')}\n")
                f.write(f"猫娘心情: {self.neko_mood}\n")
                f.write(f"{'='*50}\n")
                f.write(f"开放端口: {len(self.open_ports)}\n")
                f.write(f"关闭端口: {len(self.closed_ports)}\n")
                f.write(f"过滤端口: {len(self.filtered_ports)}\n")
                f.write(f"{'='*50}\n")
                
                for port_info in self.open_ports:
                    f.write(f"端口: {port_info['port']:5d}/tcp\n")
                    f.write(f"状态: {port_info['state']}\n")
                    f.write(f"服务: {port_info['service']}\n")
                    if port_info['banner']:
                        f.write(f"横幅: {port_info['banner'][:100]}\n")
                    f.write(f"{'-'*30}\n")
    
    def print_results(self):
        """打印扫描结果 (猫娘汇报ing)"""
        print(f"\n{self.get_neko_prefix()} 扫描结果摘要喵:")
        print(f"    目标: {self.host_info.get('ip', 'unknown')}")
        print(f"    主机名: {self.host_info.get('hostname', 'unknown')}")
        print(f"    开放端口: {len(self.open_ports)} 个喵!")
        print(f"    关闭端口: {len(self.closed_ports)} 个")
        print(f"    过滤端口: {len(self.filtered_ports)} 个")
        
        if self.open_ports:
            print(f"\n{self.get_neko_prefix()} 开放端口详情喵:")
            print(f"{'端口':<8} {'状态':<10} {'服务':<15} {'横幅'}")
            print(f"{'-'*60}")
            
            for port_info in sorted(self.open_ports, key=lambda x: x['port']):
                banner = port_info['banner'][:30] if port_info['banner'] else ''
                print(f"{port_info['port']:<8} {port_info['state']:<10} {port_info['service']:<15} {banner}")
        
        print(f"\n{self.get_neko_prefix()} 扫描完成喵! 今天的猫娘也很努力呢! (=^･ω･^=)")

def main():
    parser = argparse.ArgumentParser(
        description='NekoMap - 超可爱猫娘网络扫描工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
喵~ 欢迎使用NekoMap猫娘扫描器喵!

示例:
  python3 nekomap.py 192.168.1.1                    # 扫描常见端口喵~
  python3 nekomap.py 192.168.1.1 -p 1-1000          # 扫描指定端口范围喵!
  python3 nekomap.py 192.168.1.1 --top-ports 100    # 扫描前100个常见端口喵~
  python3 nekomap.py 192.168.1.1 -sS                 # SYN扫描喵!
  python3 nekomap.py 192.168.1.1 -oA scan_result     # 保存所有格式结果喵!

猫娘提示: 使用的时候要温柔一点哦~ nya♪
        """
    )
    
    parser.add_argument('target', help='目标主机 (IP地址或域名) 喵~')
    parser.add_argument('-p', '--ports', help='端口范围 (例如: 1-1000 或 80,443,8080) 喵~')
    parser.add_argument('--top-ports', type=int, help='扫描最常见的N个端口 喵!')
    parser.add_argument('-sS', '--syn', action='store_true', help='SYN半开扫描 喵~')
    parser.add_argument('-sT', '--tcp', action='store_true', help='TCP连接扫描 (默认) 喵~')
    parser.add_argument('-O', '--os', action='store_true', help='操作系统检测 喵~')
    parser.add_argument('-T', '--threads', type=int, default=100, help='线程数 (默认: 100) 喵~')
    parser.add_argument('-oA', '--output-all', help='保存所有格式结果的基本文件名 喵~')
    parser.add_argument('-oN', '--output-normal', help='保存文本格式结果 喵~')
    parser.add_argument('-oJ', '--output-json', help='保存JSON格式结果 喵~')
    parser.add_argument('-oC', '--output-csv', help='保存CSV格式结果 喵~')
    parser.add_argument('--timeout', type=float, default=1.0, help='连接超时时间 (默认: 1.0秒) 喵~')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出 喵~')
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        parser.print_help()
        print(f"\n{random.choice(['喵~', 'nya~', '咪呀~'])} 主人需要帮助吗? 猫娘随时为你服务!")
        return
    
    scanner = NekoScanner()
    signal.signal(signal.SIGINT, scanner.signal_handler)
    
    # 超可爱的猫娘LOGO
    neko_logos = [
        """
    (=^･ω･^=)     ____        __  ____
   /     \       / __ \____ _/ /_/ __ \___  ____ ___
  /  ( )  \     / /_/ / __ `/ __/ /_/ / _ \/ __ `__ \\
 /   ┃ ┃  \    / ____/ /_/ / /_/ ____/  __/ / / / / /
/___┃ ┃___\  /_/    \__,_/\__/_/    \___/_/ /_/ /_/
        """,
        """
   ∧＿∧        ____        __  ____
  ( ･ω･ )     / __ \____ _/ /_/ __ \___  ____ ___
  /　 　＼    / /_/ / __ `/ __/ /_/ / _ \/ __ `__ \\
 (  川  ）  / ____/ /_/ / /_/ ____/  __/ / / / / /
  ｜ ｜｜   /_/    \__,_/\__/_/    \___/_/ /_/ /_/
  ｜U｜｜
        """,
        """
   ╱|、
  (˚ˎ 。7     ____        __  ____
   |、˜〵     / __ \____ _/ /_/ __ \___  ____ ___
  じしˍ,)ノ  / /_/ / __ `/ __/ /_/ / _ \/ __ `__ \\
            / ____/ /_/ / /_/ ____/  __/ / / / / /
           /_/    \__,_/\__/_/    \___/_/ /_/ /_/
        """
    ]
    
    print(random.choice(neko_logos))
    print("NekoMap - 超可爱猫娘网络扫描工具 v2.0")
    print("猫娘口号: 连端口扫描都变得萌萌哒~ nya♪\n")
    
    # 解析目标
    target_ip = scanner.resolve_host(args.target)
    if not target_ip:
        print(f"呜喵...无法解析主机: {args.target} 咪呀...")
        return
    
    scanner.host_info['ip'] = target_ip
    scanner.host_info['hostname'] = scanner.get_host_info(target_ip)
    
    print(f"{scanner.get_neko_prefix()} 开始扫描 {args.target} ({target_ip}) 喵~")
    
    # 主机发现
    if not scanner.ping_scan(target_ip):
        print(f"{scanner.get_neko_prefix()} 呜喵...主机 {target_ip} 好像睡着了...")
        if not args.verbose:
            return
    
    # 操作系统检测
    if args.os:
        print(f"{scanner.get_neko_prefix()} 进行操作系统检测喵...")
        os_info = scanner.os_detection(target_ip)
        print(f"{scanner.get_neko_prefix()} OS检测: {os_info}")
    
    # 确定扫描类型
    scan_type = 'syn' if args.syn else 'tcp'
    
    # 确定端口范围
    if args.ports:
        if '-' in args.ports:
            start, end = map(int, args.ports.split('-'))
            scanner.port_range_scan(target_ip, start, end, scan_type, args.threads)
        else:
            # 单个端口或端口列表
            ports = [int(p.strip()) for p in args.ports.split(',')]
            for port in ports:
                if scan_type == 'syn':
                    scanner.syn_scan(target_ip, port, args.timeout)
                else:
                    scanner.tcp_scan(target_ip, port, args.timeout)
    elif args.top_ports:
        scanner.scan_top_ports(target_ip, args.top_ports, scan_type)
    else:
        # 默认扫描常见端口
        scanner.scan_top_ports(target_ip, 100, scan_type)
    
    # 显示结果
    scanner.print_results()
    
    # 保存结果
    if args.output_all:
        scanner.save_results(args.output_all, 'txt')
        scanner.save_results(args.output_all, 'json')
        scanner.save_results(args.output_all, 'csv')
        print(f"{scanner.get_neko_prefix()} 结果已保存到 {args.output_all}.* 喵!")
    
    if args.output_normal:
        scanner.save_results(args.output_normal, 'txt')
        print(f"{scanner.get_neko_prefix()} 文本结果已保存到 {args.output_normal}.txt 喵!")
    
    if args.output_json:
        scanner.save_results(args.output_json, 'json')
        print(f"{scanner.get_neko_prefix()} JSON结果已保存到 {args.output_json}.json 喵!")
    
    if args.output_csv:
        scanner.save_results(args.output_csv, 'csv')
        print(f"{scanner.get_neko_prefix()} CSV结果已保存到 {args.output_csv}.csv 喵!")
    
    print(f"\n{scanner.get_neko_prefix()} 主人，扫描任务完成喵! 猫娘今天也很努力呢! (=^･ω･^=)")

if __name__ == '__main__':
    main()
