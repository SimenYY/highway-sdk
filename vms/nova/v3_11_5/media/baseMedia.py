#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: baseMedia.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/7/31 13:21
:Department: 公路机电工程技术中心
:Copyright: ©1993-2023 浙江中控信息产业股份有限公司
"""
from abc import ABC, abstractmethod


class BaseMedia(ABC):

    def __init__(self, builder):
        self.index: int = builder.index
        self.x: int = builder.x
        self.y: int = builder.y
        self.width: int = builder.width
        self.height: int = builder.height
        self.duration: int = builder.duration

    @abstractmethod
    def create_protocol(self) -> str:
        pass
