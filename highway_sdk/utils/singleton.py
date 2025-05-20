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
import logging

from filelock import FileLock

logger = logging.getLogger(__name__)


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
        logger.info(f"lock file path: {str(Path(tempfile.gettempdir()) / lock_name)}")

    def __enter__(self):
        try:
            self.lock.acquire(timeout=0)
            logger.info("The program is started successfully")
        except TimeoutError:
            logger.info("The program is already running")
            sys.exit(0)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.lock.release()
        logger.info("The program is exited successfully")
