#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: __init__.py.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/8/2 15:34
:Department: 公路机电工程技术中心
:Copyright: ©1993-2023 浙江中控信息产业股份有限公司
"""
import logging
from highway_sdk.core.log.handlers import ColoredStreamHandler

logger = logging.getLogger(__name__)

logger.addHandler(ColoredStreamHandler())
logger.setLevel(logging.DEBUG)

