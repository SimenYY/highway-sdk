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
from typing import List

from pydantic import BaseModel, ValidationError


class ConfigModel(BaseModel):
    class Config:
        extra = 'forbid'


class _Log(ConfigModel):
    name: str = 'unknown'
    brand: str = 'unknown'
    level: str = 'ERROR'
    rotation: str = '1 day'
    retention: str = '7 days'
    compression: str = 'zip'
    enqueue: bool = True
    file: bool = True
    console: bool = False


class _Comm(ConfigModel):
    polling_interval: int = 5


class _Address(ConfigModel):
    port: int = 28888
    ip_list: List[str] = ['127.0.0.1']


class DriverConfigModel(ConfigModel):
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
    def load(
            cls, json_file_path: str,
            validate: bool = True
    ) -> 'DriverConfigModel':
        """
        如果需要加载额外字段，需要重新定义config

        :param json_file_path:
        :param validate:
        :return:
        """
        if not json_file_path.endswith('.json'):
            raise Exception('配置文件必须是配置文件类型')
        try:
            with open(json_file_path, 'r') as f:
                if validate:
                    return cls.model_validate_json(f.read())
                else:
                    import json
                    return cls.model_construct(json.load(f))
        except FileNotFoundError:
            with open(json_file_path, 'w') as f:
                import json
                default = cls()
                json.dump(default.dict(), f, indent=4)
            raise FileNotFoundError(f'{json_file_path} 不存在，已创建默认配置文件！')
        except ValidationError:
            raise
        except Exception:
            raise
