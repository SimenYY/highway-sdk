"""Highway SDK - Python SDK for Highway devices.

This SDK provides a unified interface for communicating with various highway devices,
including VMS (Variable Message Signs) and VD (Vehicle Detectors) from different vendors.
"""

import logging

from platformdirs import PlatformDirs

from ._version import __version__

__name__ = "highway-sdk"
__all__ = ["__version__"]

logger = logging.getLogger(__name__)
dirs = PlatformDirs(appauthor=__name__)

# 从core模块导入常用组件，方便用户直接使用
from .core import (
    BaseTags,
    DriverTCPClientProtocol,
    HighwaySDKException,
    LoguruConfig,
    MetricsMixin,
    TCPReconnectingConnector,
    UDPConnector,
    start_prometheus_server,
)
