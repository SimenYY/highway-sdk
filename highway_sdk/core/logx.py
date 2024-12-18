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
import sys

from loguru import logger


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
            name: str = 'none',
            brand: str = 'none',
            level: str = 'DEBUG',
            rotation: str = '1 day',
            retention: str = '7 days',
            compression: str = 'zip',
            enqueue: bool = True,
            file: bool = True,
            console: bool = True
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
