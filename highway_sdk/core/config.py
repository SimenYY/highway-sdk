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
from typing import List

from pydantic import BaseModel


class ExtraForbidModel(BaseModel):
    class Config:
        extra = 'forbid'


class _Log(ExtraForbidModel):
    name: str = 'unknown'
    brand: str = 'unknown'
    level: str = 'ERROR'
    rotation: str = '1 day'
    retention: str = '7 days'
    compression: str = 'zip'
    enqueue: bool = True
    file: bool = True
    console: bool = False


class _Comm(ExtraForbidModel):
    polling_interval: int = 5


class _Address(ExtraForbidModel):
    port: int = 28888
    ip_list: List[str] = ['127.0.0.1']


class DriverConfigModel(ExtraForbidModel):
    """
    示例
    {
      'log': {
        'name': 'unknown',
        'brand': 'unknown',
        'level': 'ERROR',
        'rotation': '1 day',
        'retention': '7 days',
        'compression': 'zip',
        'enqueue': True,
        'file': True,
        'console': False
      },
      'comm': {
        'polling_interval': 5
      },
      'address': {
        'port': 28888,
        'ip_list': [
          '127.0.0.1'
        ]
      }
    }

    """
    log: _Log = _Log()
    comm: _Comm = _Comm()
    address: _Address = _Address()

    @classmethod
    def load(cls, file_path: str) -> 'DriverConfigModel':
        if not file_path.endswith('.json'):
            raise Exception('配置文件必须是配置文件类型')

        try:
            with open(file_path, 'r') as f:
                config = json.load(f)
                return cls(**config)
        except FileNotFoundError:
            with open(file_path, 'w') as f:
                default = cls()
                json.dump(default.dict(), f, indent=4)
            raise FileNotFoundError(f'{file_path} 不存在，已创建默认配置文件！')
        except Exception:
            raise
