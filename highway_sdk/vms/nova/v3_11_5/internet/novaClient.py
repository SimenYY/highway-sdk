#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
from contextlib import contextmanager
from typing import Optional

from loguru import logger

from highway_sdk.core.exceptions import (
    ResponseError,
    CrcError,
    InvalidSocketError,
    HostResponseTimeoutError
)
from highway_sdk.core.validators import (
    validate_ipv4_address,
    validate_port,
)
from .utils.constants import (
    NovaWhat,
    NovaReturnCode,
    get_success_rsp,
    get_success_rsp_len
)
from .utils.structs import NovaPacket
from .utils.crc import Bytes16


class NovaClient:
    # 通信响应超时时间
    nova_rsp_timeout: int = 3

    def __init__(self, ip: str, port: int = 5000):
        """
        不合法的通信地址要让实例一开始就不成立
        """
        validate_ipv4_address(ip)
        validate_port(port)

        self.ip: str = ip
        self.port: int = port
        self.sock: Optional[socket.socket] = None

    def __enter__(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.nova_rsp_timeout)
            self.sock.connect((self.ip, self.port))
        except ConnectionRefusedError as e:
            logger.error(f'{self.__log_prefix()} {e}')
        except TimeoutError as e:
            logger.error(f'{self.__log_prefix()} {e}')
        except Exception as e:
            logger.error(f'{self.__log_prefix()} {e}')
        finally:
            return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sock.__exit__()
        self.sock = None
        if exc_type:
            logger.error(f'{self.__log_prefix()} {exc_val}')

    # @contextmanager
    # def connect(self):
    #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.sock:
    #         try:
    #             self.sock.settimeout(self.nova_rsp_timeout)
    #             self.sock.connect((self.ip, self.port))
    #         except ConnectionRefusedError as e:
    #             logger.error(f'{self.__log_prefix()} {e}')
    #         except TimeoutError as e:
    #             logger.error(f'{self.__log_prefix()} {e}')
    #         except Exception as e:
    #             logger.error(f'{self.__log_prefix()} {e}')
    #         finally:
    #             yield self
    #             self.sock = None

    def __send_file_name(self, file_name: str) -> None:
        """
        发送文件名
        :raise HostResponseTimeoutError
        :raise ResponseError
        :param file_name:
        :return: None
        """
        BLOCK_SIZE = 65535

        data = BLOCK_SIZE.to_bytes(2, 'little')
        data += file_name.encode('utf-8', 'ignore')

        send_buffer = NovaPacket.pack(what=NovaWhat.FILE_NAME_REQ,
                                      data=data)
        self.sock.send(send_buffer)
        try:
            recv_buffer = self.sock.recv(1024)
        except TimeoutError as e:
            raise HostResponseTimeoutError(f'__send_file_name {e}')

        if (len(recv_buffer) == get_success_rsp_len(NovaWhat.FILE_NAME_RSP)
                and recv_buffer == get_success_rsp(NovaWhat.FILE_NAME_RSP)):
            pass
        else:
            raise ResponseError(f'发送文件名响应失败')

    def __send_file_content(self, content: str) -> None:
        """
        发送文件内容
        :raise HostResponseTimeoutError
        :raise ResponseError
        :param content:
        :return: None
        """
        BLOCK_NUM = 1

        data = BLOCK_NUM.to_bytes(1, 'little')
        data += content.encode('utf-8', 'ignore')

        send_buffer = NovaPacket.pack(what=NovaWhat.FILE_CONTENT_REQ,
                                      data=data)
        self.sock.send(send_buffer)
        try:
            recv_buffer = self.sock.recv(1024)
        except TimeoutError as e:
            raise HostResponseTimeoutError(f'__send_file_content {e}')

        if (len(recv_buffer) == get_success_rsp_len(NovaWhat.FILE_CONTENT_RSP)
                and recv_buffer == get_success_rsp(NovaWhat.FILE_CONTENT_RSP)):
            pass
        else:
            raise ResponseError('发送文件内容响应失败')

    def __play_list_by_id(self, play_id: int) -> None:
        """
        指定播放
        :raise HostResponseTimeoutError
        :raise ResponseError
        :param play_id:
        :return: None
        """
        data = play_id.to_bytes(2, 'little')
        send_buffer = NovaPacket.pack(what=NovaWhat.PLAY_LIST_REQ,
                                      data=data)
        self.sock.send(send_buffer)
        try:
            recv_buffer = self.sock.recv(1024)
        except TimeoutError as e:
            raise HostResponseTimeoutError(f'__play_list {e}')

        if (len(recv_buffer) == get_success_rsp_len(NovaWhat.PLAY_LIST_RSP)
                and recv_buffer == get_success_rsp(NovaWhat.PLAY_LIST_RSP)):
            pass
        else:
            raise ResponseError('指定播放响应失败')

    def __log_prefix(self) -> str:
        return f'{self.ip}:{self.port}'

    @logger.catch
    def set_play_list(self, content: str, play_id: int = 1) -> int:
        """
        组合指令，发送文件名，发送文件内容，指定播放

        :param content:
        :param play_id:
        :return: int 返回码
        """
        if self.sock is None:
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
            logger.error(f'{self.__log_prefix()} {e}')
            return NovaReturnCode.HOST_RESPONSE_TIMEOUT
        except ResponseError as e:
            logger.error(f'{self.__log_prefix()} {e}')
            return NovaReturnCode.HOST_RESPONSE_ERROR

        return NovaReturnCode.SUCCESS

    @logger.catch
    def get_device_size(self) -> tuple[int, int] | None:
        """
        获取屏幕点阵大小
        :return: 宽，高 or None
        """
        if self.sock is None:
            logger.error('socket is none.')
            return None

        data = b''
        send_buffer = NovaPacket.pack(what=NovaWhat.SCREEN_WIDTH_HEIGHT_REQ,
                                      data=data)
        self.sock.send(send_buffer)
        try:
            recv_buffer = self.sock.recv(1024)
            if len(recv_buffer) != get_success_rsp(NovaWhat.SCREEN_WIDTH_HEIGHT_RSP):
                logger.error('host response length is incorrect.')
                return None
            packet = NovaPacket.unpack(recv_buffer)
        except TimeoutError as e:
            logger.error(f'{self.__log_prefix()} {e}')
        except CrcError as e:
            logger.error(f'{self.__log_prefix()} {e}')
        else:
            if packet.what == NovaWhat.SCREEN_WIDTH_HEIGHT_RSP:
                width = Bytes16(packet.data[:2]).reverse_bytes_to_int()
                height = Bytes16(packet.data[2:4]).reverse_bytes_to_int()
                return width, height
            else:
                logger.error('host response what is incorrect.')

        return None

    @logger.catch
    def get_now_play_content(self) -> str | None:
        """
        获取当前播放内容
        :return: 当前item内容 or None
        """
        if self.sock is None:
            logger.error('socket is none.')
            return None

        data = b''
        send_buffer = NovaPacket.pack(what=NovaWhat.GET_PLAYING_ITEM_REQ,
                                      data=data)
        self.sock.send(send_buffer)
        try:
            recv_buffer = self.sock.recv(1024)
            if len(recv_buffer) != get_success_rsp_len(NovaWhat.GET_PLAYING_ITEM_RSP):
                logger.error('host response length is incorrect.')
                return None
            packet = NovaPacket.unpack(recv_buffer)
        except TimeoutError as e:
            logger.error(f'{self.__log_prefix()} {e}')
        except CrcError as e:
            logger.error(f'{self.__log_prefix()} {e}')
        else:
            if packet.what == NovaWhat.GET_PLAYING_ITEM_RSP:
                current_item = packet.data[1:]
                return current_item.decode('utf-8', 'ignore')
            else:
                logger.error('host response what is incorrect.')
        return None

    @logger.catch
    def get_now_play_all_content(self) -> str | None:
        """
        获取当前播放全部内容
        :return: 当前播放全部内容 or None
        """
        if self.sock is None:
            logger.error('socket is none.')
            return None

        data = b''
        send_buffer = NovaPacket.pack(what=NovaWhat.GET_PLAYING_ALL_REQ,
                                      data=data)
        self.sock.send(send_buffer)
        try:
            recv_buffer = self.sock.recv(1024)
            if len(recv_buffer) != get_success_rsp_len(NovaWhat.GET_PLAYING_ALL_RSP):
                logger.error('host response length is incorrect.')
                return None
            packet = NovaPacket.unpack(recv_buffer)
        except TimeoutError as e:
            logger.error(f'{self.__log_prefix()} {e}')
        except CrcError as e:
            logger.error(f'{self.__log_prefix()} {e}')
        else:
            if packet.what == NovaWhat.GET_PLAYING_ALL_RSP:
                current_all_item = packet.data[1:]
                return current_all_item.decode('utf-8', 'ignore')
            else:
                logger.error('host response what is incorrect.')

        return None
