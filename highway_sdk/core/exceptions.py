#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: exceptions.py
:Project:
:Brand:
:Version:
:Description:
:Author: He YinYu
:Link:
:Time: 2024/8/8 11:22
"""


class HighwaySDKException(Exception):
    """HighwaySDK异常基类"""

#-----------------------------------------------------------------------------
# 校验异常
#-----------------------------------------------------------------------------
class ValidationError(HighwaySDKException, ValueError):
    """数据校验引发的异常信息"""


class CrcValidationError(ValidationError):
    """crc校验异常"""


#-----------------------------------------------------------------------------
# 主机响应异常
#-----------------------------------------------------------------------------

class ResponseError(HighwaySDKException, OSError):
    """响应异常"""

class HostResponseTimeoutError(ResponseError):
    """主机响应超时"""

class HostResponseIncompleteError(ResponseError):
    """主机响应不完整"""


#-----------------------------------------------------------------------------
# 协议解析异常
#-----------------------------------------------------------------------------    
class ProtocolParserError(HighwaySDKException, ValueError):
    """协议解析异常"""

#-----------------------------------------------------------------------------
# 套接字错误
#-----------------------------------------------------------------------------

class InvalidSocketError(HighwaySDKException):
    """无效的socket"""
