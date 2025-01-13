#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio

from highway_sdk import logger

from highway_sdk.vms.base.vmsClient import VmsClient, VmsAsyncClient
from highway_sdk.core.exceptions import (
    ResponseError,
    ProtocolParserError,
    HostResponseTimeoutError,
    InvalidSocketError
)
from highway_sdk.vms.crc import Bytes16
from .protocol import Protocol
from .utils.constants import (
    NovaWhat
)

from highway_sdk.vms.constants import DeviceReturnCode


class NovaClient(VmsClient):
    """
    诺瓦通信客户端
    详情用法可参考 http://172.16.1.53/supconit/highway_sdk/-/tree/dev?ref_type=heads
    """

    def get_now_brightness(self) -> str | None:
        pass

    def set_now_brightness(self, brightness: int) -> int:
        pass

    def __init__(self, host: str = 'localhost', port: int = 5000):
        super().__init__(host, port)

    def __send_file_name(self, file_name: str) -> None:
        """
        发送文件名
        :raise HostResponseTimeoutError
        :raise ResponseError
        :param file_name:
        :return: None
        """
        if self._sock is None:
            raise InvalidSocketError('__send_file_name sock is None')

        send_buffer = Protocol.send_file_name(file_name)

        try:
            self._sock.send(send_buffer)
            recv_buffer = self._sock.recv(self.buffer_size)
            data = Protocol.parser(recv_buffer, NovaWhat.SEND_FILE_NAME_RSP)
        except TimeoutError as e:
            raise HostResponseTimeoutError(f'__send_file_name recv timeout {e}')
        except ProtocolParserError as e:
            raise ProtocolParserError(f'__send_file_name parser error {e}')
        except Exception:
            raise
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
        if self._sock is None:
            raise InvalidSocketError('__send_file_content sock is None')

        send_buffer = Protocol.send_file_content(content)

        try:
            self._sock.send(send_buffer)
            recv_buffer = self._sock.recv(self.buffer_size)
            data = Protocol.parser(recv_buffer, NovaWhat.SEND_FILE_CONTENT_RSP)
        except TimeoutError as e:
            raise HostResponseTimeoutError(f'__send_file_content recv timeout {e}')
        except ProtocolParserError as e:
            raise ProtocolParserError(f'__send_file_content parser error {e}')
        except Exception:
            raise
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
        if self._sock is None:
            raise InvalidSocketError('__play_list_by_id sock is None')

        send_buffer = Protocol.play_list(play_id)

        try:
            self._sock.send(send_buffer)
            recv_buffer = self._sock.recv(self.buffer_size)
            data = Protocol.parser(recv_buffer, NovaWhat.PLAY_LIST_RSP)
        except TimeoutError as e:
            raise HostResponseTimeoutError(f'__play_list_by_id timeout {e}')
        except ProtocolParserError as e:
            raise ProtocolParserError(f'__play_list_by_id parser error {e}')
        except Exception:
            raise
        else:
            # 数据域内容： 执行结果1B
            if data != b'\x01':
                raise ResponseError('__play_list_by_id response error')

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
        try:
            # 发送文件名
            file_name = f'play{play_id:03d}.lst'
            self.__send_file_name(file_name)
            # 发送文件内容
            self.__send_file_content(content)
            # 指定播放
            self.__play_list_by_id(play_id)
        except InvalidSocketError as e:
            logger.error(f'{self.log_addr} {e}')
            return DeviceReturnCode.SOCKET_ERROR
        except HostResponseTimeoutError as e:
            logger.error(f'{self.log_addr} {e}')
            return DeviceReturnCode.HOST_RESPONSE_TIMEOUT
        except ProtocolParserError as e:
            logger.error(f'{self.log_addr} {e}')
            return DeviceReturnCode.PROTOCOL_PARSER_ERROR
        except ResponseError as e:
            logger.error(f'{self.log_addr} {e}')
            return DeviceReturnCode.HOST_RESPONSE_ERROR
        except Exception as e:
            logger.error(f'{self.log_addr} {e}')
            return DeviceReturnCode.UNKNOWN_ERROR

        return DeviceReturnCode.SUCCESS

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
            recv_buffer = self._sock.recv(self.buffer_size)
            data = Protocol.parser(recv_buffer, NovaWhat.GET_DEVICE_SIZE_RSP)
        except (TimeoutError, ProtocolParserError) as e:
            logger.error(f'{self.log_addr} {e}')
        else:
            width = Bytes16(data[:2]).reverse_bytes_to_int()
            height = Bytes16(data[2:4]).reverse_bytes_to_int()

            return width, height

        return None

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
            recv_buffer = self._sock.recv(self.buffer_size)
            data = Protocol.parser(recv_buffer, NovaWhat.GET_NOW_PLAY_CONTENT_RSP)
        except (TimeoutError, ProtocolParserError) as e:
            logger.error(f'{self.log_addr} {e}')
        else:
            current_item = data[1:]
            return current_item.decode('utf-8', 'ignore')

        return None

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
            recv_buffer = self._sock.recv(self.buffer_size * 2)
            data = Protocol.parser(recv_buffer, NovaWhat.GET_NOW_PLAY_ALL_CONTENT_RSP)
        except (TimeoutError, ProtocolParserError) as e:
            logger.error(f'{self.log_addr} {e}')
        else:
            current_all_item = data[1:]
            return current_all_item.decode('utf-8', 'ignore')

        return None


