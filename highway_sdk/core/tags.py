"""数据标签基类模块。

定义了设备数据的标准化表示，用于统一不同厂商设备的数据格式。
"""

from pydantic import BaseModel


class BaseTags(BaseModel):
    """数据标签基类。

    所有设备返回的数据都应该继承此类，提供标准化的数据结构。
    """

    pass
