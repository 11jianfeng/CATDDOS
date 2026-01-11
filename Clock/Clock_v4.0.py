#!/usr/bin/env python3
import time, os, sys
from datetime import datetime

def clear():
    os.system('cls' if os.name=='nt' else 'clear')

while True:
    try:
        clear()
        print(datetime.now().strftime("%H:%M:%S"))
        time.sleep(1)
    except KeyboardInterrupt:
        sys.exit()
