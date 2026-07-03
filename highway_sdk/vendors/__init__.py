"""设备厂商实现模块。

该模块提供了各种设备厂商的协议实现。
"""

from .cms import (
    DianMingCodec,
    DianMingDevice,
    FengHaiCodec,
    FengHaiDevice,
    NovaCodec,
    NovaDevice,
    SanSiCodec,
    SanSiDevice,
    XianKeCodec,
    XianKeDevice,
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
    "DianMingCodec",
    "DianMingDevice",
    "FengHaiCodec",
    "FengHaiDevice",
    "NovaCodec",
    "NovaDevice",
    "SanSiCodec",
    "SanSiDevice",
    "VendorMetadata",
    "VendorRegistry",
    "XianKeCodec",
    "XianKeDevice",
    "connect_device",
    "create_device",
    "get_vendor",
    "list_vendors",
    "register_vendor",
    "registry",
]
