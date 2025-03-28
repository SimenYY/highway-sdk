#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: xianKeClient.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2025/2/17 10:19
"""
import asyncio
from highway_sdk.core.log import logger
from highway_sdk.core.exceptions import ResponseError, HostResponseTimeoutError, ProtocolParserError
from highway_sdk.vms.base.vmsClient import VmsAsyncClient
from highway_sdk.vms.constants import DeviceReturnCode
from .protocol import ProtocolMessage, ProtocolParser
from .constants import XianKeResCode


class XianKeAsyncClient(VmsAsyncClient):

    def __init__(self,  host: str, port: int):
        super().__init__(host, port)

        self.pm = ProtocolMessage()

    async def set_play_list(self, content: str, play_id: int = 0) -> int:

        try:
            if not content:
                logger.error(f'{self.log_addr} content is empty')
                return DeviceReturnCode.INVALID_INPUT

            if play_id < 0 or play_id > 999:
                logger.error(f'{self.log_addr} play_id must be between 0 and 999')
                return DeviceReturnCode.INVALID_INPUT

            file_name = f'{play_id:03d}.xkl'
            file_type = 'list'

            # 上传文件
            await self._upload_file(content, file_type, file_name)
            # 显示播放列表
            await self._play_list(file_name)
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
            file_type: str = 'list',
            file_name: str = r'list\000.xkl'
    ) -> None:

        send_buffer = self.pm.upload_file(content, file_type, file_name)
        try:
            await self.send(send_buffer, log_prefix='upload_file')
            recv_buffer = await self.recv()
            pp = ProtocolParser(recv_buffer)
            data = pp.parse_packet().data
        except asyncio.TimeoutError as e:
            raise HostResponseTimeoutError(f"upload_file timed out: {e}")
        except ProtocolParserError as e:
            raise ProtocolParserError(f"upload_file parse error: {e}")
        else:
            if data != XianKeResCode.SUCCESS:
                raise ResponseError(f'upload_file response failed')

    async def _play_list(self, file_name: str = "000.xkl") -> None:

        send_buffer = self.pm.play_list(file_name)

        try:
            await self.send(send_buffer, log_prefix='play_list')
            recv_buffer = await self.recv()
            pp = ProtocolParser(recv_buffer)
            data = pp.parse_packet().data
        except asyncio.TimeoutError as e:
            raise HostResponseTimeoutError(f"play_list timed out: {e}")
        except ProtocolParserError as e:
            raise ProtocolParserError(f"play_list parse error: {e}")
        else:
            if data != XianKeResCode.SUCCESS:
                raise ResponseError(f'play_list response failed')

    async def get_now_play_content(self) -> str | None:
        pass

    async def get_now_play_all_content(self) -> str | None:
        pass

    async def set_now_brightness(self, brightness: int) -> int:
        pass

    async def get_now_brightness(self) -> str | None:
        pass
