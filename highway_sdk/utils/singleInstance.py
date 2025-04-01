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

import os
from pathlib import Path
import sys
import tempfile


class SingleInstance:
    """通过文件锁，防止应用二次启动"""
    def __init__(
            self,
            lock_name: str = 'single_instance.lock'):

        self.lock_file = Path(tempfile.gettempdir()) / lock_name

    def __enter__(self):
        if self.lock_file.exists():
            print("The program is already running!")
            sys.exit(0)

        print("The program started successfully!")
        self.lock_file.write_text(str(os.getpid()))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.lock_file.exists():
            self.lock_file.unlink()
        print("The program has exited and the lock file has been deleted.")

