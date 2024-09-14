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


class _Log(BaseModel):
    name: str = None
    brand: str = None
    level: str = None
    rotation: str = None
    retention: str = None
    compression: str = None
    enqueue: bool = None
    file: bool = None
    console: bool = None

    class Config:
        extra = 'forbid'


class _Comm(BaseModel):
    polling_interval: int = None

    class Config:
        extra = 'forbid'


class _Address(BaseModel):
    port: int
    ip_list: List[str]

    class Config:
        extra = 'forbid'


class DriverConfigModel(BaseModel):
    log: Optional[_Log] = None
    protocol: Optional[_Comm] = None
    address: _Address

    class Config:
        extra = 'forbid'


def load_config_model(config_model: Type[BaseModel], file_path: str) -> BaseModel | None:
    try:
        with open(file_path, 'r') as f:
            config = json.load(f)
            model = config_model(**config)
    except Exception as e:
        logger.error(f'{e.__class__.__name__}: {e}')
        return None
    else:
        return model
