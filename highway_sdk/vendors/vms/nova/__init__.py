"""诺瓦厂商VMS协议模块。"""

from highway_sdk.vendors.registry import VendorMetadata

from .codec import NovaCodec
from .device import NovaDevice
from .spec import Frame, ResultCode, What

metadata = VendorMetadata(
    name="nova",
    display_name="诺瓦",
    device_type="vms",
    description="诺瓦VMS设备协议实现",
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
