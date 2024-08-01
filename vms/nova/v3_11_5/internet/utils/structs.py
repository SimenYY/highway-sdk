#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: structs.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/8/1 10:47
:Department: 公路机电工程技术中心
:Copyright: ©1993-2023 浙江中控信息产业股份有限公司
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class NovaPacket:
    """
    Nova数据帧格式：【起始符 1B】-【设备地址 2B】-【指令码 1B】-【数据域 nB】-【结束符 1B】-【校验码 2B】
    注：
    1. 校验码为校验前面全部，包括起始符和结束符
    2. 设备地址默认为0xFFFF
    """
    START: bytes = b'\xAA'
    address: Optional[bytes] = b'\xFF\xFF'
    what: Optional[bytes] = None
    data: Optional[bytes] = None
    END: bytes = b'\xCC'
    crc: Optional[bytes] = None
