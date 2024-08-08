#!/usr/bin/env python
# -*- coding: utf-8 -*-

import socket

from .utils.constants import NovaWhat, NovaOkRsp
from .utils.crc import CrcUtils
from .utils.escape import NovaEscape
from .utils.structs import NovaPacket
from highway_sdk.core.validators import (
    validate_ipv4_address,
    validate_port,
)
from highway_sdk.core.exceptions import ResponseError
import logging

logger = logging.getLogger(__name__)


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

    @classmethod
    def __make_send_packet(cls, what: bytes, data: bytes, **kwargs) -> bytes:

        to_check = NovaPacket.START
        to_check += NovaPacket.address
        to_check += what
        to_check += NovaEscape.send(data)
        to_check += NovaPacket.END

        crc_16 = CrcUtils.nova_crc_16_table(to_check)

        out_buffer = to_check
        out_buffer += crc_16.l
        out_buffer += crc_16.h

        return out_buffer

    def __send_file_name(self, sock: socket.socket, file_name: str) -> None:
        """
        发送文件名

        :raise TimeoutError
        :raise NovaFileNameError
        :param sock:
        :param file_name:
        :return: None
        """
        BLOCK_SIZE = 65535

        data = BLOCK_SIZE.to_bytes(2, 'little')
        data += file_name.encode('utf-8')

        send_buffer = self.__make_send_packet(what=NovaWhat.FILE_NAME_REQ,
                                              data=data)
        sock.send(send_buffer)
        try:
            recv_buffer = sock.recv(1024)
        except TimeoutError as e:
            raise TimeoutError(f'__send_file_name {e}')

        if (len(recv_buffer) == len(NovaOkRsp.FILE_NAME_OK_RSP)
                and recv_buffer == NovaOkRsp.FILE_NAME_OK_RSP):
            pass
        else:
            raise ResponseError(f'发送文件名响应失败')

    def __send_file_content(self, sock: socket.socket, content: str) -> None:
        """
        发送文件内容

        :raise TimeoutError
        :raise NovaFileContentError
        :param sock:
        :param content:
        :return: None
        """
        BLOCK_NUM = 1

        data = BLOCK_NUM.to_bytes(1, 'little')
        data += content.encode('utf-8')

        send_buffer = self.__make_send_packet(what=NovaWhat.FILE_CONTENT_REQ,
                                              data=data)
        sock.send(send_buffer)
        try:
            recv_buffer = sock.recv(1024)
        except TimeoutError as e:
            raise TimeoutError(f'__send_file_content {e}')

        if (len(recv_buffer) == len(NovaOkRsp.FILE_CONTENT_OK_RSP)
                and recv_buffer == NovaOkRsp.FILE_CONTENT_OK_RSP):
            pass
        else:
            raise ResponseError('发送文件内容响应失败')

    def __play_list(self, sock: socket.socket, play_id: int) -> None:
        """
        指定播放

        :raise TimeoutError
        :raise NovaPlayListError
        :param sock:
        :param play_id:
        :return: None
        """
        data = play_id.to_bytes(2, 'little')
        send_buffer = self.__make_send_packet(what=NovaWhat.PLAY_LIST_REQ,
                                              data=data)
        sock.send(send_buffer)
        try:
            recv_buffer = sock.recv(1024)
        except TimeoutError as e:
            raise TimeoutError(f'__play_list {e}')

        if (len(recv_buffer) == len(NovaOkRsp.PLAY_LIST_OK_RSP)
                and recv_buffer == NovaOkRsp.PLAY_LIST_OK_RSP):
            pass
        else:
            raise ResponseError('指定播放响应失败')

    def send_play_list(self, content: str, play_id: int = 1) -> bool:
        """
        发送节目，并播放

        :param content:
        :param play_id:
        :return: bool
        """

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                # 设置超时时间
                sock.settimeout(self.nova_rsp_timeout)
                sock.connect((self.ip, self.port))
                # 发送文件名
                file_name = f'play{play_id:03d}.lst'
                self.__send_file_name(sock, file_name)
                # 发送文件内容
                self.__send_file_content(sock, content)
                # 指定播放
                self.__play_list(sock, play_id)

            except ConnectionRefusedError as e:
                err_msg = f'{self.ip}:{self.port} {e}'
                logger.error(err_msg)
                return False
            except TimeoutError as e:
                err_msg = f'{self.ip}:{self.port} {e}'
                logger.error(err_msg)
                return False
            except ResponseError as e:
                err_msg = f'{self.ip}:{self.port} {e}'
                logger.error(err_msg)
                return False

        return True

    def get_log_prefix(self) -> str:
        return f'{self.ip}:{self.port}'



