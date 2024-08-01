#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: logging_ex.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/8/1 16:32
:Department: 公路机电工程技术中心
:Copyright: ©1993-2023 浙江中控信息产业股份有限公司
"""
import logging
import sys
from copy import copy
from typing import Literal

import click


class ColourizedFormatter(logging.Formatter):
    level_name_colors = {
        logging.DEBUG: lambda level_name: click.style(str(level_name), fg="cyan"),
        logging.INFO: lambda level_name: click.style(str(level_name), fg="green"),
        logging.WARNING: lambda level_name: click.style(str(level_name), fg="yellow"),
        logging.ERROR: lambda level_name: click.style(str(level_name), fg="red"),
        logging.CRITICAL: lambda level_name: click.style(
            str(level_name), fg="bright_red"
        ),
    }

    def __init__(
            self,
            fmt: str | None = None,
            datefmt: str | None = None,
            style: Literal["%", "{", "$"] = "%",
            use_colors: bool | None = None,
    ):
        if use_colors in (True, False):
            self.use_colors = use_colors
        else:
            self.use_colors = self.should_use_colors()
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def color_level_name(self, level_name: str, level_no: int) -> str:
        def default(_level_name: str) -> str:
            return str(_level_name)  # pragma: no cover

        func = self.level_name_colors.get(level_no, default)
        return func(level_name)

    def format(self, record):
        """
        重写此函数，具体影响格式

        :param record:
        :return:
        """
        record_copy = copy(record)
        level_name = record_copy.levelname
        level_no = record_copy.levelno
        seperator = " " * (8 - len(level_name))
        if self.use_colors:
            level_name = self.color_level_name(level_name, level_no)
        record_copy.__dict__['level_prefix'] = level_name + ':' + seperator
        return super().format(record_copy)

    def should_use_colors(self) -> bool:
        return True  # pragma: no cover


class DefaultFormatter(ColourizedFormatter):
    def should_use_colors(self) -> bool:
        return sys.stderr.isatty()  # pragma: no cover
