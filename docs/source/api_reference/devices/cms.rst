CMS设备API
==========

CMS (Variable Message Sign) 是可变信息标志设备，用于在高速公路上显示可变信息，如路况、天气、事故信息等。

CMS设备厂商实现
----------------

Highway SDK支持多种CMS设备厂商，包括丰海、Nova、Xianke和Sansi等。

丰海 (Fenghai) 厂商实现
^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: highway_sdk.vendors.cms.fenghai
   :members:
   :undoc-members:
   :show-inheritance:

**主要类**：

.. autoclass:: highway_sdk.vendors.cms.fenghai.protocol.VmsFenghaiProtocol
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.vendors.cms.fenghai.factory.FrameFactory
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.vendors.cms.fenghai.parser.Parser
   :members:
   :undoc-members:
   :show-inheritance:

Nova 厂商实现
^^^^^^^^^^^^

.. automodule:: highway_sdk.vendors.cms.nova
   :members:
   :undoc-members:
   :show-inheritance:

**主要类**：

.. autoclass:: highway_sdk.vendors.cms.nova.protocol.VmsNovaProtocol
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.vendors.cms.nova.factory.FrameFactory
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.vendors.cms.nova.parser.Parser
   :members:
   :undoc-members:
   :show-inheritance:

Xianke 厂商实现
^^^^^^^^^^^^^^^

.. automodule:: highway_sdk.vendors.cms.xianke
   :members:
   :undoc-members:
   :show-inheritance:

**主要类**：

.. autoclass:: highway_sdk.vendors.cms.xianke.protocol.VmsXiankeProtocol
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.vendors.cms.xianke.factory.FrameFactory
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.vendors.cms.xianke.parser.Parser
   :members:
   :undoc-members:
   :show-inheritance:

Sansi 厂商实现
^^^^^^^^^^^^^^

.. automodule:: highway_sdk.vendors.cms.sansi
   :members:
   :undoc-members:
   :show-inheritance:

**主要类**：

.. autoclass:: highway_sdk.vendors.cms.sansi.protocol.VmsSansiProtocol
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.vendors.cms.sansi.factory.FrameFactory
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.vendors.cms.sansi.parser.Parser
   :members:
   :undoc-members:
   :show-inheritance: