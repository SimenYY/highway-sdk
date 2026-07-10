"""电明厂商CMS协议模块。"""

from highway_sdk.vendors.registry import VendorMetadata

from .codec import DianMingCodec
from .device import DianMingCms
from .spec import (
    BaseMedia,
    Bmp,
    Color,
    Esc,
    Font,
    FontSize,
    Frame,
    Gif,
    Item,
    Jpg,
    Play,
    Png,
    ResultCode,
    Text,
    What,
)

metadata = VendorMetadata(
    name="dianming",
    display_name="电明",
    device_type="cms",
    description="电明CMS设备协议实现",
    device_class=DianMingCms,
    codec_class=DianMingCodec,
)

__all__ = [
    "BaseMedia",
    "Bmp",
    "Color",
    "DianMingCms",
    "DianMingCodec",
    "Esc",
    "Font",
    "FontSize",
    "Frame",
    "Gif",
    "Item",
    "Jpg",
    "Play",
    "Png",
    "ResultCode",
    "Text",
    "What",
    "metadata",
]
