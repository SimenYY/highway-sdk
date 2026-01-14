"""VMS设备厂商实现模块。

该模块提供了各种VMS（可变信息标志）设备厂商的协议实现，包括丰海、Nova、Xianke等。
"""

# 丰海厂商实现
from .fenghai.factory import FrameFactory as FenghaiFrameFactory
from .fenghai.parser import Parser as FenghaiParser
from .fenghai.protocol import VmsFenghaiProtocol
from .nova.factory import FrameFactory as NovaFrameFactory
from .nova.parser import Parser as NovaParser

# Nova厂商实现
from .nova.protocol import VmsNovaProtocol
from .sansi.factory import FrameFactory as SansiFrameFactory
from .sansi.parser import Parser as SansiParser

# Sansi厂商实现
from .sansi.protocol import VmsSansiProtocol
from .xianke.factory import FrameFactory as XiankeFrameFactory
from .xianke.parser import Parser as XiankeParser

# Xianke厂商实现
from .xianke.protocol import VmsXiankeProtocol

__all__ = [
    # 丰海
    "VmsFenghaiProtocol",
    "FenghaiFrameFactory",
    "FenghaiParser",
    # Nova
    "VmsNovaProtocol",
    "NovaFrameFactory",
    "NovaParser",
    # Sansi
    "VmsSansiProtocol",
    "SansiFrameFactory",
    "SansiParser",
    # Xianke
    "VmsXiankeProtocol",
    "XiankeFrameFactory",
    "XiankeParser",
]