class NovaAsyncClient(VmsAsyncClient):
    """
    诺瓦异步通信客户端
    """

    async def get_now_play_all_content(self) -> str | None:
        pass

    async def set_now_brightness(self, brightness: int) -> int:
        pass

    async def get_now_brightness(self) -> str | None:
        pass

    async def get_now_play_content(self) -> str | None:
        pass

    def __init__(self, host: str = 'localhost', port: int = 5000):
        super().__init__(host, port)

    async def _send_file_name(self, file_name: str) -> None:
        """
        发送文件名

        e.g.
        发送
        AA FF FF 11 FF FF 70 6C 61 79 30 30 31 2E 6C 73 74 CC 5A 9B
        接受
        AA FF FF 12 01 CC A1 B4

        :raise HostResponseTimeoutError
        :raise ResponseError
        :param file_name:
        :return: None
        """
        func_name = 'send_file_name'
        send_buffer = Protocol.send_file_name(file_name)

        try:
            await self.send(send_buffer)
            recv_buffer = await self.recv()
            data = Protocol.parser(recv_buffer, NovaWhat.SEND_FILE_NAME_RSP)
        except asyncio.TimeoutError as e:
            raise HostResponseTimeoutError(f'{func_name} recv timeout {e}')
        except ProtocolParserError as e:
            raise ProtocolParserError(f'{func_name} parser error {e}')
        except Exception as e:
            raise
        else:
            # 数据域内容： 执行结果1B
            if data != b'\x01':
                raise ResponseError(f'{func_name} response error')

    async def _send_file_content(self, content: str) -> None:
        """
        发送文件内容

        e.g.
        发送
        略
        接受
        AA FF FF 14 01 00 01 CC 91 C4

        :raise HostResponseTimeoutError
        :raise ResponseError
        :param content:
        :return: None
        """
        func_name = 'send_file_content'
        send_buffer = Protocol.send_file_content(content)
        try:
            await self.send(send_buffer)
            recv_buffer = await self.recv()
            data_1 = Protocol.parser(recv_buffer, NovaWhat.SEND_FILE_CONTENT_RSP)
            # 文件发送完毕
            finished_rsp = await self.recv()
            data_2 = Protocol.parser(finished_rsp, NovaWhat.FILE_SEND_END_RSP)
        except asyncio.TimeoutError as e:
            raise HostResponseTimeoutError(f'{func_name} recv timeout {e}')
        except ProtocolParserError as e:
            raise ProtocolParserError(f'{func_name} parser error {e}')
        except Exception:
            raise
        else:
            # 数据域内容： 块号2B + 执行结果1B
            if data_1[2:] != b'\x01':
                raise ResponseError(f'{func_name} response error')
            if data_2 != b'\x01':
                raise ResponseError(f'{func_name} finished response error')

    async def _play_list_by_id(self, play_id: int) -> None:
        """
        指定播放

        e.g.
        发送
        AA FF FF 1B 01 CC BF 28
        接受
        AA FF FF 1C 01 CC BA A4

        :raise HostResponseTimeoutError
        :raise ResponseError
        :param play_id:
        :return: None
        """
        func_name = 'play_list_by_id'
        send_buffer = Protocol.play_list(play_id)

        try:
            await self.send(send_buffer)
            recv_buffer = await self.recv()
            data = Protocol.parser(recv_buffer, NovaWhat.PLAY_LIST_RSP)
        except asyncio.TimeoutError as e:
            raise HostResponseTimeoutError(f'{func_name} timeout {e}')
        except ProtocolParserError as e:
            raise ProtocolParserError(f'{func_name} parser error {e}')
        except Exception:
            raise
        else:
            # 数据域内容： 执行结果1B
            if data != b'\x01':
                raise ResponseError(f'{func_name} response error')

    async def set_play_list(self, content: str, play_id: int = 1) -> int:
        """
        组合指令，发送文件名，发送文件内容，指定播放

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
        :return: int 返回码
        """
        try:
            # 发送文件名
            file_name = f'play{play_id:03d}.lst'
            await self._send_file_name(file_name)
            # 发送文件内容
            await self._send_file_content(content)
            # 指定播放
            await self._play_list_by_id(play_id)
        except InvalidSocketError as e:
            logger.error(f'{self.log_addr} {e}')
            return DeviceReturnCode.SOCKET_ERROR
        except HostResponseTimeoutError as e:
            logger.error(f'{self.log_addr} {e}')
            return DeviceReturnCode.HOST_RESPONSE_TIMEOUT
        except ProtocolParserError as e:
            logger.error(f'{self.log_addr} {e}')
            return DeviceReturnCode.PROTOCOL_PARSER_ERROR
        except ResponseError as e:
            logger.error(f'{self.log_addr} {e}')
            return DeviceReturnCode.HOST_RESPONSE_ERROR
        except Exception as e:
            logger.error(f'{self.log_addr} {e}')
            return DeviceReturnCode.UNKNOWN_ERROR

        return DeviceReturnCode.SUCCESS
