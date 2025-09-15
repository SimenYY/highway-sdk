#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: vmsClient.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/11/21 11:05
"""
from highway_sdk.core.client import Client, AsyncClient
from abc import abstractmethod


class VmsClient(Client):
    @abstractmethod
    def set_play_list(self, content: str, play_id: int = 1) -> int:
        """组合指令，发送文件名，发送文件内容，指定播放

        返回码参考：
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
    @abstractmethod
    def get_now_play_content(self) -> str | None:
        """获取当前播放内容

        :return: 当前item内容 or None
        """

    @abstractmethod
    def get_now_play_all_content(self) -> str | None:
        """获取当前播放全部内容

        :return: 当前播放全部内容 or None
        """

    @abstractmethod
    def set_now_brightness(self, brightness: int) -> int:
        """设置当前亮度

        :param brightness:
        :return:
        """

    @abstractmethod
    def get_now_brightness(self) -> str | None:
        """获取当前亮度

        :return:
        """


class VmsAsyncClient(AsyncClient):
    @abstractmethod
    async def set_play_list(self, content: str, play_id: int = 1) -> int:
        """组合指令，发送文件名，发送文件内容，指定播放

        返回码参考：
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

    @abstractmethod
    async def get_now_play_content(self) -> str | None:
        """获取当前播放内容

        :return: 当前item内容 or None
        """

    @abstractmethod
    async def get_now_play_all_content(self) -> str | None:
        """获取当前播放全部内容

        :return: 当前播放全部内容 or None
        """

    @abstractmethod
    async def set_now_brightness(self, brightness: int) -> int:
        """设置当前亮度

        :param brightness:
        :return:
        """

    @abstractmethod
    async def get_now_brightness(self) -> str | None:
        """获取当前亮度

        :return:
        """
