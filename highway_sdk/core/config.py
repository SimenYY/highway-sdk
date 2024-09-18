#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: settings.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/9/14 9:47
"""
import json
from typing import List, Optional, Type

from pydantic import BaseModel

from .logx import logger


class ExtraForbidModel(BaseModel):
    class Config:
        extra = 'forbid'


class _Log(ExtraForbidModel):
    name: str = None
    brand: str = None
    level: str = None
    rotation: str = None
    retention: str = None
    compression: str = None
    enqueue: bool = None
    file: bool = None
    console: bool = None


class _Comm(ExtraForbidModel):
    polling_interval: int = None


class _Address(ExtraForbidModel):
    port: int
    ip_list: List[str]


class DriverConfigModel(ExtraForbidModel):
    log: Optional[_Log] = None
    comm: Optional[_Comm] = None
    address: _Address

    @classmethod
    def load(cls, file_path: str) -> 'DriverConfigModel':
        try:
            with open(file_path, 'r') as f:
                config = json.load(f)
                model = cls(**config)
        except Exception:
            raise
        else:
            return model
