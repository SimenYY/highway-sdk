#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: novaClient.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/8/1 9:35
:Department: 公路机电工程技术中心
:Copyright: ©1993-2023 浙江中控信息产业股份有限公司
"""
import socket

from .utils.constants import NovaWhat, NovaOkRsp
from .utils.crc import CrcUtils
from .utils.escape import NovaEscape
from .utils.exceptions import *
from .utils.structs import NovaPacket
from config import get_logger

logger = get_logger()


class NovaClient:
    nova_rsp_timeout: int = 3

    def __init__(self, ip: str, port: int = 5000):
        self.ip: str = ip
        self.port: int = port

    @classmethod
    def __make_send_packet(cls, what: bytes, data: bytes, **kwargs) -> bytes:
        to_check = b''.join([
            NovaPacket.START,
            NovaPacket.address,
            what,
            NovaEscape.send(data),
            NovaPacket.END,
        ])

        crc_16 = CrcUtils.nova_crc_16_table(to_check)

        out_buffer = b''.join([
            to_check,
            crc_16.l,
            crc_16.h
        ])

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
        data = b''.join([
            BLOCK_SIZE.to_bytes(2, 'little'),
            file_name.encode('utf-8'),
        ])

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
            raise NovaFileNameError

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
        data = b''.join([
            BLOCK_NUM.to_bytes(1, 'little'),
            content.encode('utf-8'),
        ])
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
            raise NovaFileContentError

    def __play_list(self, sock: socket.socket, play_id: int) -> None:
        """
        指定播放

        :raise TimeoutError
        :raise NovaPlayListError
        :param sock:
        :param play_id:
        :return: None
        """
        data = b''.join([
            play_id.to_bytes(2, 'little'),
        ])
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
            raise NovaPlayListError

    def send_play_list(self, content: str, play_id: int = 1) -> bool:
        """
        发送节目

        :param content:
        :param play_id:
        :return: bool
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
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
        except NovaException as e:
            err_msg = f'{self.ip}:{self.port} {e}'
            logger.error(err_msg)
            return False

        return True
