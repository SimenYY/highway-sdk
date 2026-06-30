"""电明厂商VMS协议模块。"""

from highway_sdk.vendors.registry import VendorMetadata

from .codec import DianMingCodec
from .device import DianMingDevice
from .spec import Frame, ResultCode, What

metadata = VendorMetadata(
    name="dianming",
    display_name="电明",
    device_type="vms",
    description="电明VMS设备协议实现",
    device_class=DianMingDevice,
    codec_class=DianMingCodec,
)

__all__ = [
    "DianMingCodec",
    "DianMingDevice",
    "Frame",
    "ResultCode",
    "What",
    "metadata",
]
