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
from highway_sdk.core.validators import (
    validate_ipv4_address,
    validate_port,
)
from .protocol import Protocol
from .utils.constants import (
    NovaWhat,
    NovaReturnCode
)
from .utils.crc import Bytes16


class NovaClient:
    """
    详情用法可参考 http://172.16.1.53/supconit/highway_sdk/-/tree/dev?ref_type=heads
    """
    # 通信响应超时时间
    nova_rsp_timeout: int = 3
    # 接受字节流大小单位
    buf_size: int = 1024

    def __init__(self, ip: str, port: int = 5000):
        """
        不合法的通信地址要让实例一开始就不成立
        """
        validate_ipv4_address(ip)
        validate_port(port)

        self.ip: str = ip
        self.port: int = port
        self._sock: Optional[socket.socket] = None

    def __enter__(self):
        self.make_connection()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()
        if exc_type is not None:
            logger.error(f'{self.log_prefix()} {exc_type} {exc_val} {exc_tb}')
        # 抑制异常
        return True

    @property
    def sock(self) -> socket.socket:
        return self._sock

    @sock.setter
    def sock(self, sock: socket.socket):
        self._sock = sock

    # @contextmanager
    # def client_session(self) -> Generator['NovaClient', None, None]:
    #     self.make_connection()
    #     try:
    #         yield self
    #     finally:
    #         self.close_connection()

    def make_connection(self):
        if self._sock is not None:
            return

        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(self.nova_rsp_timeout)
            self._sock.connect((self.ip, self.port))
        except (TimeoutError, ConnectionRefusedError, Exception) as e:
            logger.error(f'{self.log_prefix()} {e}')
            self.close_connection()

    def close_connection(self):
        if self._sock is not None:
            self._sock.close()
            self._sock = None

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

    def log_prefix(self) -> str:
        return f'{self.ip}:{self.port}'

    @logger.catch
    def set_play_list(self, content: str, play_id: int = 1) -> int:
        """
        组合指令，发送文件名，发送文件内容，指定播放

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
