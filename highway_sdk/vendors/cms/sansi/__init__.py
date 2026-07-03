"""三思厂商VMS协议模块。"""

from highway_sdk.vendors.registry import VendorMetadata

from .codec import SanSiCodec
from .device import SanSiDevice
from .spec import Frame, ResultCode, What

metadata = VendorMetadata(
    name="sansi",
    display_name="三思",
    device_type="vms",
    description="三思VMS设备协议实现",
    device_class=SanSiDevice,
    codec_class=SanSiCodec,
)

__all__ = [
    "Frame",
    "ResultCode",
    "SanSiCodec",
    "SanSiDevice",
    "What",
    "metadata",
]
