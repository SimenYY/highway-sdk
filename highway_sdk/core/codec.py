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

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """子类创建时扫描带 _decoder_what 标记的方法，注册到子类独立的 _decoders。"""
        super().__init_subclass__(**kwargs)
        cls._decoders = {}
        for value in cls.__dict__.values():
            # 解包 classmethod → 获取 __func__（可调用）
            method = getattr(value, "__func__", value)
            # 解包 lru_cache → 查找 _decoder_what 标记
            raw = getattr(method, "__wrapped__", method)
            what = getattr(raw, "_decoder_what", None)
            if what is not None:
                cls._decoders[what] = method

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

    @staticmethod
    def register(what: Any):
        """注册解码函数的装饰器。

        在函数上标记 _decoder_what，由 __init_subclass__ 统一注册到子类独立的 _decoders。

        Args:
            what: 指令标识。

        Returns:
            Callable: 装饰器函数。
        """

        def decorator(func: Callable[..., BaseTags]) -> Callable[..., BaseTags]:
            func._decoder_what = what  # type: ignore[attr-defined]
            return func

        return decorator
