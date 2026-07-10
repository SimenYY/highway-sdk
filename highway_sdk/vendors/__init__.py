"""设备厂商实现模块。

该模块提供了各种设备厂商的协议实现。
"""

from .cms import (
    DianMingCms,
    DianMingCodec,
    FengHaiCms,
    FengHaiCodec,
    NovaCms,
    NovaCodec,
    SanSiCms,
    SanSiCodec,
    XianKeCms,
    XianKeCodec,
)

# 自动注册所有厂商到全局注册表
from .cms.dianming import metadata as dianming_metadata
from .cms.fenghai import metadata as fenghai_metadata
from .cms.nova import metadata as nova_metadata
from .cms.sansi import metadata as sansi_metadata
from .cms.xianke import metadata as xianke_metadata
from .registry import (
    VendorMetadata,
    VendorRegistry,
    connect_device,
    create_device,
    get_vendor,
    list_vendors,
    register_vendor,
    registry,
)

registry.register(dianming_metadata)
registry.register(fenghai_metadata)
registry.register(nova_metadata)
registry.register(sansi_metadata)
registry.register(xianke_metadata)

__all__ = [
    "DianMingCms",
    "DianMingCodec",
    "FengHaiCms",
    "FengHaiCodec",
    "NovaCms",
    "NovaCodec",
    "SanSiCms",
    "SanSiCodec",
    "VendorMetadata",
    "VendorRegistry",
    "XianKeCms",
    "XianKeCodec",
    "connect_device",
    "create_device",
    "get_vendor",
    "list_vendors",
    "register_vendor",
    "registry",
]
