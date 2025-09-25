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
import configparser
import re
from typing import Union

from highway_sdk.core.exceptions import CrcValidationError, ProtocolParserError
from highway_sdk.vms.tags import NowPlayContentTags, NowBrightnessTags, NowPlayAllContentTags
from .constants import NovaWhat
from .structs import NovaPacket


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
        data = block_num.to_bytes(2, 'little')
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
        """
        对情报板报文进行合法性校验

        :param recv_buffer:
        :param what:
        :return:
        """
        try:
            # 长度校验
            if len(recv_buffer) < cls.PROTOCOL_MIN_LENGTH:
                raise ProtocolParserError('Length is less than the minimum length')

            # crc校验
            packet = NovaPacket.unpack(recv_buffer)

            # 标识符校验
            if packet.what != what:
                raise ProtocolParserError('what error')
        except CrcValidationError as e:
            raise ProtocolParserError(e.message)
        else:
            return packet.data

    @classmethod
    def lazy_parser(cls, recv_buffer: bytes) -> Union["NowPlayContentTags", "NowBrightnessTags", "NowPlayAllContentTags"]:
        """
        如果你很懒的话，那就一键使用这个函数解析吧！

        :param recv_buffer:
        :return:
        """
        length = len(recv_buffer)
        what = recv_buffer[3:4]

        if length == 9 and what == NovaWhat.GET_NOW_BRIGHTNESS_RSP:
            return cls.parser_now_brightness(recv_buffer)
        elif what == NovaWhat.GET_NOW_PLAY_CONTENT_RSP:
            return cls.parser_now_play_content(recv_buffer)
        elif what == NovaWhat.GET_NOW_PLAY_ALL_CONTENT_RSP:
            return cls.parser_now_play_all_content(recv_buffer)
        else:
            raise ValueError(f'Unknown what = {what} and recv_buffer = {recv_buffer}')

    @classmethod
    def parser_now_play_content(cls, recv_buffer: bytes) -> NowPlayContentTags:
        """
        内容	        字节数	备注
        开关屏标志	1	    1-表示开屏 2-表示关屏，关屏时以下内容无效
        播放类型标志	1	    1-列表播放
        播放列表号	1	    当前播放的列表编号或测试编号
        内容头	    8	    [itemN]\r\n,N 为播放清单中 item 编号
        当前播放内容	n	    参见附录一 播放文件列表说明


        now_play_content:
            [item1]
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
            now_play_content = data[3:].decode(cls.ENCODING)
            tags = Protocol._parser_item(now_play_content)
        except Exception:
            raise
        else:
            return tags

    @staticmethod
    def _parser_item(item: Union[str, dict]) -> NowPlayContentTags:
        """
        解析目标，item内容，例如：
            [item1]
            param=100,1,1,1,0,5,1,0,1
            txt1=10,0,3,1616,1,8,0,车牌：冀A318AA大货车,192,320,0
            txtparam1=0,0

        :param item:
        :return:
        """
        like_config = configparser.ConfigParser()

        if type(item) is str:
            like_config.read_string(item)
        elif type(item) is dict:
            like_config.read_dict(item)

        item_name = like_config.sections()[0]
        # item_index = int(item_name[len('item'):])
        options = like_config.options(item_name)
        tags = NowPlayContentTags()
        for option in options:
            match option:
                case 'param':
                    param = like_config.get(item_name, 'param')
                    params = param.split(',')
                    tags.duration = int(params[0]) * 0.1
                    tags.screen_in = params[1]
                case _ if re.match(r'^txt\d+$', option):  # 匹配 txt+任意数字
                    raw = like_config.get(item_name, option)
                    params = raw.split(',')
                    tags.raw_str = raw
                    if tags.text is None:
                        tags.text = params[7]
                    else:
                        tags.text += params[7]
                    tags.text_color = params[4]
                    tags.font = params[2]
                    tags.font_size = params[3]
                case _ if re.match(r'^txtext\d+$', option):  # 匹配 txtext+任意数字
                    raw = like_config.get(item_name, option)
                    params = raw.split(',')
                    tags.raw_str = raw
                    if tags.text is None:
                        tags.text = params[17]
                    else:
                        tags.text += params[17]
                    tags.text_color = params[11]
                    tags.font = params[4]
                    tags.font_size = params[5]
                case _ if re.match(r'^img\d+$', option):  # 匹配 img+任意数字
                    raw = like_config.get(item_name, option)
                    params = raw.split(',')
                    tags.raw_str = raw
                    if tags.image_name is None:
                        tags.image_name = params[2]
                    else:
                        tags.image_name += params[2]
                case _ if re.match(r'^imgparam\d+$', option):
                    raw = like_config.get(item_name, option)
                    params = raw.split(',')
                    tags.duration = int(params[0]) *0.1
                case 'info':
                    raw = like_config.get(item_name, option)
                    params = raw.split(',')
                    tags.area_width = int(params[0])
                    tags.area_height = int(params[1])
                case _:
                    # raise ValueError(f'item {option} dont support')
                    pass

        return tags

    @classmethod
    def parser_now_brightness(cls, recv_buffer: bytes) -> NowBrightnessTags:
        """
        内容	        字节数	备注
        亮度控制模式	1	    0-获取亮度异常；
                            1-自动；
                            2-手动；
                            3-定时
        亮度值	    1	    当前亮度值；当亮度控制模式获取失败时，无该值, 范围【0-255】

        上位机发送: AA FF FF C3 CC 67 79
        设备回复: AA FF FF C3 02 FF CC 3A 2F

        all_content:
            [all]
            items=1
            [item1]
            param=100,1,1,1,0,5,1,0,1
            txt1=10,0,3,1616,1,8,0,车牌：冀A318AA大货车,192,320,0
            txtparam1=0,0

        :param recv_buffer:
        :return:
        """
        max_brightness = 255
        tags = NowBrightnessTags()
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
        return tags

    @classmethod
    def parser_now_play_all_content(cls, recv_buffer: bytes) -> NowPlayAllContentTags:
        """
        内容	                字节数	备注
        当前播放节目的列表编号	1	    0x01 代表 play001.lst
        当前播放节目的所有内容	N	    UTF8 编码，格式同附录的播放内容的单个 item 内所有内容

        上位机发送：AA FF FF 3A CC 77 D2
        设备回复：AA FF FF 3B 01 5B 61 6C 6C 5D 0A 69 74 65 6D 73 3D 31 0A 5B 69 74 65 6D 31 5D
        0A 70 61 72 61 6D 3D 31 30 30 2C 31 2C 31 2C 31 2C 30 2C 35 2C 31 2C 30 2C 31 0A 74 78 74 31 3D 31 30 2C 30
        2C 33 2C 31 36 31 36 2C 31 2C 38 2C 30 2C E8 BD A6 E7 89 8C EF BC 9A E5 86 80 41 33 31 38 41 41 E5 A4 A7 E8
        B4 A7 E8 BD A6 2C 31 39 32 2C 33 32 30 2C 30 0A 74 78 74 70 61 72 61 6D 31 3D 30 2C 30 CC D9 25

        all_content:
            [all]
            items=2
            [item1]
            param=100,1,1,1,0,5,1,0,1
            txt1=10,0,3,1616,1,8,0,车牌：冀A318AA大货车,192,320,0
            txtparam1=0,0
            [item2]
            param=100,1,1,1,0,5,1,0,1
            txt1=10,0,3,1616,1,8,0,车牌：冀A318AA大货车,192,320,0
            txtparam1=0,0

        :param recv_buffer:
        :return:
        """

        try:
            data = cls.parser(recv_buffer, NovaWhat.GET_NOW_PLAY_ALL_CONTENT_RSP)
        except ProtocolParserError:
            raise

        try:
            tags = NowPlayAllContentTags()
            now_all_content = data[1:].decode(cls.ENCODING)
            like_config = configparser.ConfigParser()
            like_config.read_string(now_all_content)
            items_count = int(like_config.get('all', 'items'))

            for i in range(1, items_count + 1):
                section = f'item{i}'
                item = {}
                for option in like_config.options(section):
                    item[option] = like_config.get(section, option)
                item_tags = Protocol._parser_item({section: item})
                tags.items.append(item_tags)
        except Exception:
            raise
        else:
            return tags
