# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: protocol.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2025/2/17 10:19
"""
import re

from highway_sdk.core import exceptions
from highway_sdk.vms.tags import NowPlayContentTags, NowPlayAllContentTags
from .constants import XianKeWhat
from .structs import XianKePacket


class ProtocolConfig:
    # 报文编码
    encoding: str = 'gbk'
    # 报文最小长度
    min_length: int = 9


class ProtocolParser:
    """协议解析
    """

    def __init__(self, raw_data: bytes, config: ProtocolConfig = None):
        self.raw_data = raw_data
        self.config = config or ProtocolConfig()

    def parse_packet(self) -> XianKePacket:
        """解析成包结构

        :raise ProtocolParserError
        :return:
        """
        if len(self.raw_data) < self.config.min_length:
            raise exceptions.ProtocolParserError(f'Length is less than the minimum length '
                                                 f'{self.config.min_length}: {self.raw_data.hex()}')
        try:
            p = XianKePacket.unpack(self.raw_data)
        except exceptions.CrcError as e:
            raise exceptions.ProtocolParserError(f'Crc error: {e}') from e
        except Exception as e:
            raise exceptions.ProtocolParserError(f'unpack error: {e}') from e

        return p

    def parse_tags(self) -> NowPlayContentTags | NowPlayAllContentTags:
        """解析成点位结构

        :raises ProtocolParserError: 解析错误
        :return: 当前显示内容或当前显示列表
        :rtype: NowPlayContentTags | NowPlayAllContentTags
        """

        p = self.parse_packet()
        match p.what:
            case XianKeWhat.GET_NOW_PLAY_CONTENT:
                return self._parse_now_play_content(p.data)
            case XianKeWhat.GET_NOW_PLAY_ALL_CONTENT:
                return self._parse_now_play_all_content(p.data)
            case _:
                raise exceptions.ProtocolParserError(f'Unknown what: {p.what}')

    def _parse_now_play_content(self, data: bytes) -> NowPlayContentTags:
        """解析当前显示内容

        e.g.
            3,1,0,1,1,\\C000000\\Fs32\\T255255000000\\B000000000000\\U安全第一\\N预防为主

        :param data:
        :return:
        :rtype: NowPlayContentTags
        """

        # 00异常/01正常
        flag = data[0:1]
        if flag != b'\x01':
            raise exceptions.ResponseError(f"查询当前内容响应异常")

        tags = NowPlayContentTags()

        data_str = data[1:].decode(self.config.encoding)
        params = data_str.split(",", maxsplit=5)

        tags.duration = params[0]
        tags.screen_in = params[1]
        tags.raw_str = params[-1]

        # 字体、字体大小
        font_search_resul = re.search(r"\\F([a-zA-Z])(\d{2})", tags.raw_str)
        if font_search_resul:
            tags.font = font_search_resul.group(1)
            tags.font_size = font_search_resul.group(2)

        # 字体颜色
        text_color_search_result = re.search(r"\\T(\d{12})", tags.raw_str)
        if text_color_search_result:
            tags.text_color = text_color_search_result.group(1)

        # 图片
        image_search_result = re.search(r"\\(GI)(\d{3})", tags.raw_str)
        if image_search_result:
            image_type_map = {
                "G": "gif",
                "I": "bmp"
            }
            image_type = image_search_result.group(1)
            tags.image_type = image_type_map[image_type]
            tags.image_name = image_search_result.group(2)

        # 文本
        text_search_result = re.search(r"\\U(.*)", tags.raw_str)
        if text_search_result:
            text = text_search_result.group(1)
            text = text.replace("\\N", "")
            text = text.replace("\r", "")
            text = text.replace("\n", "")
            tags.text = text

        return tags

    @staticmethod
    def _parse_now_play_all_content(data: bytes) -> NowPlayAllContentTags:
        """
        解析当前显示列表

        :param data:
        :return:
        :rtype: NowPlayAllContentTags
        """
        # todo
        pass


class ProtocolMessage:
    """协议类

    生成各种功能报文
    """

    def __init__(self, config: ProtocolConfig = None):
        self.config = config or ProtocolConfig()

    def play_list(self, file_name: str = r'000.xkl') -> bytes:
        """播放列表

        :param file_name:
        :return:
        """
        p = XianKePacket(what=XianKeWhat.PLAY_LIST,
                         data=file_name.encode(self.config.encoding))
        return p.pack()

    def upload_file(self,
                    content: str,
                    file_type: str = 'list',
                    file_name: str = r'list\000.xkl'
                    ) -> bytes:
        """
        data组成：【reserved 1B】【文件帧标记 1B】【文件名长度 3B】【文件名 nB】【文件偏移地址 4B】【数据 nB】

        :param content:
        :param file_type:
        :param file_name:
        :return:
        """
        file_path = f"{file_type}\\{file_name}"

        data = b'\x31'  # reserved
        data += b'\x30'  # 默认文件帧标记

        data += str(len(file_path)).encode('ascii').rjust(3, b'\x30')
        data += file_path.encode(self.config.encoding)
        data += b'\x30\x30\x30\x30'  # 文件偏移地址
        data += content.encode(self.config.encoding)
        p = XianKePacket(what=XianKeWhat.upload_file, data=data)

        return p.pack()

    def get_now_play_content(self) -> bytes:
        """获取当前显示内容

        :return:
        """
        p = XianKePacket(what=XianKeWhat.GET_NOW_PLAY_CONTENT,
                         data=b'')
        return p.pack()

    def get_now_play_all_content(self) -> bytes:
        """获取当前显示列表

        :return:
        """
        p = XianKePacket(what=XianKeWhat.GET_NOW_PLAY_ALL_CONTENT,
                         data=b'')
        return p.pack()

    def get_now_brightness(self) -> bytes:
        """获取当前显示亮度

        :return:
        """
        p = XianKePacket(what=XianKeWhat.GET_NOW_BRIGHTNESS,
                         data=b'')
        return p.pack()

    def set_now_brightness(self, brightness: int) -> bytes:
        """设置当前显示亮度

        :param brightness:
        :return:
        """
        pass
