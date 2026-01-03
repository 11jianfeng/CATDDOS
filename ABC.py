#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简易加密 + 随机数工具
Termux / Linux / Windows 通用
"""

import random
import string
import base64
import hashlib
import time

# ===== 随机数工具 =====
def rand_int(a=0, b=100):
    """返回 a~b 闭区间随机整数"""
    return random.randint(a, b)

def rand_float(a=0.0, b=1.0):
    """返回 a~b 随机浮点数"""
    return random.uniform(a, b)

def rand_str(length=8, charset=None):
    """返回随机字符串（默认大小写+数字）"""
    if charset is None:
        charset = string.ascii_letters + string.digits
    return ''.join(random.choice(charset) for _ in range(length))

def rand_choice(seq):
    """从序列中随机取一个元素"""
    return random.choice(seq)

# ===== 简易加密/解密 =====
def b64_encrypt(plain_text: str) -> str:
    """Base64 编码（非加密，仅混淆）"""
    return base64.b64encode(plain_text.encode()).decode()

def b64_decrypt(cipher_text: str) -> str:
    """Base64 解码"""
    return base64.b64decode(cipher_text.encode()).decode()

def xor_encrypt(plain_text: str, key: str) -> str:
    """异或加密/解密（对称）"""
    key = (key * ((len(plain_text) // len(key)) + 1))[:len(plain_text)]
    cipher = ''.join(chr(ord(p) ^ ord(k)) for p, k in zip(plain_text, key))
    return base64.b64encode(cipher.encode()).decode()   # 再包一层 Base64 方便显示

def xor_decrypt(cipher_text: str, key: str) -> str:
    """异或解密"""
    cipher = base64.b64decode(cipher_text.encode()).decode()
    key = (key * ((len(cipher) // len(key)) + 1))[:len(cipher)]
    return ''.join(chr(ord(c) ^ ord(k)) for c, k in zip(cipher, key))

def sha256_hash(text: str) -> str:
    """SHA256 单向哈希（不可解密）"""
    return hashlib.sha256(text.encode()).hexdigest()

# ===== 演示 =====
if __name__ == "__main__":
    print("=== 随机数示例 ===")
    print("随机整数 1~100 :", rand_int(1, 100))
    print("随机浮点数 0~1 :", rand_float())
    print("随机字符串(12) :", rand_str(12))
    print("随机选择       :", rand_choice(['apple', 'banana', ' cherry']))

    print("\n=== 加密示例 ===")
    msg = "Hello Termux!"
    pwd = "1234"

    print("原文 :", msg)
    print("Base64 :", b64_encrypt(msg))
    xor_cipher = xor_encrypt(msg, pwd)
    print("XOR加密:", xor_cipher)
    print("XOR解密:", xor_decrypt(xor_cipher, pwd))
    print("SHA256 :", sha256_hash(msg))
