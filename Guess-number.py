#!/usr/bin/env python3
import random

def game():
    print("=== 猜数字喵 1~100 ===")
    n = random.randint(1, 100)
    cnt = 0
    while True:
        try:
            g = int(input("猜: "))
            cnt += 1
            if g == n:
                print(f"猜中！用了 {cnt} 次喵")
                print(f'喵咪下工了，再见喵~')
                break
            print("大了喵" if g > n else "小了喵")
        except ValueError:
            print("请输入整数喵")

if __name__ == "__main__":
    game()
