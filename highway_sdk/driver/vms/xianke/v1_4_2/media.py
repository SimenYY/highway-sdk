#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: txtMedia.py
:Project:
:Brand:
:Version:
:Description:
:Author: He YinYu
:Link:
:Time: 2025/2/18 14:20
"""

import configparser
from ftplib import CRLF
import re
from pydantic import BaseModel, Field
from typing import List, Any
from enum import StrEnum, IntEnum
from abc import abstractmethod


# ==============================================================================
# 枚举量
# ==============================================================================
class FontEnum(StrEnum):
    HEI_TI = "h"
    KAI_TI = "k"
    SONG_TI = "s"
    FANG_SONG = "f"


class TextSizeEnum(IntEnum):
    SIZE_16 = 16
    SIZE_24 = 24
    SIZE_32 = 32
    SIZE_48 = 48
    SIZE_64 = 64


class ColorEnum(StrEnum):
    RED = "255000000000"
    GREEN = "000255000000"
    YELLOW = "255255000000"
    BLACK = "000000000000"


class ScreenInOutEnum(IntEnum):
    NORMAL = 1
    MOVE_UP = 6
    MOVE_DOWN = 7
    MOVE_LEFT = 8
    MOVE_RIGHT = 9


class EscEnum(StrEnum):
    """转义字符

    Args:
        StrEnum (_type_): _description_
    """
    XY = "\\C"  # 起始坐标
    IMAGE = "\\I"  # 图片信息设置，默认bmp
    ICON = "\\A"  # 交通图标
    FONT = "\\F"  # 字体
    FONT_COLOR = "\\T"  # 字符颜色
    BACKGROUND_COLOR = "\\B"  # 字符背景颜色
    TEXT = "\\U"  # 显示信息内容
    GIF = "\\G"  # GIF信息
    VIDEO = "\\V"  # Video信息
    LF = "\\N"  # 换行转义符


# ==============================================================================
# 媒体类
# ==============================================================================
class _Media(BaseModel):
    x: int = Field(..., ge=-99, le=999)
    y: int = Field(..., ge=-99, le=999)
    font: FontEnum
    text_size: TextSizeEnum
    text_color: ColorEnum
    background_color: ColorEnum
    text: str
    bmp_file_name: str
    gif_file_name: str
    video_file_name: str
    def __str__(self):
        protocol = (
            f"{EscEnum.XY.value}{self.x:03d}{self.y:03d}"
            f"{EscEnum.FONT.value}{self.font.value}{self.text_size}" # todo 这个文本大小格式是否有问题
            f"{EscEnum.FONT_COLOR.value}{self.text_color.value}"
            f"{EscEnum.BACKGROUND_COLOR.value}{self.background_color.value}"
        )
        # todo: 修改判断文本后再添加字体及颜色
        if self.text:
            protocol += f"{EscEnum.TEXT.value}{self.text}"
        else:
            protocol += f"{EscEnum.IMAGE.value}{self.bmp_file_name.rjust(3, '0')}"

        return protocol


class MediaBuilder:
    def __init__(self):
        self.x: int = 0
        self.y: int = 0
        self.font: str = FontEnum.HEI_TI.value
        self.text_size: int = TextSizeEnum.SIZE_16.value
        self.text_color: str = ColorEnum.YELLOW.value
        self.background_color: str = ColorEnum.BLACK.value
        self.text: str = ""
        self.bmp_file_name: str = ""
        self.gif_file_name: str = ""
        self.video_file_name: str = ""
    def build(self) -> _Media:
        """构造函数

        :return:
        """
        return _Media(**self.__dict__)


# ==============================================================================
# 播放项类
# ==============================================================================
class _Item(BaseModel):
    # 停留时间
    duration: int
    # 进入方式
    screen_in: ScreenInOutEnum
    # 显示效果
    play_effect: int
    # 出屏方式
    screen_out: ScreenInOutEnum
    # 播放速度
    play_speed: int = Field(..., gt=0)
    # 媒体内容
    _media: _Media

    def __str__(self):
        protocol = (
            f"{self.duration},"
            f"{self.screen_in.value},"
            f"{self.play_effect},"
            f"{self.screen_out.value},"
            f"{self.play_speed},"
            f"{self._media}"
        )
        return protocol


class ItemBuilder:
    def __init__(self):
        self._media: _Media
        self.duration: int = 10
        self.screen_in: int = ScreenInOutEnum.NORMAL.value
        self.screen_out: int = ScreenInOutEnum.NORMAL.value
        self.play_effect: int = 0
        self.play_speed: int = 1

    def build(self) -> _Item:
        item = _Item(**self.__dict__)
        item._media = self._media
        return item


# ==============================================================================
# 播放表类
# ==============================================================================
class _Play(BaseModel):
    _item_list: List[_Item]

    def __str__(self):
        """
        注：除了转义字符，其他字符均大小写无关
        
        :return:
        """
        protocol = "[LIST]"
        protocol += CRLF
        protocol += f"ItemCount={len(self._item_list):03d}"
        protocol += CRLF
        for i, item in enumerate(self._item_list):
            protocol += f"Item{i:02d}={item}"
            protocol += CRLF

        return protocol


class PlayBuilder:
    """播放表构建器
    """

    def __init__(self):
        self._item_list: List[_Item] = []

    def add_item_builder(self, builder: ItemBuilder) -> "PlayBuilder":
        """添加item建造器

        :param builder: 建造器
        :return:
        :rtype: PlayBuilder
        """
        self._item_list.append(builder.build())
        return self

    def build(self) -> _Play:
        """构造函数

        :return: Play
        """
        play = _Play(**self.__dict__)
        play._item_list = self._item_list
        return play
    
#==============================================================================
# 解析器
#==============================================================================

class BaseParser:
    @classmethod
    @abstractmethod
    def parse(cls, data: str) -> Any:
        pass
    
class PlayParser(BaseParser):
    """播放表解析器

    播放表格式
    [LIST]
    ItemCount=002
    Item00=2,1,0,1,1,\\C000000\\Fs32\\T255000000000\\B000000000000\\U 深圳显科科技有限公司 
    Item01=2,1,0,1,1,\\C000000\\Fs32\\T000255000000\\B000000000000\\U 深圳显科科技有限公司
        
    Args:
        BaseParser (_type_): _description_
    """
    @classmethod
    def parse(cls, data: str) -> PlayBuilder:
        play_parser = configparser.ConfigParser()
        play_parser.read_string(data)
        section = "LIST"
        items_num = int(play_parser.get(section, "ItemCount"))
        play_builder = PlayBuilder()
        
        for i in range(items_num):
            option = f"Item{i:02d}"
            item = play_parser.get(section, option)
            item_builder = ItemParser.parse(item)
            play_builder.add_item_builder(item_builder)
            
        return play_builder
    

class ItemParser(BaseParser):
    """播放项解析器

    播放项格式（查询返回不包含项序）
    3,1,0,1,1,\\C000000\\Fs32\\T255255000000\\B000000000000\\U安全第一\\N预防为主

    Args:
        BaseParser (_type_): _description_2
    """
    # 预编译正则表达式以提高性能
    FONT_PATTERN = re.compile(r"\\F([a-zA-Z])(\d{2})")
    COLOR_PATTERN = re.compile(r"\\T(\d{12})")
    IMAGE_PATTERN = re.compile(r"\\I(\d{3})")
    GIF_PATTERN = re.compile(r"\\G(\d{3})")
    VIDEO_PATTERN = re.compile(r"\\V(\d{3})")
    BG_COLOR_PATTERN = re.compile(r"\\B(\d{12})")
    TEXT_PATTERN = re.compile(r"\\U(.*)")

    @classmethod
    def parse(cls, data: str) -> ItemBuilder:
            fields = data.split(",")
            
            item_builder = ItemBuilder()
            item_builder.duration = int(fields[0])
            item_builder.screen_in = int(fields[1])
            item_builder.play_effect = int(fields[2])
            item_builder.screen_out = int(fields[3])
            item_builder.play_speed = int(fields[4])
            
            media_builder = MediaBuilder()
            media = fields[5]

            # 字体、字号（通常在媒体字符串前部，优先匹配）
            res = cls.FONT_PATTERN.search(media)
            if res:
                media_builder.font = res.group(1)
                media_builder.text_size = int(res.group(2))

            # 字体颜色
            res = cls.COLOR_PATTERN.search(media)
            if res:
                media_builder.text_color = res.group(1)

            # 背景颜色
            res = cls.BG_COLOR_PATTERN.search(media)
            if res:
                media_builder.background_color = res.group(1)

            # 检查是否有文本内容（通常在末尾，可提前处理）
            text_res = cls.TEXT_PATTERN.search(media)
            if text_res:
                text = text_res.group(1)
                text = text.replace(EscEnum.LF.value, "")
                media_builder.text = text
            else:
                # 只有在无文本时才检查图片/GIF/视频（互斥）
                res = cls.IMAGE_PATTERN.search(media)
                if res:
                    media_builder.bmp_file_name = res.group(1)
                else:
                    res = cls.GIF_PATTERN.search(media)
                    if res:
                        media_builder.gif_file_name = res.group(1)
                    else:
                        res = cls.VIDEO_PATTERN.search(media)
                        if res:
                            media_builder.video_file_name = res.group(1)

            item_builder._media = media_builder.build()
            return item_builder