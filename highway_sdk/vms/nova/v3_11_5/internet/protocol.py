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
from .utils.constants import NovaWhat
from .utils.structs import NovaPacket
from highway_sdk.core.exceptions import CrcError, ProtocolParserError


class Protocol:
    # 报文最小长度
    PROTOCOL_MIN_LENGTH = 7

    @classmethod
    def get_device_size(cls):
        return NovaPacket.pack(what=NovaWhat.GET_DEVICE_SIZE_REQ,
                               data=b'')

    @classmethod
    def file_name(cls, file_name: str, block_size: int = 65535):
        data = block_size.to_bytes(2, 'little')
        data += file_name.encode('utf-8', 'ignore')
        return NovaPacket.pack(what=NovaWhat.FILE_NAME_REQ,
                               data=data)

    @classmethod
    def file_content(cls, content: str, block_num: int = 1):
        data = block_num.to_bytes(1, 'little')
        data += content.encode('utf-8', 'ignore')
        return NovaPacket.pack(what=NovaWhat.FILE_CONTENT_REQ,
                               data=data)

    @classmethod
    def play_list(cls, play_id: int = 1):
        data = play_id.to_bytes(1, 'big')
        return NovaPacket.pack(what=NovaWhat.PLAY_LIST_REQ,
                               data=data)

    @classmethod
    def get_now_play_content(cls):
        return NovaPacket.pack(what=NovaWhat.GET_NOW_PLAY_CONTENT_REQ,
                               data=b'')

    @classmethod
    def get_now_play_all_content(cls):
        return NovaPacket.pack(what=NovaWhat.GET_NOW_PLAY_ALL_CONTENT_REQ,
                               data=b'')

    @classmethod
    def Parser(cls, recv_buffer: bytes, what: bytes) -> bytes | None:
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
