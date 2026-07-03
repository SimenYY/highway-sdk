"""显科厂商CMS协议模块。"""

from highway_sdk.vendors.registry import VendorMetadata

from .codec import XianKeCodec
from .device import XianKeDevice
from .spec import Frame, ResultCode, What

metadata = VendorMetadata(
    name="xianke",
    display_name="显科",
    device_type="cms",
    description="显科CMS设备协议实现",
    device_class=XianKeDevice,
    codec_class=XianKeCodec,
)

__all__ = [
    "Frame",
    "ResultCode",
    "What",
    "XianKeCodec",
    "XianKeDevice",
    "metadata",
]
