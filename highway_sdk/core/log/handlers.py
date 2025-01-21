#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: handlers.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/12/2 17:01
"""
import datetime
import inspect
import logging
import os
import socket
import sys
import time
from collections import OrderedDict
from queue import Queue
from threading import Thread
from typing import Literal

import requests

from loguru import logger
from requests.auth import HTTPBasicAuth


# 将logging 转发到 loguru
class InterceptHandler(logging.Handler):
    """
    使用：logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
    """

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class ColoredStreamHandler(logging.StreamHandler):
    def __init__(self):
        super().__init__()

        from colorlog import ColoredFormatter

        self.setFormatter(ColoredFormatter(
            "%(green)s%(asctime)s.%(msecs)03d"
            "%(red)s | "
            "%(log_color)s%(levelname)-8s"
            "%(red)s | "
            "%(cyan)s%(name)s"
            "%(red)s:"
            "%(cyan)s%(module)s"
            "%(red)s:"
            "%(cyan)s%(funcName)s"
            "%(red)s:"
            "%(cyan)s%(lineno)d"
            "%(red)s - "
            "%(log_color)s%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            reset=True,
            log_colors={
                'DEBUG': 'blue',
                'INFO': 'white',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'white,bg_red',
            },
            style='%'
        ))


class HttpHandler(logging.Handler):
    def __init__(
            self,
            host: str,
            url: str,
            method: Literal['POST', 'GET'] = "POST",
            secure: bool = False,
            credentials: tuple | list = None
    ):
        super().__init__()
        method = method.upper()
        if method not in ['POST', 'GET']:
            raise ValueError("method must be POST or GET")

        self.host = host
        self.url = url
        self.method = method
        self.secure = secure
        self.credentials = credentials
        self.session = requests.Session()

    def map_log_Record(self, record):

        record.__dict__.update(
            hostname=socket.gethostname(),
        )
        return record.__dict__

    @property
    def full_url(self) -> str:
        """
        Get an HTTP[S] URL using requests.
        """
        if self.secure:
            url = f"https://{self.host}{self.url}"
        else:
            url = f"http://{self.host}{self.url}"
        return url

    def _send_req(self, record):
        try:
            url = self.full_url
            data = self.map_log_Record(record)
            auth = None

            if self.credentials:
                auth = HTTPBasicAuth(*self.credentials)
            match self.method:
                case "GET":
                    self.session.get(url, params=data, auth=auth)
                case "POST":
                    self.session.post(url, json=data, auth=auth)
                case _:
                    raise ValueError(f"Unsupported method: {self.method}")

        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)

    def emit(self, record):
        self._send_req(record)


class MongoHandler(logging.Handler):
    pass


class KafkaHandler(logging.Handler):
    pass


class ElasticHandler(logging.Handler):
    ES_INTERVAL_SECONDS = 0.5
    host_name = socket.gethostname()
    host_process = f'{host_name} -- {os.getpid()}'

    script_name = sys.argv[0]

    task_queue = Queue()

    last_es_op_time = time.time()
    has_start_do_bulk_op = False

    def __init__(self, elastic_hosts: list, elastic_port: int, index_prefix='pylog-'):
        """

        :param elastic_hosts:
        :param elastic_port:
        :param index_prefix:
        """
        super().__init__()

        from elasticsearch import Elasticsearch, helpers

        self._helpers = helpers
        self._es_client = Elasticsearch(elastic_hosts, )
        self._index_prefix = index_prefix
        t = Thread(target=self._do_bulk_op)
        t.daemon = True
        t.start()

    @classmethod
    def __add_task_to_bulk(cls, task):
        cls.task_queue.put(task)

    @classmethod
    def __clear_bulk_task(cls):
        cls.task_queue.queue.clear()

    def _do_bulk_op(self):
        if self.__class__.has_start_do_bulk_op:
            return
        self.__class__.has_start_do_bulk_op = True
        while True:
            try:
                if self.__class__.task_queue.qsize() > 10000:
                    self.__clear_bulk_task()
                    return
                tasks = list(self.__class__.task_queue.queue)
                self.__clear_bulk_task()
                self._helpers.bulk(self._es_client, tasks)
                self.__class__.last_es_op_time = time.time()
            except Exception:
                raise
            finally:
                time.sleep(self.ES_INTERVAL_SECONDS)

    def emit(self, record):
        try:
            log_info_dict = OrderedDict()
            log_info_dict['@timestamp'] = datetime.datetime.utcfromtimestamp(record.created).isoformat()
            log_info_dict['time'] = time.strftime('%Y-%m-%d %H:%M:%S')
            log_info_dict['name'] = record.name
            log_info_dict['host'] = self.host_name
            log_info_dict['host_process'] = self.host_process
            log_info_dict['file_path'] = record.pathname
            log_info_dict['file_name'] = record.filename
            log_info_dict['func_name'] = record.funcName
            log_info_dict['line_no'] = record.lineno
            log_info_dict['log_level'] = record.levelname
            log_info_dict['msg'] = record.getMessage()
            log_info_dict['script'] = self.script_name
            self.__add_task_to_bulk({
                "_index": f"{self._index_prefix}{record.name.lower()}",
                # "_type": f'_doc',    # es7 服务端之后不支持_type设置
                "_source": log_info_dict
            })
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)
