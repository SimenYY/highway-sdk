#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: sansiClient.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/8/8 10:52
"""
from highway_sdk.core.client import Client
from highway_sdk.core.exceptions import (HostResponseTimeoutError,
                                         ProtocolParserError,
                                         ResponseError,
                                         InvalidSocketError)
from .protocol import Protocol
from .utils.constants import SanSiReturnCode
from loguru import logger


class SanSiClient(Client):

    def __init__(self, host: str = 'localhost', port: int = 2929):
        super().__init__(host, port)

    def __send_file_name_and_content(self, content: str, play_id: int = 0) -> None:
        """
        当文件名固定为play.lst时，是替换当前播放列表

        上载文件
        :param content:
        :param play_id:
        :return:
        """
        # 在哪里使用就在哪里做防卫式编程
        if self.sock is None:
            raise InvalidSocketError('__send_file_name_and_content sock is None')

        send_buffer = Protocol.send_file_name_and_content(content, play_id)

        try:
            self.sock.send(send_buffer)
            recv_buffer = self.sock.recv(self.buffer_size)
            data = Protocol.parser(recv_buffer)
        except TimeoutError as e:
            raise HostResponseTimeoutError(f'__send_file_name_and_content {e}')
        except ProtocolParserError as e:
            raise ProtocolParserError(f'__send_file_name_and_content {e}')
        except Exception:
            raise
        else:
            # 数据域内容
            if data[:1] != b'\x30':
                error_msg = data[1:].decode(Protocol.ENCODING, 'ignore')
                raise ResponseError(error_msg)

    @logger.catch
    def set_play_list(self, content: str = '', play_id: int = 0) -> int:
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
        try:
            self.__send_file_name_and_content(content, play_id)
        except InvalidSocketError as e:
            logger.error(f'{e}')
            return SanSiReturnCode.SOCKET_ERROR
        except HostResponseTimeoutError as e:
            logger.error(f'{self.log_addr} {e}')
            return SanSiReturnCode.HOST_RESPONSE_TIMEOUT
        except ProtocolParserError as e:
            logger.error(f'{self.log_addr} {e}')
            return SanSiReturnCode.PROTOCOL_PARSER_ERROR
        except ResponseError as e:
            logger.error(f'{self.log_addr} {e}')
            return SanSiReturnCode.HOST_RESPONSE_ERROR
        except Exception as e:
            logger.error(f'{self.log_addr} {e}')
            return SanSiReturnCode.UNKNOWN_ERROR
        else:
            return SanSiReturnCode.SUCCESS

    @logger.catch
    def get_now_play_content(self) -> str | None:
        if self.sock is None:
            logger.error('socket is None')
            return None

        send_buffer = Protocol.get_now_play_content()

        try:
            self.sock.send(send_buffer)
            recv_buffer = self.sock.recv(self.buffer_size)
            data = Protocol.parser(recv_buffer)
        except (TimeoutError, ProtocolParserError, Exception) as e:
            logger.error(f'{self.log_addr} {e}')
            return None
        else:
            current_str = data[15:].decode(Protocol.ENCODING, 'ignore')
            return current_str
