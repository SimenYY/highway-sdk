#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: protocol.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/8/22 9:20
"""
import re
from typing import Union

from deprecated import deprecated

from highway_sdk.core import exceptions
from highway_sdk.core.exceptions import CrcError, ProtocolParserError
from highway_sdk.vms.SanSi.v4_21_0.internet.constants import SanSiWhat
from highway_sdk.vms.SanSi.v4_21_0.internet.structs import SanSiPacketReq, SanSiPacketRsp
from highway_sdk.vms.tags import NowBrightnessTags
from highway_sdk.vms.tags import NowPlayContentTags, NowPlayAllContentTags


@deprecated(reason="Used ProtocolMessage、ProtocolParser instead", version="1.24.2")
class Protocol:
    """
    PS:
        对这个类进行了重构，以便更清晰的划分类的职责跟以后的扩展，保留以兼容旧的用法
    """
    # 报文最小长度
    PROTOCOL_MIN_LENGTH = 7

    ENCODING = 'GBK'

    @classmethod
    def play_list(cls, play_id: int = 1) -> bytes:
        pass

    @classmethod
    def set_now_brightness(cls, brightness: int) -> bytes:
        """
        设置当前亮度

        :param brightness: 协议亮度范围 0-31
        :return:
        """
        if brightness > 31:
            brightness = 31

        if brightness < 0:
            brightness = 0

        first = brightness // 10
        second = brightness % 10

        # 红，绿，蓝三基色相同
        data = b''.join(
            [bytes([ord(str(first))]), bytes([ord(str(second))])] * 3
        )
        return SanSiPacketReq.pack(what=SanSiWhat.SET_NOW_BRIGHTNESS,
                                   data=data)

    @classmethod
    def get_now_brightness(cls) -> bytes:
        return SanSiPacketReq.pack(what=SanSiWhat.GET_NOW_BRIGHTNESS,
                                   data=b'')

    @classmethod
    def send_file_name_and_content(cls, content: str, play_id: int = 0) -> bytes:
        # 如文件名为 "play.lst"， 是更改可变信息标志的当前播放表
        file_name = 'play.lst'
        data = file_name.encode(cls.ENCODING)
        # 分隔符，代表文件名结束
        data += b'\x2B'
        # 文件指针偏移
        data += b'\x00\x00\x00\x00'
        # 文件内容
        data += content.encode(cls.ENCODING, 'ignore')

        return SanSiPacketReq.pack(what=SanSiWhat.UPLOAD_FILE,
                                   data=data)

    @classmethod
    def get_now_play_content(cls) -> bytes:
        return SanSiPacketReq.pack(what=SanSiWhat.GET_NOW_PLAY_CONTENT,
                                   data=b'')

    @classmethod
    def lazy_parser(cls, recv_buffer: bytes) -> Union["NowPlayContentTags", "NowBrightnessTags"]:
        """
        如果你很懒的话，那就一键使用这个函数解析吧！

        :param recv_buffer:
        :return:
        """
        length = len(recv_buffer)
        match length:
            case 9:
                return cls.parser_now_brightness(recv_buffer)
            case _:
                return cls.parser_now_play_content(recv_buffer)

    @classmethod
    def parser(cls, recv_buffer: bytes) -> bytes:
        """
        :param recv_buffer:
        :return:
        """
        try:
            # 长度校验
            if len(recv_buffer) < cls.PROTOCOL_MIN_LENGTH:
                raise ProtocolParserError('Length is less than the minimum length')
            # crc 校验
            packet = SanSiPacketRsp.unpack(recv_buffer)
        except CrcError as e:
            raise ProtocolParserError(e.message)
        else:
            return packet.data

    @classmethod
    def parser_now_play_content(cls, recv_buffer: bytes) -> NowPlayContentTags:
        """
        返回字典键值说明， 默认没有则为None
            raw_str: 原始字符串
            font: 字体， h 表示黑体、 k 表示楷体、 s 表示宋体、 f 表示仿宋体
            font_height: 字体高度，1-64
            font_width: 字体宽度, 同上
            text_color: 文本颜色，格式 RRRGGGBBBYYY
            text: 文本
            image_type: 图片类型，B表示bmp， J表示jpg， G表示gif
            image_name: 图片文件名，xxx
        :param recv_buffer:
        :return:
        """
        try:
            data = cls.parser(recv_buffer)
        except ProtocolParserError:
            raise

        tags = NowPlayContentTags()

        remaining_str = data.decode(cls.ENCODING)

        # 除去\n
        remaining_str = remaining_str.replace('\\n', ' ')

        tags.raw_str = remaining_str

        # 字体，字体大小
        font_search_result = re.search(r'\\f([a-zA-Z])(\d{2})(\d{2})', remaining_str)

        if font_search_result:
            tags.font = font_search_result.group(1)
            font_height = font_search_result.group(2)
            font_width = font_search_result.group(3)
            tags.font_size = f'{font_height}{font_width}'
            remaining_str = remaining_str.replace(font_search_result.group(), '')

        # 字符颜色
        text_color_search_result = re.search(r'\\c(\d{12})', remaining_str)

        if text_color_search_result:
            tags.text_color = text_color_search_result.group(1)
            remaining_str = remaining_str.replace(text_color_search_result.group(), '')

        # 文本内容
        text_search_result = re.search(r'[\u4e00-\u9fff].*[\u4e00-\u9fff]', remaining_str)

        if text_search_result:
            tags.text = text_search_result.group()
            remaining_str = remaining_str.replace(text_search_result.group(), '')

        # 图片内容
        image_search_result = re.search(r'\\([BJG])(\d{3})', remaining_str)
        if image_search_result:
            tags.image_name = image_search_result.group(2)

    
        return tags

    @classmethod
    def parser_now_brightness(cls, recv_buffer: bytes) -> NowBrightnessTags:
        """
        data组成：【亮度调节方式 1B】【显示亮度 2B】
        亮度调节方式：'0'表示自动，'1'表示手动

        亮度范围0-31

        send:
        02 30 30 30 36 BA 4C 03
        recv:
        02 30 31 31 31 35 F4 74 03

        :param recv_buffer:
        :return: 当前亮度值
        """
        max_brightness = 31
        tags = NowBrightnessTags()
        try:
            data = cls.parser(recv_buffer)
        except ProtocolParserError:
            raise

        if len(data) != 3:
            raise ProtocolParserError('Data length is not 3')

        first = int(chr(data[1]))
        second = int(chr(data[2]))
        brightness = first * 10 + second
        # 亮度显示百分比
        percentage = round(brightness / max_brightness * 100)
        tags.brightness = percentage
        return tags


class ProtocolConfig:
    # 报文编码
    encoding: str = 'gbk'
    # 报文最小长度
    min_length: int = 7
    # 换行符
    line_break: str = "\\n"
    # 最大亮度
    max_brightness = 31


class ProtocolMessage:
    def __init__(self, config: ProtocolConfig = None):
        self.config = config or ProtocolConfig()

    def play_list(self, play_id: int = 1) -> bytes:
        """
        发送：
           "98"             2 字节帧类型
           编号             3 字节 ASCII 码，预置播放表的编号
       应答：
           执行结果         1 字节 ASCII 码

        >>> print(ProtocolMessage().play_list().hex(" "))
        02 30 30 39 38 30 30 31 9d fb 03

        :param play_id:
        :return:
        """
        data = f"{play_id:03d}".encode(self.config.encoding)
        return SanSiPacketReq.pack(what=SanSiWhat.PLAY_LIST,
                                   data=data)

    def upload_file(self, content: str, file_name: str = "play.lst") -> bytes:
        """
        发送：
           "10"             2 字节帧类型
           文件名           不定长 ASCII 码字符串
           分隔符           1 字节，0x2B，表明文件名的结束
           文件指针偏移     4 字节十六进制数，先发高字节，后发低字节
           一段文件内容     不定长，0-2048 字节
       应答：
           执行结果         1 字节 ASCII 码
           错误信息         不定长 ASCII 码字符串

        :param content:
        :param file_name:
        :return:
        """
        data = file_name.encode(self.config.encoding)
        # 分隔符，代表文件名结束
        data += b'\x2B'
        # 文件指针偏移
        data += b'\x00\x00\x00\x00'
        # 文件内容
        data += content.encode(self.config.encoding, 'ignore')

        return SanSiPacketReq.pack(what=SanSiWhat.UPLOAD_FILE,
                                   data=data)

    def get_now_play_content(self) -> bytes:
        """
        发送：
           "97"             2 字节帧类型
       应答：
           序号             3 字节 ASCII 码，当前显示内容在播放表中的序号
           停留时间         5 字节 ASCII 码，当前显示内容的停留时间
           出字方式         2 字节 ASCII 码，当前显示内容的出字方式
           出字速度         5 字节 ASCII 码，当前显示内容的出字速度
           显示字符串       不定长 ASCII 码字符串，当前正在显示的内容，带转义符

        >>> print(ProtocolMessage().get_now_play_content().hex(" "))
        02 30 30 39 37 10 f5 03

        :return:
        """
        return SanSiPacketReq.pack(what=SanSiWhat.GET_NOW_PLAY_CONTENT,
                                   data=b"")

    def download_file(self, file_name: str = "play.lst") -> bytes:
        """
        发送：
           "09"             2 字节帧类型
           文件名           不定长 ASCII 码字符串
           文件指针偏移     4 字节十六进制数，先发高字节，后发低字节
       应答：
           一段文件内容     不定长，0-2048 字节

        >>> print(ProtocolMessage().download_file().hex(" "))
        02 30 30 30 39 70 6c 61 79 2e 6c 73 74 00 00 00 00 57 2a 03

        :param file_name:
        :return:
        """
        # 文件名
        data = file_name.encode(self.config.encoding)
        # 文件指针偏移
        data += b'\x00\x00\x00\x00'
        return SanSiPacketReq.pack(what=SanSiWhat.DOWNLOAD_FILE,
                                   data=data)

    def set_now_brightness(self, brightness: int = 15) -> bytes:
        """
        设置当前亮度

        >>> print(ProtocolMessage().set_now_brightness().hex(" "))
        02 30 30 30 35 31 35 31 35 31 35 5e a0 03

        :param brightness: 协议亮度范围 0-31
        :return:
        """
        brightness = max(0, min(31, brightness))

        first = brightness // 10
        second = brightness % 10

        # 红，绿，蓝三基色相同
        data = b''.join(
            [bytes([ord(str(first))]), bytes([ord(str(second))])] * 3
        )
        return SanSiPacketReq.pack(what=SanSiWhat.SET_NOW_BRIGHTNESS,
                                   data=data)

    def get_now_brightness(self) -> bytes:
        """
        >>> print(ProtocolMessage().get_now_brightness().hex(" "))
        02 30 30 30 36 ba 4c 03

        :return:
        """
        return SanSiPacketReq.pack(what=SanSiWhat.GET_NOW_BRIGHTNESS,
                                   data=b'')


class ProtocolParser:
    def __init__(self, raw_data: bytes, config: ProtocolConfig = None):
        self.raw_data = raw_data
        self.config = config or ProtocolConfig()

    def parse_packet(self) -> SanSiPacketRsp:
        """解析成包结构

        :raise ProtocolParserError
        :return:
        """
        if len(self.raw_data) < self.config.min_length:
            raise exceptions.ProtocolParserError(f'Length is less than the minimum length '
                                                 f'{self.config.min_length}: {self.raw_data.hex()}')
        try:
            p = SanSiPacketRsp.unpack(self.raw_data)
        except exceptions.CrcError as e:
            raise exceptions.ProtocolParserError(f'Crc error: {e}') from e
        except Exception as e:
            raise exceptions.ProtocolParserError(f'unpack error: {e}') from e

        return p

    def parse_tags(self) -> NowBrightnessTags | NowPlayAllContentTags | NowPlayContentTags:
        """解析成点位结构

        :raises ProtocolParserError: 解析错误
        :return: 当前显示内容或当前显示列表
        :rtype: NowPlayContentTags | NowPlayAllContentTags
        """
        p = self.parse_packet()
        length = len(self.raw_data)
        match length:
            case 9:
                return self._parse_now_brightness(p.data)
            case _:
                return self._parse_now_play_content(p.data)

    def _parse_item(self, data_str: str) -> NowPlayContentTags:
        """解析目标item内容

        e.g.
            200, 1, 0, \B003\C048008\fk3232\c255000000000\S05\s000255000000hi, 你好

        :param data_str:
        :return:
        """

        tags = NowPlayContentTags()
        # 原单位是百分之一秒
        tags.duration = int(int(data_str[3:8]) * 0.01)
        tags.screen_in = str(int(data_str[8:10]))
        tags.raw_str = data_str[15:]

        # 字体，字体大小
        font_search_result = re.search(r'\\f([a-zA-Z])(\d{2})(\d{2})', tags.raw_str)

        if font_search_result:
            tags.font = font_search_result.group(1)
            font_height = font_search_result.group(2)
            font_width = font_search_result.group(3)
            tags.font_size = f'{font_height}{font_width}'

        # 字符颜色
        text_color_search_result = re.search(r'\\c(\d{12})', tags.raw_str)

        if text_color_search_result:
            tags.text_color = text_color_search_result.group(1)

        # 文本内容
        text_search_result = re.search(r'[\u4e00-\u9fff].*[\u4e00-\u9fff]', tags.raw_str)

        if text_search_result:
            tags.text = text_search_result.group()

        # 图片内容
        image_search_result = re.search(r'\\([BJG])(\d{3})', tags.raw_str)
        if image_search_result:
            tags.image_type = image_search_result.group(1)
            tags.image_name = image_search_result.group(2)

        return tags

    def _parse_now_play_content(self, data: bytes) -> NowPlayContentTags:
        """
        返回字典键值说明， 默认没有则为None
            raw_str: 原始字符串
            font: 字体， h 表示黑体、 k 表示楷体、 s 表示宋体、 f 表示仿宋体
            font_height: 字体高度，1-64
            font_width: 字体宽度, 同上
            text_color: 文本颜色，格式 RRRGGGBBBYYY
            text: 文本
            image_type: 图片类型，B表示bmp， J表示jpg， G表示gif
            image_name: 图片文件名，xxx
        :param data:
        :return:
        """
        tags = self._parse_item(data.decode(self.config.encoding))
        return tags

    def _parse_now_play_all_content(self, data: bytes) -> NowPlayAllContentTags:
        pass

    def _parse_now_brightness(self, data: bytes) -> NowBrightnessTags:
        """
        data组成：【亮度调节方式 1B】【显示亮度 2B】
        亮度调节方式：'0'表示自动，'1'表示手动

        亮度范围0-31

        send:
        02 30 30 30 36 BA 4C 03
        recv:
        02 30 31 31 31 35 F4 74 03

        :param data:
        :return: 当前亮度值
        """

        tags = NowBrightnessTags()

        if len(data) != 3:
            raise ProtocolParserError('Data length is not 3')

        first = int(chr(data[1]))
        second = int(chr(data[2]))
        brightness = first * 10 + second
        # 亮度显示百分比
        percentage = round(brightness / self.config.max_brightness * 100)
        tags.brightness = percentage
        return tags


if __name__ == '__main__':
    import doctest

    doctest.testmod()
