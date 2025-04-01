#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: singleInstance.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2025/4/1 14:07
"""

import sys
import tempfile
from pathlib import Path

from filelock import FileLock


class Singleton:
    """应用二次启动文件锁

    Usage:
        with Singleton(lock_name="your_app.lock"):
            print("your func")

    """

    def __init__(
            self,
            lock_name: str = 'Singleton.lock',
    ):
        # 创建锁
        self.lock = FileLock(Path(tempfile.gettempdir()) / lock_name)

    def __enter__(self):
        try:
            self.lock.acquire(timeout=0)
            print("The program is started successfully")
        except TimeoutError:
            print("The program is already running")
            sys.exit(0)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lock.release()
        print("The program is exited successfully")
