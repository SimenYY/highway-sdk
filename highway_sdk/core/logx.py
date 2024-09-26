#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: logx.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/9/4 17:05
"""
import inspect
import logging
import sys

import requests
from loguru import logger


# 将logging 转发到 loguru
class InterceptHandler(logging.Handler):
    """
    使用：logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    """

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class HttpHandler:
    def __init__(self, url):
        self.url = url

    def emit(self, record):
        print(record)
        log_entry = {'log': record}
        self.send_log(log_entry)

    def send_log(self, log_entry):
        try:
            response = requests.post(
                self.url,
                json=log_entry,
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send log to server: {e}")


class BaseLoggerConfig:

    def __init__(self):
        self._logger = logger
        self._logger.remove()

    @property
    def logger(self):
        return self._logger


class DriverLoggerConfig(BaseLoggerConfig):
    """
    用于驱动脚本的日志配置
    """

    def __init__(
            self,
            name: str = 'unknown',
            brand: str = 'unknown',
            level: str = 'INFO',
            rotation: str = '1 day',
            retention: str = '7 days',
            compression: str = 'zip',
            enqueue: bool = True,
            file: bool = True,
            console: bool = False
    ):
        super().__init__()

        if file:
            self._logger.add(
                f'logs/{name}/' + f'{brand}' + '_{time: YYYY-MM-DD}.log',
                level=level,
                rotation=rotation,
                retention=retention,
                compression=compression,
                enqueue=enqueue
            )
        if console:
            self._logger.add(
                sys.stdout,
                level=level,
            )


class ApiLoggerConfig(BaseLoggerConfig):
    """
    Api 服务日志配置
    """

    def __init__(
            self,
            log_file: str = 'api.log',
            level: str = 'INFO',
            rotation: str = '1 day',
            retention: str = '7 days',
            compression: str = True,
            enqueue: bool = True
    ):
        super().__init__()
        self._logger.add(
            f'logs/Api/' + f'{log_file}' + '_{time: YYYY-MM-DD}.log',
            level=level,
            rotation=rotation,
            retention=retention,
            compression=compression,
            enqueue=enqueue
        )
