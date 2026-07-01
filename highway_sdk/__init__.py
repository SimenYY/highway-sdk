"""Highway SDK - Python SDK for Highway devices.

This SDK provides a unified interface for communicating with various highway devices,
including VMS (Variable Message Signs) and VD (Vehicle Detectors) from different vendors.
"""

from ._version import __version__
from .core import (
    BaseCodec,
    BaseDevice,
    BaseFrame,
    BaseTags,
    Transport,
    get_logger,
)
from .vendors import (
    DianMingCodec,
    DianMingDevice,
    FengHaiCodec,
    FengHaiDevice,
    NovaCodec,
    NovaDevice,
    SanSiCodec,
    SanSiDevice,
    VendorMetadata,
    XianKeCodec,
    XianKeDevice,
    connect_device,
    create_device,
    get_vendor,
    list_vendors,
    register_vendor,
)

__name__ = "highway_sdk"
__all__ = [
    "BaseCodec",
    "BaseDevice",
    "BaseFrame",
    "BaseTags",
    "DianMingCodec",
    "DianMingDevice",
    "FengHaiCodec",
    "FengHaiDevice",
    "NovaCodec",
    "NovaDevice",
    "SanSiCodec",
    "SanSiDevice",
    "Transport",
    "VendorMetadata",
    "XianKeCodec",
    "XianKeDevice",
    "__version__",
    "connect_device",
    "create_device",
    "get_logger",
    "get_vendor",
    "list_vendors",
    "register_vendor",
]
