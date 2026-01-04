import time
import os
import sys

def clear_screen():
    """清屏函数"""
    if os.name == 'nt':  # Windows
        os.system('cls')
    else:  # Linux/Mac/Termux
        os.system('clear')

def format_time():
    """格式化当前时间"""
    current_time = time.localtime()
    return time.strftime("%Y-%m-%d %H:%M:%S", current_time)

def display_clock():
    """显示时钟主函数"""
    try:
        print("实时时钟 - 按 Ctrl+C 退出")
        print("=" * 30)
        
        while True:
            # 获取当前时间
            now = format_time()
            
            # 清屏并显示时间
            clear_screen()
            print("实时时钟 - 按 Ctrl+C 退出")
            print("=" * 30)
            print(f"\n当前时间: {now}")
            print(f"\n星期{['日','一','二','三','四','五','六'][time.localtime().tm_wday]}")
            print("\n" + "=" * 30)
            
            # 等待下一秒
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n时钟已停止运行")
        sys.exit(0)

def simple_clock():
    """简化版时钟（不显示星期）"""
    try:
        while True:
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"\r{current_time}", end="", flush=True)
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n时钟已停止运行")

if __name__ == "__main__":
    # 选择显示模式
    print("选择显示模式:")
    print("1. 全屏时钟（带清屏）")
    print("2. 简化时钟（单行显示）")
    
    try:
        choice = input("\n请输入选择(1/2，默认1): ").strip()
        
        if choice == "2":
            print("\n简化时钟模式")
            simple_clock()
        else:
            print("\n全屏时钟模式")
            display_clock()
            
    except (KeyboardInterrupt, EOFError):
        print("\n程序退出")
        sys.exit(0)
