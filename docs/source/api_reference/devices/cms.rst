VMS设备API
==========

VMS (Variable Message Sign) 是可变信息标志设备，用于在高速公路上显示可变信息，如路况、天气、事故信息等。

VMS设备厂商实现
----------------

Highway SDK支持多种VMS设备厂商，包括丰海、Nova、Xianke和Sansi等。

丰海 (Fenghai) 厂商实现
^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: highway_sdk.vendors.vms.fenghai
   :members:
   :undoc-members:
   :show-inheritance:

**主要类**：

.. autoclass:: highway_sdk.vendors.vms.fenghai.protocol.VmsFenghaiProtocol
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.vendors.vms.fenghai.factory.FrameFactory
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.vendors.vms.fenghai.parser.Parser
   :members:
   :undoc-members:
   :show-inheritance:

Nova 厂商实现
^^^^^^^^^^^^

.. automodule:: highway_sdk.vendors.vms.nova
   :members:
   :undoc-members:
   :show-inheritance:

**主要类**：

.. autoclass:: highway_sdk.vendors.vms.nova.protocol.VmsNovaProtocol
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.vendors.vms.nova.factory.FrameFactory
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.vendors.vms.nova.parser.Parser
   :members:
   :undoc-members:
   :show-inheritance:

Xianke 厂商实现
^^^^^^^^^^^^^^^

.. automodule:: highway_sdk.vendors.vms.xianke
   :members:
   :undoc-members:
   :show-inheritance:

**主要类**：

.. autoclass:: highway_sdk.vendors.vms.xianke.protocol.VmsXiankeProtocol
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.vendors.vms.xianke.factory.FrameFactory
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.vendors.vms.xianke.parser.Parser
   :members:
   :undoc-members:
   :show-inheritance:

Sansi 厂商实现
^^^^^^^^^^^^^^

.. automodule:: highway_sdk.vendors.vms.sansi
   :members:
   :undoc-members:
   :show-inheritance:

**主要类**：

.. autoclass:: highway_sdk.vendors.vms.sansi.protocol.VmsSansiProtocol
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.vendors.vms.sansi.factory.FrameFactory
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.vendors.vms.sansi.parser.Parser
   :members:
   :undoc-members:
   :show-inheritance: