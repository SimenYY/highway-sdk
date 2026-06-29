"""Highway SDK - Python SDK for Highway devices.

This SDK provides a unified interface for communicating with various highway devices,
including VMS (Variable Message Signs) and VD (Vehicle Detectors) from different vendors.
"""

import logging

from platformdirs import PlatformDirs

from ._version import __version__
from .core import (
    BaseCodec,
    BaseDevice,
    BaseFrame,
    BaseTags,
    LogConfig,
    Transport,
    setup_logger,
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
    XianKeCodec,
    XianKeDevice,
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
    "LogConfig",
    "NovaCodec",
    "NovaDevice",
    "SanSiCodec",
    "SanSiDevice",
    "Transport",
    "XianKeCodec",
    "XianKeDevice",
    "__version__",
    "setup_logger",
]

logger = logging.getLogger(__name__)
dirs = PlatformDirs(appauthor=__name__)
