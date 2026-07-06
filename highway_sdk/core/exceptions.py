"""Highway SDK 异常定义模块。

定义了 SDK 中使用的所有异常类，包括：
- 连接异常：连接失败、连接丢失、连接超时
- 协议异常：协议错误、响应超时
"""


class HighwaySDKError(Exception):
    """Highway SDK 异常基类。"""


# -----------------------------------------------------------------------------
# 连接异常
# 注意：不使用 ``ConnectionError`` 这个名字，因为它会遮蔽 Python 内建
# ``ConnectionError``（OSError 子类）。SDK 内部抛出的连接异常均继承
# ``DeviceConnectionError``，调用方 ``except DeviceConnectionError`` 时
# 不会意外吞掉 asyncio/socket 层抛出的内建 ConnectionError。
# -----------------------------------------------------------------------------
class DeviceConnectionError(HighwaySDKError):
    """设备连接异常基类。"""


class ConnectionLostError(DeviceConnectionError):
    """连接丢失异常。"""


class ConnectionTimeoutError(DeviceConnectionError):
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
# 注意：不使用 ``ValidationError`` 这个名字，避免与 pydantic.ValidationError
# 同名混淆。本组异常专指帧数据校验失败（CRC、解析、不支持）。
# -----------------------------------------------------------------------------
class FrameValidationError(HighwaySDKError, ValueError):
    """帧数据校验异常基类。"""


class CrcValidationError(FrameValidationError):
    """CRC 校验异常。"""


class ProtocolParsingError(FrameValidationError):
    """协议解析错误。"""


class ProtocolNotSupportedError(FrameValidationError):
    """协议不支持解析。"""


# -----------------------------------------------------------------------------
# 设备业务异常
# -----------------------------------------------------------------------------
class DeviceError(HighwaySDKError):
    """设备相关异常。"""


class DeviceOperationError(DeviceError):
    """设备操作异常。"""
