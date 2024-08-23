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
from .utils.constants import SanSiWhat
from .utils.structs import SanSiPacketReq, SanSiPacketRsp
from highway_sdk.core.exceptions import CrcError, ProtocolParserError


class Protocol:
    # 报文最小长度
    PROTOCOL_MIN_LENGTH = 7

    ENCODING = 'GBK'

    @classmethod
    def play_list(cls, play_id: int = 1) -> bytes:
        # 暂不实现
        pass

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
    def parser(cls, recv_buffer: bytes) -> bytes:
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
