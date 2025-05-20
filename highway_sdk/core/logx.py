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
from deprecated import deprecated


@deprecated(
    version="1.28.0",
    reason="使用 highway_sdk.utils.logger_config 代替"
)
def get_driver_loger(
        name: str = 'none',
        brand: str = 'none',
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

    :param name: 种类
    :param brand: 品牌
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

    # 将本库的日志记录器转发到loguru中
    lib_logger = logging.getLogger('highway_sdk')
    lib_logger.setLevel(logging.DEBUG)
    lib_logger.addHandler(InterceptHandler())
    lib_logger.propagate = False

    if file:
        logger.add(
            f'logs/{name}/' + f'{brand}' + '_{time: YYYY-MM-DD}.log',
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
