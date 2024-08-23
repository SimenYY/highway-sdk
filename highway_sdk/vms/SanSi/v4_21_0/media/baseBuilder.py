#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: baseBuilder.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/8/12 15:19
"""

from abc import ABC, abstractmethod


class BaseBuilder(ABC):

    def to_dict(self):
        modify_dict = {}
        for k, v in self.__dict__.items():
            if k.startswith('_'):
                modify_dict[k[1:]] = v
            elif k.startswith('__'):
                modify_dict[k[2:]] = v
            else:
                modify_dict[k] = v
        return modify_dict

    @abstractmethod
    def build(self):
        pass
