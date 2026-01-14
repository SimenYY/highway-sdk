from highway_sdk.core.exceptions import HighwaySDKException

__all__ = [
    "SupaiotAPIError",
    "SupaiotAPILoginError",
    "SupaiotAPIResponseValidateError",
    "SupaiotAPIconnectError",
    "SupaiotError",
]


class SupaiotError(HighwaySDKException):
    """物联智控异常"""


class SupaiotAPIError(SupaiotError):
    """API异常"""


class SupaiotAPIconnectError(SupaiotAPIError):
    """连接异常"""


class SupaiotAPIResponseValidateError(SupaiotAPIError):
    """响应数据验证异常"""


class SupaiotAPILoginError(SupaiotAPIError):
    """登录异常"""
