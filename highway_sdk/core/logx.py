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
from logging.handlers import HTTPHandler
import requests
from loguru import logger
from requests.auth import HTTPBasicAuth


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


class PooledHTTPHandler(HTTPHandler):
    """
    http日志记录
    """
    def __init__(self,
                 host,
                 url,
                 method="POST",
                 secure=False,
                 credentials=None,
                 context=None,
                 ):
        """

        :param host: e.g. 127.0.0.1:8888
        :param url: e.g. /log
        :param method:
        :param secure:
        :param credentials: (username, password)
        :param context:
        """
        super().__init__(host, url, method, secure, credentials, context)
        self.session = requests.Session()

    @property
    def full_url(self) -> str:
        """
        Get an HTTP[S] URL using requests.
        """
        if self.secure:
            url = f"https://{self.host}{self.url}"
        else:
            url = f"http://{self.host}{self.url}"
        return url

    def emit(self, record: logging.LogRecord) -> None:
        try:
            url = self.full_url
            data = self.mapLogRecord(record)
            auth = None

            if self.credentials:
                auth = HTTPBasicAuth(*self.credentials)

            match self.method:
                case "GET":
                    self.session.get(url, params=data, auth=auth)
                case "POST":
                    self.session.post(url, params=data, auth=auth)
                case _:
                    raise ValueError(f"Unsupported method: {self.method}")
        except Exception:
            self.handleError(record)


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

    默认的使用方式
    logger = DriverLoggerConfig().logger
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

    默认的使用方式
    logger = ApiLoggerConfig().logger
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
