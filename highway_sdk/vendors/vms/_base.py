"""VMS厂商基础模块。

该模块提供了VMS（可变情报板）厂商SDK的基础类和接口，包括：
- BaseBuilder: 建造者模式协议接口
- BaseFrame: 帧数据基类
- BaseParser: 解析器基类，提供通用的解析功能
"""

from collections.abc import Callable
from functools import lru_cache, wraps
from typing import Any, Protocol, Self

from pydantic import BaseModel, Field, field_validator

from highway_sdk.core.base import BaseTags
from highway_sdk.core.constants import STX
from highway_sdk.core.exceptions import (
    DeviceOperationError,
    ProtocolNotSupportedError,
    ProtocolParsingError,
)


class BaseBuilder(Protocol):
    """建造者模式协议接口。

    定义了建造者类必须实现的方法，用于构建对象。
    """

    def build(self) -> Any:
        """构建并返回对象。

        Returns:
            Any: 构建完成的对象。
        """
        ...


class BaseFrame(BaseModel):
    """帧数据基类。

    定义了VMS通信帧的基本结构，包括起始符和结束符。
    所有厂商的帧类都应该继承此类。

    Attributes:
        start: 帧起始符，默认为STX（0x02）。
        end: 帧结束符，默认为ETX（0x03）。
    """

    start: bytes = Field(default=b"\x02", frozen=True, description="帧起始符")
    end: bytes = Field(default=b"\x03", frozen=True, description="帧结束符")

    @field_validator("start")
    @classmethod
    def ensure_start(cls, v: Any):
        """验证起始符是否为STX。

        Args:
            v: 起始符值。

        Returns:
            bytes: 验证通过的起始符。

        Raises:
            ValueError: 如果起始符不是STX。
        """
        if v != STX:
            raise ValueError("start must be STX")
        return v

    @field_validator("end")
    @classmethod
    def ensure_end(cls, v: Any):
        """验证结束符是否为ETX。

        Args:
            v: 结束符值。

        Returns:
            bytes: 验证通过的结束符。

        Raises:
            ValueError: 如果结束符不是ETX。
        """
        if v != cls.end:
            raise ValueError("end must be ETX")
        return v

    @classmethod
    def from_bytes(cls, message: bytes) -> Self:
        """从字节数据创建帧对象。

        Args:
            message: 帧数据的字节表示。

        Returns:
            Self: 解析后的帧对象。
        """
        ...

    def __bytes__(self) -> bytes:
        """将帧对象转换为字节数据。

        Returns:
            bytes: 帧的字节表示。
        """
        ...


class BaseParser:
    """基础解析器类，提供所有厂商共有的解析功能。

    该类实现了通用的解析逻辑，包括：
    - 解析器注册机制
    - 帧数据解析
    - 返回结果校验

    用法:
        1. 继承此类创建厂商特定的解析器
        2. 使用 @register(what) 装饰器注册解析函数
        3. 实现厂商特定的解析方法

    Example:
        >>> class MyParser(BaseParser):
        ...     @classmethod
        ...     @MyParser.register(What.GET_ITEM)
        ...     def _parse_get_item(data: bytes):
        ...         return ItemTags(text=data.decode())
    """

    _parsers: dict[Any, Callable[..., BaseTags]] = {}

    @classmethod
    @lru_cache
    def parse(cls, frame):
        """解析帧数据。

        根据帧的what类型查找对应的解析函数并执行解析。

        Args:
            frame: 帧对象，包含 what 和 data 属性。

        Returns:
            BaseTags: 解析后的标签对象。

        Raises:
            ProtocolNotSupportedError: 不支持的指令类型。
            ProtocolParsingError: 解析失败。
            DeviceOperationError: 设备操作失败。
        """
        try:
            return cls._parsers[frame.what](frame.data)
        except KeyError as e:
            raise ProtocolNotSupportedError(f"Unsupported what: {e}")
        except DeviceOperationError:
            raise
        except Exception as e:
            raise ProtocolParsingError(f"Failed to parse frame: {e}")

    @classmethod
    def register(cls, what):
        """注册解析函数的装饰器。

        使用该装饰器将解析函数注册到指定指令类型。

        Args:
            what: 指令类型枚举值。

        Returns:
            Callable: 装饰器函数。

        Example:
            >>> @Parser.register(What.GET_ITEM)
            ... def _parse_get_item(data: bytes):
            ...     return ItemTags(text=data.decode())
        """

        def decorate(func):
            cls._parsers[what] = func

            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorate

    @classmethod
    def _is_ok(cls, data: bytes, success_value: bytes):
        """检查返回是否成功。

        通过检查返回数据是否以成功值开头来判断操作是否成功。

        Args:
            data: 返回的数据。
            success_value: 成功的标识值。

        Returns:
            bool: 是否成功。
        """
        return data.startswith(success_value)
