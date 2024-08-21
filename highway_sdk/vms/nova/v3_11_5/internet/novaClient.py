#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
from typing import Optional

from loguru import logger

from highway_sdk.core.exceptions import (
    ResponseError,
    ProtocolParserError,
    HostResponseTimeoutError
)
from highway_sdk.core.client import Client
from .protocol import Protocol
from .utils.constants import (
    NovaWhat,
    NovaReturnCode
)
from .utils.crc import Bytes16


class NovaClient(Client):
    """
    诺瓦通信客户端
    详情用法可参考 http://172.16.1.53/supconit/highway_sdk/-/tree/dev?ref_type=heads
    """

    def __init__(self, ip: str = 'localhost', port: int = 5000):
        super().__init__(ip, port)

    def __send_file_name(self, file_name: str) -> None:
        """
        发送文件名
        :raise HostResponseTimeoutError
        :raise ResponseError
        :param file_name:
        :return: None
        """

        send_buffer = Protocol.file_name(file_name)
        self._sock.send(send_buffer)
        try:
            recv_buffer = self._sock.recv(self.buf_size)
            data = Protocol.Parser(recv_buffer, NovaWhat.FILE_NAME_RSP)
        except TimeoutError as e:
            raise HostResponseTimeoutError(f'__send_file_name recv timeout {e}')
        except ProtocolParserError as e:
            raise ProtocolParserError(f'__send_file_name parser error {e}')
        else:
            # 数据域内容： 执行结果1B
            if data != b'\x01':
                raise ResponseError('__send_file_name response error')

    def __send_file_content(self, content: str) -> None:
        """
        发送文件内容
        :raise HostResponseTimeoutError
        :raise ResponseError
        :param content:
        :return: None
        """

        send_buffer = Protocol.file_content(content)
        self._sock.send(send_buffer)
        try:
            recv_buffer = self._sock.recv(self.buf_size)
            data = Protocol.Parser(recv_buffer, NovaWhat.FILE_CONTENT_RSP)
        except TimeoutError as e:
            raise HostResponseTimeoutError(f'__send_file_content recv timeout {e}')
        except ProtocolParserError as e:
            raise ProtocolParserError(f'__send_file_content parser error {e}')
        else:
            # 数据域内容： 块号2B + 执行结果1B
            if data[2:] != b'\x01':
                raise ResponseError('__send_file_content response error')

    def __play_list_by_id(self, play_id: int) -> None:
        """
        指定播放
        :raise HostResponseTimeoutError
        :raise ResponseError
        :param play_id:
        :return: None
        """
        send_buffer = Protocol.play_list(play_id)
        self._sock.send(send_buffer)
        try:
            recv_buffer = self._sock.recv(self.buf_size)
            data = Protocol.Parser(recv_buffer, NovaWhat.PLAY_LIST_RSP)
        except TimeoutError as e:
            raise HostResponseTimeoutError(f'__play_list_by_id timeout {e}')
        except ProtocolParserError as e:
            raise ProtocolParserError(f'__play_list_by_id parser error {e}')
        else:
            # 数据域内容： 执行结果1B
            if data != b'\x01':
                raise ResponseError('__play_list_by_id response error')

    @logger.catch
    def set_play_list(self, content: str, play_id: int = 1) -> int:
        """
        组合指令，发送文件名，发送文件内容，指定播放

        返回码参考
        SUCCESS = 0
        SOCKET_ERROR = -1
        HOST_RESPONSE_TIMEOUT = -2
        HOST_RESPONSE_ERROR = -3
        PROTOCOL_PARSER_ERROR = -4

        :param content:
        :param play_id:
        :return: int 返回码
        """
        if self._sock is None:
            return NovaReturnCode.SOCKET_ERROR

        try:
            # 发送文件名
            file_name = f'play{play_id:03d}.lst'
            self.__send_file_name(file_name)
            # 发送文件内容
            self.__send_file_content(content)
            # 指定播放
            self.__play_list_by_id(play_id)
        except HostResponseTimeoutError as e:
            logger.error(f'{self.log_prefix()} {e}')
            return NovaReturnCode.HOST_RESPONSE_TIMEOUT
        except ProtocolParserError as e:
            logger.error(f'{self.log_prefix()} {e}')
            return NovaReturnCode.PROTOCOL_PARSER_ERROR
        except ResponseError as e:
            logger.error(f'{self.log_prefix()} {e}')
            return NovaReturnCode.HOST_RESPONSE_ERROR

        return NovaReturnCode.SUCCESS

    @logger.catch
    def get_device_size(self) -> tuple[int, int] | None:
        """
        获取屏幕点阵大小
        :return: 宽，高 or None
        """
        if self._sock is None:
            logger.error('socket is none.')
            return None

        send_buffer = Protocol.get_device_size()
        self._sock.send(send_buffer)
        try:
            recv_buffer = self._sock.recv(self.buf_size)
            data = Protocol.Parser(recv_buffer, NovaWhat.GET_DEVICE_SIZE_RSP)
        except (TimeoutError, ProtocolParserError) as e:
            logger.error(f'{self.log_prefix()} {e}')
        else:
            width = Bytes16(data[:2]).reverse_bytes_to_int()
            height = Bytes16(data[2:4]).reverse_bytes_to_int()

            return width, height

        return None

    @logger.catch
    def get_now_play_content(self) -> str | None:
        """
        获取当前播放内容
        :return: 当前item内容 or None
        """
        if self._sock is None:
            logger.error('socket is none.')
            return None

        send_buffer = Protocol.get_now_play_content()
        self._sock.send(send_buffer)
        try:
            recv_buffer = self._sock.recv(self.buf_size)
            data = Protocol.Parser(recv_buffer, NovaWhat.GET_NOW_PLAY_CONTENT_RSP)
        except (TimeoutError, ProtocolParserError) as e:
            logger.error(f'{self.log_prefix()} {e}')
        else:
            current_item = data[1:]
            return current_item.decode('utf-8', 'ignore')

        return None

    @logger.catch
    def get_now_play_all_content(self) -> str | None:
        """
        获取当前播放全部内容
        :return: 当前播放全部内容 or None
        """
        if self._sock is None:
            logger.error('socket is none.')
            return None

        send_buffer = Protocol.get_now_play_all_content()
        self._sock.send(send_buffer)
        try:
            recv_buffer = self._sock.recv(self.buf_size * 2)
            data = Protocol.Parser(recv_buffer, NovaWhat.GET_NOW_PLAY_ALL_CONTENT_RSP)
        except (TimeoutError, ProtocolParserError) as e:
            logger.error(f'{self.log_prefix()} {e}')
        else:
            current_all_item = data[1:]
            return current_all_item.decode('utf-8', 'ignore')

        return None
