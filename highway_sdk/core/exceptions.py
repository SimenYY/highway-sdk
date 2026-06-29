"""Highway SDK 异常定义模块。

定义了 SDK 中使用的所有异常类，包括：
- 连接异常：连接失败、连接丢失、连接超时
- 协议异常：协议错误、响应超时
"""


class HighwaySDKError(Exception):
    """Highway SDK 异常基类。"""


# -----------------------------------------------------------------------------
# 连接异常
# -----------------------------------------------------------------------------
class ConnectionError(HighwaySDKError):
    """连接异常基类。"""


class ConnectionLostError(ConnectionError):
    """连接丢失异常。"""


class ConnectionTimeoutError(ConnectionError):
    """连接超时异常。"""


# -----------------------------------------------------------------------------
# 协议异常
# -----------------------------------------------------------------------------
class ProtocolError(HighwaySDKError):
    """协议异常基类。"""


class ResponseTimeoutError(ProtocolError):
    """响应超时异常。"""


# -----------------------------------------------------------------------------
# 数据校验异常
# -----------------------------------------------------------------------------
class ValidationError(HighwaySDKError, ValueError):
    """数据校验相关异常基类。"""


class CrcValidationError(ValidationError):
    """CRC 校验异常。"""


class ProtocolParsingError(ValidationError):
    """协议解析错误。"""


class ProtocolNotSupportedError(ValidationError):
    """协议不支持解析。"""


# -----------------------------------------------------------------------------
# 设备业务异常
# -----------------------------------------------------------------------------
class DeviceError(HighwaySDKError):
    """设备相关异常。"""


class DeviceOperationError(DeviceError):
    """设备操作异常。"""
