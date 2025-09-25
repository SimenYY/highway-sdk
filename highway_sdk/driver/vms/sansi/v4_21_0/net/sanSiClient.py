#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: sansiClient.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:s
:Time: 2024/8/8 10:52
"""
import asyncio
from deprecated import deprecated
from highway_sdk.vms.base.vmsClient import VmsClient, VmsAsyncClient
from highway_sdk.core.exceptions import (HostResponseTimeoutError,
                                         ProtocolParserError,
                                         ResponseError,
                                         InvalidSocketError)
from .protocol import Protocol, ProtocolMessage, ProtocolParser
from highway_sdk.vms.constants import DeviceReturnCode
from highway_sdk.core._log import logger
from .constants import SanSiResCode


@deprecated(
    reason="Used SanSiAsyncClient instead",
    version="1.26.0"
)
class SanSiClient(VmsClient):

    def get_now_play_all_content(self) -> str | None:
        pass

    def set_now_brightness(self, brightness: int) -> int:
        pass

    def get_now_brightness(self) -> str | None:
        pass

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
        else:
            return DeviceReturnCode.SUCCESS

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


class SanSiAsyncClient(VmsAsyncClient):

    def __init__(self, host: str, port: int):
        super().__init__(host, port)

        self.pm = ProtocolMessage()

    async def get_now_play_content(self) -> str | None:
        pass

    async def get_now_play_all_content(self) -> str | None:
        pass

    async def set_now_brightness(self, brightness: int) -> int:
        pass

    async def get_now_brightness(self) -> str | None:
        pass

    async def set_play_list(self, content: str, play_id: int = 1) -> int:
        try:
            if not content:
                logger.error(f'{self.log_addr} content is empty')
                return DeviceReturnCode.INVALID_INPUT

            if play_id < 0 or play_id > 999:
                logger.error(f'{self.log_addr} play_id must be between 0 and 999')
                return DeviceReturnCode.INVALID_INPUT

            file_name = 'play.lst'
            # 直接更改当前播放表
            await self._upload_file(content, file_name)
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

    async def _upload_file(
            self,
            content: str,
            file_name: str = "play.lst"
    ) -> None:
        """
        文件名为 "play.lst"，是更改可变信息标志的当前播放表；

        :param content:
        :param file_name:
        :return:
        """
        send_buffer = self.pm.upload_file(content, file_name)
        try:
            await self.send(send_buffer, log_prefix="upload_file")
            recv_buffer = await self.recv()
            pp = ProtocolParser(recv_buffer)
            data = pp.parse_packet().data
        except asyncio.TimeoutError as e:
            raise HostResponseTimeoutError(f"upload_file timed out: {e}")
        except ProtocolParserError as e:
            raise ProtocolParserError(f"upload_file parse error: {e}")
        else:
            if data[:1] != SanSiResCode.SUCCESS:
                error_msg = data[1:].decode(self.pm.config.encoding, 'ignore')
                raise ResponseError(error_msg)
