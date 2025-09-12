#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: logger_config.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2025/5/20 15:35
"""
import sys
import logging
from pathlib import Path
import loguru
from highway_sdk.core.log.handlers import InterceptHandler as _InterceptHandler


class LoguruConfig:
    """配置loguru

    注释：
        1. 能够添加拦截原生的logger
        2. 能够配置console和file两种常用输出
    """

    def __init__(self, name: str, level: str = "DEBUG",
                 ):
        loguru.logger.remove()

        self.name = name
        self.level = level

    def include_logging_namespace(self, namespace: str) -> None:
        """
        添加logging命名空间
        """
        logging_logger = logging.getLogger(namespace)
        self.include_logging_logger(logging_logger)

    def include_logging_logger(self, logging_logger: logging.Logger) -> None:
        """
        添加logging.logger
        """
        logging_logger.setLevel(self.level)
        logging_logger.handlers.clear()
        logging_logger.addHandler(_InterceptHandler())
        logging_logger.propagate = False

    def setup_console(self) -> None:
        loguru.logger.add(
            sys.stdout,
            level=self.level
        )

    def setup_file(
            self,
            log_dir: str | Path = 'logs',
            *,
            rotation: str = '00:00',
            retention: str = '3 days',
            compression: str = 'zip',
            enqueue: bool = True,
    ):
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / self.name / (f"{self.name}" + "_{time: YYYY-MM-DD}.log")
        loguru.logger.add(
            str(log_file),
            level=self.level,
            rotation=rotation,
            retention=retention,
            compression=compression,
            enqueue=enqueue
        )
