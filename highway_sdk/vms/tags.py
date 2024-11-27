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
from dataclasses import dataclass, asdict, field
from typing import List, Union
from nova.v3_11_5.internet.utils.constants import NovaTagsConvertor
from SanSi.v4_21_0.internet.utils.constants import SansiTagsConvertor


@dataclass
class BaseTags:
    def to_dict(self):
        return asdict(self)


@dataclass
class NowPlayContentTags(BaseTags):
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
class NowPlayAllContentTags(BaseTags):
    """
    当前播放点位列表
    """
    items: List[NowPlayContentTags] = field(default_factory=list)


@dataclass
class NowBrightnessTags(BaseTags):
    """
    当前显示亮度
    """
    # 按0~100 百分比显示亮度
    brightness: int = None


class VmsTagConvert:
    """
    情报板标准点位转化为平台的点位键值

    e.g.
    data = VmsTagConvert(tags, 'nova').apply_convert()
    """

    def __init__(
            self,
            tags: Union["NowPlayContentTags", "NowBrightnessTags", "NowPlayAllContentTags"],
            vms_brand: str = None
    ):
        self.tags = tags
        self.vms_brand = None if vms_brand is None else vms_brand.upper()
        self.convertor = self.__get_convertor()

    def __get_convertor(self):
        match self.vms_brand:
            case 'nova':
                return NovaTagsConvertor
            case 'sansi':
                return SansiTagsConvertor
            case _:
                return None

    def apply_convert(self):
        tags_type = type(self.tags)
        new_tags = {}
        if tags_type is NowPlayAllContentTags:
            for i, item in enumerate(self.tags.items):
                i += 1
                new_tags = {
                    f'FO{i}': self.convertor.FONT_TO_PLATFORM.get(item.font),
                    f'FC{i}': self.convertor.COLOR_TO_PLATFORM.get(item.text_color),
                    f'ZCT{i}': item.text,
                }
        elif tags_type is NowPlayContentTags:
            new_tags = {
                'CT': self.tags.text,
            }
        elif tags_type is NowBrightnessTags:
            new_tags = {
                'TGFK': self.tags.brightness,
            }

        return new_tags
