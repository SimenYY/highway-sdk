#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: points.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/9/27 10:52
"""
from dataclasses import dataclass, asdict


@dataclass
class BaseTags:
    def to_dict(self):
        return asdict(self)


@dataclass
class NowPlayContent(BaseTags):
    """
    当前显示点位
    """
    raw_str: str = None
    font: str = None
    font_size: str = None
    text_color: str = None
    text: str = None
    image_name: str = None


@dataclass
class NowBrightness(BaseTags):
    """
    当前显示亮度
    """
    # 按0~100 百分比显示亮度
    brightness: int = None
