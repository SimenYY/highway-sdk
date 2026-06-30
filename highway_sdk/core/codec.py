"""编解码器基类模块。

定义了帧数据编解码的统一接口，合并了原有的 Parser 和 Builder 职责。
"""

from collections.abc import Callable
from typing import Any, ClassVar

from .frame import BaseFrame
from .tags import BaseTags


class BaseCodec:
    """编解码器基类。

    提供统一的编解码接口，使用装饰器注册机制管理不同指令的编解码函数。

    设计原则：
        - 编码（encode）：参数 → 帧
        - 解码（decode）：帧 → 数据标签
        - 通过装饰器注册具体的编解码实现

    Example:
        >>> class MyCodec(BaseCodec):
        ...     @classmethod
        ...     @MyCodec.register(b"\\x01")
        ...     def decode_get_item(cls, data: bytes) -> BaseTags:
        ...         return ItemTags(text=data.decode())
    """

    _decoders: ClassVar[dict[Any, Callable[..., BaseTags]]] = {}

    @classmethod
    def decode(cls, frame: BaseFrame) -> BaseTags:
        """解码：帧 → 数据标签。

        根据帧的指令类型查找对应的解码函数并执行。

        Args:
            frame: 待解码的帧对象。

        Returns:
            BaseTags: 解码后的数据标签。

        Raises:
            ValueError: 不支持的指令类型。
        """
        try:
            return cls._decoders[frame.what](cls, frame.data)
        except KeyError as e:
            raise ValueError(f"Unsupported command: {e}") from e

    @classmethod
    def register(cls, what: Any):
        """注册解码函数的装饰器。

        Args:
            what: 指令标识。

        Returns:
            Callable: 装饰器函数。
        """

        def decorator(func: Callable[..., BaseTags]) -> Callable[..., BaseTags]:
            # 确保注册到调用类自身的 _decoders，而非父类
            if "_decoders" not in cls.__dict__:
                cls._decoders = dict(cls._decoders)
            cls._decoders[what] = func
            return func

        return decorator
