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
import logging
from loguru import logger


# 将logging 转发到 loguru
class LoguruHandler(logging.Handler):
    """
    使用 logging.basicConfig(handlers=[LoguruHandler()], level=logging.DEBUG)
    """
    def emit(self, record):
        # 获取 loguru 的日志记录
        loguru_record = logger.opt(depth=7, exception=record.exc_info)
        loguru_record.log(record.levelname, record.getMessage())
