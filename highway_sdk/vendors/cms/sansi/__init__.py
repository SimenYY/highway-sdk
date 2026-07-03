"""三思厂商CMS协议模块。"""

from highway_sdk.vendors.registry import VendorMetadata

from .codec import SanSiCodec
from .device import SanSiDevice
from .spec import Frame, ResultCode, What

metadata = VendorMetadata(
    name="sansi",
    display_name="三思",
    device_type="cms",
    description="三思CMS设备协议实现",
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
