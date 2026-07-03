"""数据标签基类模块。

定义了设备数据的标准化表示，用于统一不同厂商设备的数据格式。

.. deprecated::
    自 v3.0.0 起，`BaseCodec.decode()` 返回 `dict` 而非 `BaseTags` 子类。
    `BaseTags` 仅作为公共 API 兼容保留，不再用于 codec 解码路径。
    新代码应直接使用 `dict` 作为解码返回类型。
"""

from pydantic import BaseModel


class BaseTags(BaseModel):
    """数据标签基类（已弃用于 codec 解码路径）。

    .. deprecated::
        自 v3.0.0 起，`BaseCodec.decode()` 返回 `dict`。
        此类仅作为公共 API 兼容保留，厂商 codec 不再继承使用。
    """

    pass
