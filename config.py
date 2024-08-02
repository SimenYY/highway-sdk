#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging.config
from typing import Any

LOGGING_CONFIG: dict[str, Any] = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            '()': 'logging_ex.DefaultFormatter',
            'fmt': '%(asctime)s - %(name)s - %(level_prefix)s %(module)s - %(funcName)s - %(lineno)d - %(message)s',
            'use_colors': None
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
        'highway_sdk': {
            'handlers': ['console', 'error_file'],
            'propagate': False
        }
    }
}

logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger('highway_sdk')


def get_logger():
    return logger
