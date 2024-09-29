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

from .utils.constants import SanSiWhat
from .utils.structs import SanSiPacketReq, SanSiPacketRsp
from highway_sdk.core.exceptions import CrcError, ProtocolParserError
from highway_sdk.vms.tags import NowPlayContent, NowBrightness


class Protocol:
    # 报文最小长度
    PROTOCOL_MIN_LENGTH = 7

    ENCODING = 'GBK'

    @classmethod
    def play_list(cls, play_id: int = 1) -> bytes:
        # 暂不实现
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

        return SanSiPacketReq.pack(what=SanSiWhat.SEND_FILE_NAME_AND_CONTENT,
                                   data=data)

    @classmethod
    def get_now_play_content(cls) -> bytes:
        return SanSiPacketReq.pack(what=SanSiWhat.GET_NOW_PLAY_CONTENT,
                                   data=b'')

    @classmethod
    def lazy_parser(cls, recv_buffer: bytes) -> dict:
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
    def parser_now_play_content(cls, recv_buffer: bytes) -> dict:
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

        tags = NowPlayContent()

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

        return tags.to_dict()

    @classmethod
    def parser_now_brightness(cls, recv_buffer: bytes) -> dict:
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
        tags = NowBrightness()
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
        return tags.to_dict()
