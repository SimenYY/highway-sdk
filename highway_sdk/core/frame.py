"""帧数据基类模块。

定义了设备通信帧的基本结构。
"""

from pydantic import BaseModel, Field


class BaseFrame(BaseModel):
    """帧数据基类。

    所有厂商的帧类都应该继承此类，定义自己的帧结构。

    Attributes:
        what: 指令码，标识帧的类型。
        data: 数据域，帧携带的有效载荷。
    """

    what: bytes = Field(..., description="指令码")
    data: bytes = Field(default=b"", description="数据域")

    @classmethod
    def from_bytes(cls, message: bytes) -> "BaseFrame":
        """从字节数据解析帧。

        子类必须实现此方法。

        Args:
            message: 原始字节数据。

        Returns:
            BaseFrame: 解析后的帧对象。
        """
        raise NotImplementedError

    def __bytes__(self) -> bytes:
        """将帧转换为字节数据。

        子类必须实现此方法。

        Returns:
            bytes: 帧的字节表示。
        """
        raise NotImplementedError
