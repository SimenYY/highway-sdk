#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: dmClient.py.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/8/20 13:54
"""

from loguru import logger

from highway_sdk.core.client import Client
from highway_sdk.core.exceptions import ProtocolParserError
from .protocol import Protocol
from .utils.constants import DmReturnCode
from .utils.constants import DmWhat


class DmClient(Client):
    """
    电明通信客户端
    详情用法可参考 http://172.16.1.53/supconit/highway_sdk/-/tree/dev?ref_type=heads
    """

    def __init__(self, host: str = 'localhost', port: int = 5009):
        super().__init__(host, port)
        # todo 增加使用协议属性，可以灵活更改协议的参数

    @logger.catch
    def set_play_list(self, content: str, play_id: int = 0) -> int:
        """
        发送播放表，并立即播放

        返回码参考
        SUCCESS = 0
        SOCKET_ERROR = -1
        HOST_RESPONSE_TIMEOUT = -2
        HOST_RESPONSE_ERROR = -3
        PROTOCOL_PARSER_ERROR = -4
        CLIENT_REQUEST_ERROR = -5
        UNKNOWN_ERROR = -99

        :param content:
        :param play_id:
        :return:
        """
        if self.sock is None:
            logger.error('socket is None')
            return DmReturnCode.SOCKET_ERROR
        try:
            send_buffer = Protocol.set_play_list(content, play_id)
            self.sock.send(send_buffer)

            recv_buffer = self.sock.recv(self.buffer_size)
            data = Protocol.Parser(recv_buffer, DmWhat.SEND_PLAY_LIST_AND_PLAY_RSP)
        except TimeoutError as e:
            logger.error(f'{self.log_addr} {e}')
            return DmReturnCode.HOST_RESPONSE_TIMEOUT
        except ProtocolParserError as e:
            logger.error(f'{self.log_addr} {e}')
            return DmReturnCode.PROTOCOL_PARSER_ERROR
        except Exception as e:
            logger.error(f'{self.log_addr} {e}')
            return DmReturnCode.UNKNOWN_ERROR
        else:
            match data:
                case b'\x31':
                    return DmReturnCode.SUCCESS
                case b'\x30':
                    logger.error(f'{self.log_addr} 响应异常')
                    return DmReturnCode.HOST_RESPONSE_ERROR
                case b'\x36':
                    logger.error(f'{self.log_addr} 播放表格式错误')
                    return DmReturnCode.CLIENT_REQUEST_ERROR
                case _:
                    logger.error(f'{self.log_addr} 响应未知错误 - {data}')
                    return DmReturnCode.UNKNOWN_ERROR

    @logger.catch
    def get_now_play_content(self) -> str | None:
        """
        当前页面字符串：“\C000000\Fs3232\T255000000000\K000000000000\WHello World”

        re参考
        pattern = r"\\W(.*?)(?:\\|$)"
        text_match = re.search(pattern, current_str)
        if text_match:
            return text_match.group(1)

        pattern = r"\\T(\d+)"
        color_match = re.search(pattern, current_str)
        if color_match:
            return color_match.group(1)

        pattern = r"\\F([a-zA-Z])\d+"
        font_match = re.search(pattern, current_str)
        if font_match:
            return font_match.group(1)

        :return:
        """
        if self.sock is None:
            logger.error('socket is None')
            return None

        send_buffer = Protocol.get_now_play_content()
        self.sock.send(send_buffer)
        try:
            rev_buffer = self.sock.recv(self.buffer_size)
            data = Protocol.Parser(rev_buffer, DmWhat.GET_NOW_PLAY_CONTENT_RSP)
        except (TimeoutError, ProtocolParserError) as e:
            logger.error(f'{self.log_addr} {e}')
        else:
            current_str = data[16:].decode('utf-8', 'ignore')
            return current_str

        return None
