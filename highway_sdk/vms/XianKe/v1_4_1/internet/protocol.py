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
from highway_sdk.core.exceptions import ProtocolParserError, CrcError
from highway_sdk.vms.tags import NowPlayContentTags, NowPlayAllContentTags
from .structs import XianKePacket
from .constants import XianKeWhat


class Protocol:
    """协议类
    """
    # 报文最小长度
    min_length: int = 9
    # 报文编码
    encoding: str = 'utf-8'

    @classmethod
    def play_list(cls, file_name: str = r'000.xkl') -> bytes:
        """播放列表

        :param file_name:
        :return:
        """
        p = XianKePacket(what=XianKeWhat.PLAY_LIST,
                         data=file_name.encode(cls.encoding))
        return p.pack()

    @classmethod
    def upload_file(cls,
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
        data += file_path.encode(cls.encoding)
        data += b'\x30\x30\x30\x30'  # 文件偏移地址
        data += content.encode(cls.encoding)
        p = XianKePacket(what=XianKeWhat.upload_file, data=data)

        return p.pack()

    @classmethod
    def get_now_play_content(cls) -> bytes:
        """获取当前显示内容

        :return:
        """
        p = XianKePacket(what=XianKeWhat.GET_NOW_PLAY_CONTENT,
                         data=b'')
        return p.pack()

    @classmethod
    def get_now_play_all_content(cls) -> bytes:
        """获取当前显示列表

        :return:
        """
        p = XianKePacket(what=XianKeWhat.GET_NOW_PLAY_ALL_CONTENT,
                         data=b'')
        return p.pack()

    @classmethod
    def get_now_brightness(cls) -> bytes:
        """获取当前显示亮度

        :return:
        """
        p = XianKePacket(what=XianKeWhat.GET_NOW_BRIGHTNESS,
                         data=b'')
        return p.pack()

    @classmethod
    def set_now_brightness(cls, brightness: int) -> bytes:
        """设置当前显示亮度

        :param brightness:
        :return:
        """
        pass


class ProtocolParser:
    """协议解析
    """

    def __init__(self, raw_data: bytes):
        self.raw_data = raw_data

    def parse(self) -> XianKePacket:
        """
        :raise ProtocolParserError
        :return:
        """
        if len(self.raw_data) < Protocol.min_length:
            raise ProtocolParserError(f'Length is less than the minimum length '
                                      f'{Protocol.min_length}: {self.raw_data.hex()}')
        try:
            p = XianKePacket.unpack(self.raw_data)
        except CrcError as e:
            raise ProtocolParserError(f'Crc error: {e}') from e
        except Exception as e:
            raise ProtocolParserError(f'unpack error: {e}') from e

        return p

    def lazy_parse(self) -> NowPlayContentTags | NowPlayAllContentTags:
        """一键解析

        :raises ProtocolParserError: 解析错误
        :return: 当前显示内容或当前显示列表
        :rtype: NowPlayContentTags | NowPlayAllContentTags
        """

        p = self.parse()
        match p.what:
            case XianKeWhat.GET_NOW_PLAY_CONTENT:
                return self.parse_now_play_content(p.data)
            case XianKeWhat.GET_NOW_PLAY_ALL_CONTENT:
                return self.parse_now_play_all_content(p.data)
            case _:
                raise ProtocolParserError(f'Unknown what: {p.what}')

    @staticmethod
    def parse_now_play_content(data: bytes) -> NowPlayContentTags:
        """解析当前显示内容

        :param data:
        :return:
        :rtype: NowPlayContentTags
        """
        # todo
        pass

    @staticmethod
    def parse_now_play_all_content(data: bytes) -> NowPlayAllContentTags:
        """
        解析当前显示列表

        :param data:
        :return:
        :rtype: NowPlayAllContentTags
        """
        # todo
        pass




