CMS设备API
==========

CMS (Variable Message Sign) 是可变信息标志设备，用于在高速公路上显示可变信息，如路况、天气、事故信息等。

CMS设备厂商实现
----------------

Highway SDK支持多种CMS设备厂商，包括电明、丰海、Nova、三思和显科等。

电明 (DianMing) 厂商实现
^^^^^^^^^^^^^^^^^^^^^^^^

**主要类**：

.. autoclass:: highway_sdk.vendors.cms.dianming.device.DianMingCms
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.vendors.cms.dianming.codec.DianMingCodec
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.vendors.cms.dianming.spec.Frame
   :members:
   :undoc-members:
   :show-inheritance:

丰海 (FengHai) 厂商实现
^^^^^^^^^^^^^^^^^^^^^^^

**主要类**：

.. autoclass:: highway_sdk.vendors.cms.fenghai.device.FengHaiCms
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.vendors.cms.fenghai.codec.FengHaiCodec
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.vendors.cms.fenghai.spec.Frame
   :members:
   :undoc-members:
   :show-inheritance:

Nova 厂商实现
^^^^^^^^^^^^

**主要类**：

.. autoclass:: highway_sdk.vendors.cms.nova.device.NovaCms
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.vendors.cms.nova.codec.NovaCodec
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.vendors.cms.nova.spec.Frame
   :members:
   :undoc-members:
   :show-inheritance:

三思 (SanSi) 厂商实现
^^^^^^^^^^^^^^^^^^^^^

**主要类**：

.. autoclass:: highway_sdk.vendors.cms.sansi.device.SanSiCms
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.vendors.cms.sansi.codec.SanSiCodec
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.vendors.cms.sansi.spec.Frame
   :members:
   :undoc-members:
   :show-inheritance:

显科 (XianKe) 厂商实现
^^^^^^^^^^^^^^^^^^^^^^

**主要类**：

.. autoclass:: highway_sdk.vendors.cms.xianke.device.XianKeCms
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.vendors.cms.xianke.codec.XianKeCodec
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.vendors.cms.xianke.spec.Frame
   :members:
   :undoc-members:
   :show-inheritance:
