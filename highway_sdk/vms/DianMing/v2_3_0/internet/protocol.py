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
:Time: 2024/8/20 13:57
"""
from highway_sdk.core.exceptions import ProtocolParserError, CrcError
from .utils.structs import DmPacket
from .utils.constants import DmWhat


class Protocol:
    # 报文最小长度
    PROTOCOL_MIN_LENGTH = 11

    @classmethod
    def set_play_list(cls, content: str, play_id: int = 0) -> bytes:
        file_name = f'play{play_id:02d}.lst'

        # 文件下载项，默认
        data = b'\x2B'
        # 文件偏移地址，默认
        data += b'\x30\x30\x30\x30\x30\x30\x30\x30'
        data += file_name.encode('utf-8')
        data += content.encode('utf-8')

        return DmPacket.pack(what=DmWhat.SEND_PLAY_LIST_AND_PLAY_REQ,
                             data=data)

    @classmethod
    def get_now_play_content(cls) -> bytes:
        return DmPacket.pack(what=DmWhat.GET_NOW_PLAY_CONTENT_REQ,
                             data=b'')

    @classmethod
    def Parser(cls, recv_buffer: bytes, what: bytes) -> bytes | None:
        try:
            # 长度校验
            if len(recv_buffer) < cls.PROTOCOL_MIN_LENGTH:
                raise ProtocolParserError('Length is less than the minimum length')

            # crc 校验
            packet = DmPacket.unpack(recv_buffer)

            # 标识符校验
            if packet.what != what:
                raise ProtocolParserError(f'What error')
        except CrcError as e:
            raise ProtocolParserError(e.message)
        else:
            return packet.data