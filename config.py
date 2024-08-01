#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: config.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/8/1 15:34
:Department: 公路机电工程技术中心
:Copyright: ©1993-2023 浙江中控信息产业股份有限公司
"""
import logging_ex.config
from pathlib import Path
from typing import Any

LOGGING_CONFIG: dict[str, Any] = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            '()': 'supcon_highway_sdk.logging.DefaultFormatter',
            'fmt': '%(asctime)s - %(name)s - %(level_prefix)s %(module)s - %(funcName)s - %(lineno)d - %(message)s',
            'use_colors': True
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'level': 'DEBUG',
            'stream': 'ext://sys.stderr'
        },
        'file': {
            'class': 'logging.FileHandler',
            'formatter': 'default',
            'filename': 'supcon_highway_sdk.log',
            'encoding': 'utf-8'
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'level': 'ERROR',
            'filename': 'sdk_errors.log',
            'encoding': 'utf-8',
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 20
        }
    },
    'loggers': {
        # 'nova': {
        #     'handlers': ['console'],
        #     'level': 'INFO',
        #     'propagate': False,
        # },
        'supcon_highway_sdk': {
            'handlers': ['console', 'error_file'],
            'propagate': False
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger('supcon_highway_sdk')


def get_logger():
    return logger
