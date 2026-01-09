#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: exceptions.py
:Project:
:Brand:
:Version:
:Description: HighwaySDK 异常定义
:Author: He YinYu
:Link:
:Time: 2024/8/8 11:22
"""


class HighwaySDKException(Exception):
    """HighwaySDK异常基类"""


# -----------------------------------------------------------------------------
# 网络通信异常
# -----------------------------------------------------------------------------
class NetworkError(HighwaySDKException, OSError):
    """网络通信相关异常基类"""


class SDKConnectionError(NetworkError):
    """连接相关异常"""


class ConnectionFailError(SDKConnectionError):
    """连接失败异常"""


class ConnectionLostError(SDKConnectionError):
    """连接丢失异常"""


class TransmissionError(NetworkError):
    """数据传输异常"""


class ResponseError(TransmissionError):
    """响应异常"""


class HostResponseTimeoutError(ResponseError):
    """主机响应超时"""


class HostResponseIncompleteError(ResponseError):
    """主机响应不完整"""


# -----------------------------------------------------------------------------
# 数据校验异常
# -----------------------------------------------------------------------------
class ValidationError(HighwaySDKException, ValueError):
    """数据校验相关异常基类"""


class CrcValidationError(ValidationError):
    """CRC校验异常"""


class ProtocolParsingError(ValidationError):
    """协议解析错误"""


class ProtocolNotSupportedError(ValidationError):
    """协议不支持解析"""


# -----------------------------------------------------------------------------
# 设备业务异常
# -----------------------------------------------------------------------------
class DeviceError(HighwaySDKException):
    """设备相关异常"""


class DeviceOperationError(DeviceError):
    """设备操作异常"""


# -----------------------------------------------------------------------------
# 系统资源异常
# -----------------------------------------------------------------------------
class ResourceError(HighwaySDKException):
    """系统资源相关异常"""


class InvalidSocketError(ResourceError):
    """无效的socket"""
