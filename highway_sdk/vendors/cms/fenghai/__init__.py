"""丰海厂商CMS协议模块。"""

from highway_sdk.vendors.registry import VendorMetadata

from .codec import FengHaiCodec
from .device import FengHaiDevice
from .spec import Frame, ResultCode, What

metadata = VendorMetadata(
    name="fenghai",
    display_name="丰海",
    device_type="cms",
    description="丰海CMS设备协议实现",
    device_class=FengHaiDevice,
    codec_class=FengHaiCodec,
)

__all__ = [
    "FengHaiCodec",
    "FengHaiDevice",
    "Frame",
    "ResultCode",
    "What",
    "metadata",
]
