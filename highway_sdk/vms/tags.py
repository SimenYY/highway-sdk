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
from typing import List, Union, Literal, Callable, Any

from highway_sdk.vms.SanSi.v4_21_0.internet.utils.constants import SansiTagsConvertor
from highway_sdk.vms.XianKe.v1_4_2.internet.constants import XianKeTagsConvertor
from highway_sdk.vms.nova.v3_11_5.internet.utils.constants import NovaTagsConvertor


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
    image_type: str = None
    # 单位秒
    duration: int = None
    # 入屏方式
    screen_in: str = None

    area_width: int = None
    area_height: int = None


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
            vms_brand: Literal["nova", "sansi", "xianke"],
            ct_process: Callable[[Any, ...], Any] = None
    ):
        """
        若需要对内容进行额外的处理，则自定义ct_process

        :param tags:
        :param vms_brand:
        :param ct_process:
        """
        self.tags = tags
        self.vms_brand = vms_brand
        self.convertor = self.get_convertor()
        self.ct_process = ct_process

    def get_convertor(self):
        match self.vms_brand:
            case "nova":
                return NovaTagsConvertor
            case "sansi":
                return SansiTagsConvertor
            case "xianke":
                return XianKeTagsConvertor
            case _:
                raise NotImplementedError(f'{self.vms_brand} is not supported')

    def apply_convert(self) -> dict | None:
        """
        如果转换器为None，则返回为None
        如果没有对应的tags类型，则返回空字典

        :return:
        """
        new_tags = {}
        if self.convertor is not None:
            tags_type = type(self.tags)

            if tags_type is NowPlayAllContentTags:
                for i, item in enumerate(self.tags.items):
                    i += 1

                    if self.ct_process is not None:
                        ct = self.ct_process(item.text, item.image_name)
                    else:
                        ct = item.text or item.image_name

                    new_tags.update({
                        # 字体
                        f'FO{i}': self.convertor.FONT_TO_PLATFORM.get(item.font, item.font),
                        # 字体颜色
                        f'FC{i}': self.convertor.COLOR_TO_PLATFORM.get(item.text_color, item.text_color),
                        # 文字或者图片编号
                        f'ZCT{i}': ct,
                        # 停留时间
                        f'TI{i}': item.duration,
                        # 入屏方式
                        f'SH{i}': item.screen_in
                    })
            elif tags_type is NowPlayContentTags:

                if self.ct_process is not None:
                    ct = self.ct_process(self.tags.text, self.tags.image_name)
                else:
                    ct = self.tags.text or self.tags.image_name

                new_tags = {
                    # 文字或者图片编号
                    'CT': ct,
                    # 字体颜色
                    'FC': self.convertor.COLOR_TO_PLATFORM.get(self.tags.text_color, self.tags.text_color),
                    # 入屏方式
                    'SH': self.tags.screen_in,
                    # 停留时间
                    'TI': self.tags.duration,
                    # 字体
                    'FO': self.convertor.FONT_TO_PLATFORM.get(self.tags.font, self.tags.font)
                }
            elif tags_type is NowBrightnessTags:
                new_tags = {
                    # 亮度
                    'TGFK': self.tags.brightness,
                }
        else:
            new_tags = None

        return new_tags