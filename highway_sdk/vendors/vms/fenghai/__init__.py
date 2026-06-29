"""丰海厂商VMS协议模块。"""

from .codec import FengHaiCodec
from .device import FengHaiDevice
from .spec import Frame, ResultCode, What

__all__ = [
    "FengHaiCodec",
    "FengHaiDevice",
    "Frame",
    "ResultCode",
    "What",
]
