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
:Time: 2024/8/15 13:41
"""
import dataclasses

from .utils.constants import NovaWhat
from .utils.structs import NovaPacket
from highway_sdk.core.exceptions import CrcError, ProtocolParserError


class Protocol:
    # 报文最小长度
    PROTOCOL_MIN_LENGTH = 7
    # 报文编码
    ENCODING = 'utf-8'

    @classmethod
    def get_device_size(cls) -> bytes:
        return NovaPacket.pack(what=NovaWhat.GET_DEVICE_SIZE_REQ,
                               data=b'')

    @classmethod
    def send_file_name(cls, file_name: str, block_size: int = 65535) -> bytes:
        data = block_size.to_bytes(2, 'little')
        data += file_name.encode(cls.ENCODING, 'ignore')
        return NovaPacket.pack(what=NovaWhat.SEND_FILE_NAME_REQ,
                               data=data)

    @classmethod
    def send_file_content(cls, content: str, block_num: int = 1) -> bytes:
        data = block_num.to_bytes(1, 'little')
        data += content.encode(cls.ENCODING, 'ignore')
        return NovaPacket.pack(what=NovaWhat.SEND_FILE_CONTENT_REQ,
                               data=data)

    @classmethod
    def play_list(cls, play_id: int = 1) -> bytes:
        data = play_id.to_bytes(1, 'big')
        return NovaPacket.pack(what=NovaWhat.PLAY_LIST_REQ,
                               data=data)

    @classmethod
    def get_now_play_content(cls) -> bytes:
        return NovaPacket.pack(what=NovaWhat.GET_NOW_PLAY_CONTENT_REQ,
                               data=b'')

    @classmethod
    def get_now_play_all_content(cls) -> bytes:
        return NovaPacket.pack(what=NovaWhat.GET_NOW_PLAY_ALL_CONTENT_REQ,
                               data=b'')

    @classmethod
    def set_now_brightness(cls, brightness: int) -> bytes:
        pass

    @classmethod
    def get_now_brightness(cls) -> bytes:
        return NovaPacket.pack(what=NovaWhat.GET_NOW_BRIGHTNESS_REQ,
                               data=b'')

    @classmethod
    def parser(cls, recv_buffer: bytes, what: bytes) -> bytes | None:
        try:
            # 长度校验
            if len(recv_buffer) < cls.PROTOCOL_MIN_LENGTH:
                raise ProtocolParserError('Length is less than the minimum length')

            # crc校验
            packet = NovaPacket.unpack(recv_buffer)

            # 标识符校验
            if packet.what != what:
                raise ProtocolParserError('what error')
        except CrcError as e:
            raise ProtocolParserError(e.message)
        else:
            return packet.data

    @classmethod
    def lazy_parser(cls, recv_buffer) -> dict:
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
    def parser_now_play_content(cls, recv_buffer: bytes) -> dict:
        pass

    @classmethod
    def parser_now_brightness(cls, recv_buffer: bytes) -> dict:
        """
        内容	        字节数	备注
        亮度控制模式	1	    0-获取亮度异常；
                            1-自动；
                            2-手动；
                            3-定时
        亮度值	    1	    当前亮度值；当亮度控制模式获取失败时，无该值, 范围【0-255】

        上位机发送: AA FF FF C3 CC 67 79
        设备回复: AA FF FF C3 02 FF CC 3A 2F

        :param recv_buffer:
        :return:
        """
        try:
            data = cls.parser(recv_buffer, NovaWhat.GET_NOW_BRIGHTNESS_RSP)
        except ProtocolParserError:
            raise

        if len(data) != 2:
            raise ProtocolParserError('data length is not 2')

        mode = data[0]
        brightness = data[1]
        return {'brightness': brightness}
