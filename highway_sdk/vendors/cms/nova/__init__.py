"""诺瓦厂商CMS协议模块。"""

from highway_sdk.vendors.registry import VendorMetadata

from .codec import NovaCodec
from .device import NovaDevice
from .spec import Frame, ResultCode, What

metadata = VendorMetadata(
    name="nova",
    display_name="诺瓦",
    device_type="cms",
    description="诺瓦CMS设备协议实现",
    device_class=NovaDevice,
    codec_class=NovaCodec,
)

__all__ = [
    "Frame",
    "NovaCodec",
    "NovaDevice",
    "ResultCode",
    "What",
    "metadata",
]
