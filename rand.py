#!/usr/bin/env python3
import random, sys

def ask_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("请输入整数！")

def main():
    print("=== 随机数生成器 ===")
    a = ask_int("区间下限: ")
    b = ask_int("区间上限: ")
    if a > b:
        a, b = b, a
    n = ask_int("生成个数: ")
    for _ in range(n):
        print(random.randint(a, b))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()
