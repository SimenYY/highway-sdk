#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: novaAsyncClient.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/11/19 14:54
"""
from loguru import logger

from highway_sdk.core.client import AsyncClient
from highway_sdk.core.exceptions import (
    ResponseError,
    ProtocolParserError,
    HostResponseTimeoutError,
    InvalidSocketError
)
from .protocol import Protocol
from .utils.constants import (
    NovaWhat,
    NovaReturnCode
)


class NovaAsyncClient(AsyncClient):
    """
    诺瓦异步通信客户端
    """

    def __init__(self, host: str = 'localhost', port: int = 5000):
        super().__init__(host, port)

    async def __send_file_name(self, file_name: str) -> None:
        """
        发送文件名
        :raise HostResponseTimeoutError
        :raise ResponseError
        :param file_name:
        :return: None
        """
        send_buffer = Protocol.send_file_name(file_name)

        try:
            await self.send(send_buffer)
            recv_buffer = await self.recv()
            data = Protocol.parser(recv_buffer, NovaWhat.FILE_NAME_RSP)
        except IOError as e:
            raise IOError(f'__send_file_name recv IOError {e}')
        except ProtocolParserError as e:
            raise ProtocolParserError(f'__send_file_name parser error {e}')
        except Exception:
            raise
        else:
            # 数据域内容： 执行结果1B
            if data != b'\x01':
                raise ResponseError('__send_file_name response error')

    async def __send_file_content(self, content: str) -> None:
        """
        发送文件内容
        :raise HostResponseTimeoutError
        :raise ResponseError
        :param content:
        :return: None
        """
        send_buffer = Protocol.send_file_content(content)

        try:
            await self.send(send_buffer)
            recv_buffer = await self.recv()
            data = Protocol.parser(recv_buffer, NovaWhat.FILE_CONTENT_RSP)
        except IOError as e:
            raise IOError(f'__send_file_content recv IOError {e}')
        except ProtocolParserError as e:
            raise ProtocolParserError(f'__send_file_content parser error {e}')
        except Exception:
            raise
        else:
            # 数据域内容： 块号2B + 执行结果1B
            if data[2:] != b'\x01':
                raise ResponseError('__send_file_content response error')

    async def __play_list_by_id(self, play_id: int) -> None:
        """
        指定播放
        :raise HostResponseTimeoutError
        :raise ResponseError
        :param play_id:
        :return: None
        """

        send_buffer = Protocol.play_list(play_id)

        try:
            await self.send(send_buffer)
            recv_buffer = await self.recv()
            data = Protocol.parser(recv_buffer, NovaWhat.PLAY_LIST_RSP)
        except IOError as e:
            raise IOError(f'__play_list_by_id timeout {e}')
        except ProtocolParserError as e:
            raise ProtocolParserError(f'__play_list_by_id parser error {e}')
        except Exception:
            raise
        else:
            # 数据域内容： 执行结果1B
            if data != b'\x01':
                raise ResponseError('__play_list_by_id response error')

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
            await self.__send_file_name(file_name)
            # 发送文件内容
            await self.__send_file_content(content)
            # 指定播放
            await self.__play_list_by_id(play_id)
        except InvalidSocketError as e:
            logger.error(f'{self.log_addr} {e}')
            return NovaReturnCode.SOCKET_ERROR
        except HostResponseTimeoutError as e:
            logger.error(f'{self.log_addr} {e}')
            return NovaReturnCode.HOST_RESPONSE_TIMEOUT
        except ProtocolParserError as e:
            logger.error(f'{self.log_addr} {e}')
            return NovaReturnCode.PROTOCOL_PARSER_ERROR
        except ResponseError as e:
            logger.error(f'{self.log_addr} {e}')
            return NovaReturnCode.HOST_RESPONSE_ERROR
        except Exception as e:
            logger.error(f'{self.log_addr} {e}')
            return NovaReturnCode.UNKNOWN_ERROR

        return NovaReturnCode.SUCCESS
