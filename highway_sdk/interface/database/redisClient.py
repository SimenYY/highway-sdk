#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: redisClient.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2025/3/25 10:47
"""
import threading
import time
from typing import Any

import redis
from highway_sdk.core.log import logger
from contextlib import suppress

redis_client = redis.Redis()


class RedisClient:
    factor: float = 1.6180339887498948
    default_delay: float = 1.0
    def __init__(
            self,
            host: str = "localhost",
            port: int = 6379,
            db: int = 0,
            max_retries: int = None,
            max_delay: float = 3600.0,
            **kwargs
    ):
        self.host: str = host
        self.port: int = port
        self.db: int = db
        self.kwargs: dict = kwargs

        self.client: redis.Redis | None = None

        self.connected: bool = False
        self.retries: int = 0
        self.delay: float = 1.0

        self.max_retries: int = max_retries
        self.max_delay: float = max_delay

        self._thread: threading.Thread | None = None
        self._thread_terminate: bool = False

    def connect(self) -> None:
        self.client = redis.Redis(host=self.host, port=self.port, db=self.db)
        try:
            if self.client.ping():
                logger.info(f"Redis({self.host}:{self.port}) connected.")
                self.connected = True
            else:
                logger.error(f"Redis({self.host}:{self.port}) connection error unexpected.")
                self.connected = False
        except redis.exceptions.ConnectionError as e:
            logger.error(f"Redis({self.host}:{self.port}) connection failed.")
            self.connected = False

    def is_connected(self) -> bool:
        """检查连接状态
        
        :return: 
        """

        connected = False

        if self.client is not None:
            with suppress(redis.exceptions.ConnectionError):
                if self.client.ping():
                    connected = True

        self.connected = connected

        return connected

    def block_start(self):
        """阻塞启动

        :return:
        """

        self.connect()

        loop = True

        while loop:

            if self._thread_terminate:
                break

            if self.is_connected():
                pass
            else:
                continue_trying = True
                self.reset_delay()
                while continue_trying:
                    # 重置延时
                    self.reconnect()

                    if not self.connected:
                        time.sleep(self.delay)
                    else:
                        continue_trying = False

    def reset_delay(self):

        self.delay = self.default_delay

    def _thread_main(self):
        try:
            self.block_start()
        finally:
            self._thread = True

    def noblock_start(self):
        """非阻塞启动

        :return:
        """

        if self._thread is not None:
            return

        self._thread_terminate = False
        self._thread = threading.Thread(target=self._thread_main)
        self._thread.daemon = True
        self._thread.start()

    def reconnect(self) -> None:
        """重连函数

        :return:
        """

        self.retries += 1
        if self.max_retries is not None and self.retries > self.max_retries:
            logger.warning(f"Abandoning  Redis({self.host}:{self.port}) after {self.retries} retries.")
            return

        self.delay = round(min(self.delay * self.factor, self.max_delay), 2)
        logger.debug(f"Redis({self.host}:{self.port}) will retry in {self.delay} seconds.")

        self.connect()

    def set(self, name: Any, value: Any, **kwargs) -> None:
        """设置键值

        :param name:
        :param value:
        :param kwargs:
        :return:
        """
        if self.connected:
            self.client.set(name, value, **kwargs)
        else:
            logger.error(f"Redis({self.host}:{self.port}) set failed, connection error")