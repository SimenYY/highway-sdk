#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: handlers.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/12/2 17:01
"""
import inspect
import logging
import socket
from typing import Literal

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


class HttpHandler(logging.Handler):
    def __init__(
            self,
            host: str,
            url: str,
            method: Literal['POST', 'GET'] = "POST",
            secure: bool = False,
            credentials: tuple | list = None
    ):
        super().__init__()
        method = method.upper()
        if method not in ['POST', 'GET']:
            raise ValueError("method must be POST or GET")

        self.host = host
        self.url = url
        self.method = method
        self.secure = secure
        self.credentials = credentials
        self.session = requests.Session()

    def map_log_Record(self, record):

        record.__dict__.update(
            hostname=socket.gethostname(),
        )
        return record.__dict__

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

    def _send_req(self, record):
        try:
            url = self.full_url
            data = self.map_log_Record(record)
            auth = None

            if self.credentials:
                auth = HTTPBasicAuth(*self.credentials)
            match self.method:
                case "GET":
                    self.session.get(url, params=data, auth=auth)
                case "POST":
                    self.session.post(url, json=data, auth=auth)
                case _:
                    raise ValueError(f"Unsupported method: {self.method}")

        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def emit(self, record):
        self._send_req(record)


class MongoHandler(logging.Handler):
    pass


class KafkaHandler(logging.Handler):
    pass


class ElasticHandler(logging.Handler):
    pass
