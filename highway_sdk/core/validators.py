#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: validators.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/8/8 11:06
"""
import ipaddress
from highway_sdk.core.exceptions import ValidationError


def validate_ipv4_address(value):
    try:
        ipaddress.IPv4Address(value)
    except ValueError:
        if value != 'localhost':
            raise ValidationError('请输入一个合法的IPv4地址')


def validate_port(value):
    if not 0 < value < 65536:
        raise ValidationError('请输入一个合法的端口号')
