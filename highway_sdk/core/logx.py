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

import loguru
from loguru import logger
import logging
from highway_sdk.core.log.handlers import InterceptHandler
from highway_sdk import get_lib_name
from deprecated import deprecated

# 将本库的日志记录器转发到loguru中
lib_logger = logging.getLogger(get_lib_name())
lib_logger.setLevel(logging.DEBUG)
lib_logger.addHandler(InterceptHandler())
lib_logger.propagate = False


@deprecated(reason="脱裤子放屁，多此一举的一个类， 用【get_driver_loger】代替", version='1.19.1')
class BaseLoggerConfig:
    def __init__(self):
        self._logger = logger
        self._logger.remove()

    @property
    def logger(self):
        return self._logger


@deprecated(reason="脱裤子放屁，多此一举的一个类， 用【get_driver_loger】代替", version='1.19.1')
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


@deprecated(reason="脱裤子放屁，多此一举的一个类， 用【get_driver_loger】代替", version='1.19.1')
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
            f'logs/api/' + f'{log_file}' + '_{time: YYYY-MM-DD}.log',
            level=level,
            rotation=rotation,
            retention=retention,
            compression=compression,
            enqueue=enqueue
        )


def get_driver_loger(
        series: str = 'none',
        sn: str = 'none',
        level: str = 'DEBUG',
        rotation: str = '00:00',
        retention: str = '3 days',
        compression: str = 'zip',
        enqueue: bool = True,
        file: bool = True,
        console: bool = True
) -> loguru.logger:
    """
    loguru按照天分割文件，不够精确

    :param series: 种类
    :param sn: 品牌
    :param level:
    :param rotation:
    :param retention:
    :param compression:
    :param enqueue:
    :param file:
    :param console:
    :return:
    """
    # 防止多余的handlers重复打印
    logger.remove()

    if file:
        logger.add(
            f'logs/{series}/' + f'{sn}' + '_{time: YYYY-MM-DD}.log',
            level=level,
            rotation=rotation,
            retention=retention,
            compression=compression,
            enqueue=enqueue
        )
    if console:
        logger.add(
            sys.stdout,
            level=level,
        )
    return logger
