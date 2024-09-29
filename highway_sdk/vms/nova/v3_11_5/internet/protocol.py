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

from highway_sdk.core.exceptions import CrcError, ProtocolParserError
from highway_sdk.vms.tags import NowPlayContent, NowBrightness
from .utils.constants import NovaWhat
from .utils.structs import NovaPacket


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
        """
        nova手动控制命令不支持
        :param brightness:
        :return:
        """
        pass

    @classmethod
    def get_now_brightness(cls) -> bytes:
        return NovaPacket.pack(what=NovaWhat.GET_NOW_BRIGHTNESS_REQ,
                               data=b'')

    @classmethod
    def get_screen_switch_status(cls) -> bytes:
        return NovaPacket.pack(what=NovaWhat.GET_SCREEN_SWITCH_STATUS_REQ,
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
        """
        内容	        字节数	备注
        开关屏标志	1	    1-表示开屏 2-表示关屏，关屏时以下内容无效
        播放类型标志	1	    1-列表播放
        播放列表号	1	    当前播放的列表编号或测试编号
        内容头	    8	    [itemN]\r\n,N 为播放清单中 item 编号
        当前播放内容	n	    参见附录一 播放文件列表说明


        now_play_content:
            param=100,1,1,1,0,5,1,0,1
            txt1=10,0,3,1616,1,8,0,车牌：冀A318AA大货车,192,320,0
            txtparam1=0,0

        :param recv_buffer:
        :return:
        """
        try:
            data = cls.parser(recv_buffer, NovaWhat.GET_NOW_PLAY_CONTENT_RSP)
        except ProtocolParserError:
            raise

        try:
            tags = NowPlayContent()

            now_play_content = data[11:].decode(cls.ENCODING)

            parts = now_play_content.split('\n')
            media_type_n, reminder = parts[1].split('=', 1)
            params: list = reminder.split(',')
            media_type = media_type_n[:-1]
            match media_type:
                case 'txt':
                    tags.raw_str = reminder
                    tags.text = params[7]
                    tags.text_color = params[4]
                    tags.font = params[2]
                    tags.font_size = params[3]
                case 'txtext':
                    tags.raw_str = reminder
                    tags.text = params[17]
                    tags.text_color = params[11]
                    tags.font = params[4]
                    tags.font_size = params[5]
                case 'img':
                    tags.raw_str = reminder
                    tags.image_name = params[2]
                case _:
                    ValueError(f'media_type {media_type} not support')
        except Exception:
            raise
        else:
            return tags.to_dict()

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
        max_brightness = 255
        tags = NowBrightness()
        try:
            data = cls.parser(recv_buffer, NovaWhat.GET_NOW_BRIGHTNESS_RSP)
        except ProtocolParserError:
            raise

        if len(data) != 2:
            raise ProtocolParserError('data length is not 2')

        # mode = data[0]
        brightness = data[1]
        # 亮度显示百分比
        percentage = round(brightness / max_brightness * 100)
        tags.brightness = percentage
        return tags.to_dict()
