#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket
from contextlib import contextmanager

from loguru import logger

from highway_sdk.core.exceptions import ResponseError
from highway_sdk.core.validators import (
    validate_ipv4_address,
    validate_port,
)
from .utils.constants import NovaWhat, NovaOkRsp
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
        self.sock = None

    @contextmanager
    def connect(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.sock:
            try:
                self.sock.settimeout(self.nova_rsp_timeout)
                self.sock.connect((self.ip, self.port))
            except ConnectionRefusedError as e:
                logger.error(f'{self.get_log_prefix()} {e}')
            except TimeoutError as e:
                logger.error(f'{self.get_log_prefix()} {e}')
            except Exception as e:
                logger.error(f'{self.get_log_prefix()} {e}')
            finally:
                yield self
                self.sock = None

    def __send_file_name(self, file_name: str) -> None:
        """
        发送文件名

        :raise TimeoutError
        :raise ResponseError
        :param file_name:
        :return: None
        """
        BLOCK_SIZE = 65535

        data = BLOCK_SIZE.to_bytes(2, 'little')
        data += file_name.encode('utf-8')

        send_buffer = NovaPacket.pack(what=NovaWhat.FILE_NAME_REQ,
                                      data=data)
        self.sock.send(send_buffer)
        try:
            recv_buffer = self.sock.recv(1024)
        except TimeoutError as e:
            raise TimeoutError(f'__send_file_name {e}')

        if (len(recv_buffer) == len(NovaOkRsp.FILE_NAME_OK_RSP)
                and recv_buffer == NovaOkRsp.FILE_NAME_OK_RSP):
            pass
        else:
            raise ResponseError(f'发送文件名响应失败')

    def __send_file_content(self, content: str) -> None:
        """
        发送文件内容

        :raise TimeoutError
        :raise ResponseError
        :param content:
        :return: None
        """
        BLOCK_NUM = 1

        data = BLOCK_NUM.to_bytes(1, 'little')
        data += content.encode('utf-8')

        send_buffer = NovaPacket.pack(what=NovaWhat.FILE_CONTENT_REQ,
                                      data=data)
        self.sock.send(send_buffer)
        try:
            recv_buffer = self.sock.recv(1024)
        except TimeoutError as e:
            raise TimeoutError(f'__send_file_content {e}')

        if (len(recv_buffer) == len(NovaOkRsp.FILE_CONTENT_OK_RSP)
                and recv_buffer == NovaOkRsp.FILE_CONTENT_OK_RSP):
            pass
        else:
            raise ResponseError('发送文件内容响应失败')

    def __play_list_by_id(self, play_id: int) -> None:
        """
        指定播放

        :raise TimeoutError
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
            raise TimeoutError(f'__play_list {e}')

        if (len(recv_buffer) == len(NovaOkRsp.PLAY_LIST_OK_RSP)
                and recv_buffer == NovaOkRsp.PLAY_LIST_OK_RSP):
            pass
        else:
            raise ResponseError('指定播放响应失败')

    def send_play_list_combined(self, content: str, play_id: int = 1) -> bool:
        """
        组合指令，发送文件名，发送文件内容，指定播放

        :param content:
        :param play_id:
        :return: bool
        """
        try:
            # 发送文件名
            file_name = f'play{play_id:03d}.lst'
            self.__send_file_name(file_name)
            # 发送文件内容
            self.__send_file_content(content)
            # 指定播放
            self.__play_list_by_id(play_id)
        except TimeoutError as e:
            logger.error(f'{self.get_log_prefix()} {e}')
            return False
        except ResponseError as e:
            logger.error(f'{self.get_log_prefix()} {e}')
            return False

        return True

    def get_log_prefix(self) -> str:
        return f'{self.ip}:{self.port}'

    def get_device_size(self):
        """
        获取屏幕点阵大小
        """
        data = bytes()
        send_buffer = NovaPacket.pack(what=NovaWhat.SCREEN_WIDTH_HEIGHT_REQ,
                                      data=data)
        self.sock.send(send_buffer)
        try:
            recv_buffer = self.sock.recv(1024)
            packet = NovaPacket.unpack(recv_buffer)
        except TimeoutError as e:
            raise TimeoutError(e)
        except ValueError as e:
            raise ValueError(e)
        else:
            if packet.what == NovaWhat.SCREEN_WIDTH_HEIGHT_RSP:
                width = Bytes16(packet.data[:2]).reverse_bytes_to_int()
                height = Bytes16(packet.data[2:4]).reverse_bytes_to_int()
                return width, height
            else:
                return None
