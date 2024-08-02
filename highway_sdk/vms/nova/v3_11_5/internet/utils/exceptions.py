#!/usr/bin/env python
# -*- coding: utf-8 -*-



class NovaException(Exception):
    def __init__(self, msg: str = 'nova通信异常'):
        self.msg = msg

    def __str__(self):
        return self.msg



class NovaFileNameError(NovaException):
    def __init__(self, msg: str = 'nova 文件名发送错误'):
        super().__init__(msg)


class NovaFileContentError(NovaException):
    def __init__(self, msg: str = 'nova 文件内容发送错误'):
        super().__init__(msg)


class NovaPlayListError(NovaException):
    def __init__(self, msg: str = 'nova 指定播放列表错误'):
        super().__init__(msg)