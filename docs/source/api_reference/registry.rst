厂商注册表API
=============

Highway SDK 的厂商注册表提供了厂商元数据定义、注册和发现机制，支持物联网平台动态加载设备协议。

模块概览
--------

.. automodule:: highway_sdk.vendors.registry
   :members:
   :undoc-members:
   :show-inheritance:

核心类和函数
------------

VendorMetadata
^^^^^^^^^^^^^^

.. autoclass:: highway_sdk.vendors.registry.VendorMetadata
   :members:
   :undoc-members:
   :show-inheritance:

VendorRegistry
^^^^^^^^^^^^^^

.. autoclass:: highway_sdk.vendors.registry.VendorRegistry
   :members:
   :undoc-members:
   :show-inheritance:

全局函数
^^^^^^^^

list_vendors
~~~~~~~~~~~~

.. autofunction:: highway_sdk.vendors.registry.list_vendors

get_vendor
~~~~~~~~~~

.. autofunction:: highway_sdk.vendors.registry.get_vendor

create_device
~~~~~~~~~~~~~

.. autofunction:: highway_sdk.vendors.registry.create_device

connect_device
~~~~~~~~~~~~~~

.. autofunction:: highway_sdk.vendors.registry.connect_device

register_vendor
~~~~~~~~~~~~~~~

.. autofunction:: highway_sdk.vendors.registry.register_vendor

使用示例
--------

查看已注册厂商
^^^^^^^^^^^^^^

.. code-block:: python

   from highway_sdk import list_vendors
   
   for vendor in list_vendors():
       print(f"{vendor.name}: {vendor.display_name} ({vendor.device_type})")

动态创建设备
^^^^^^^^^^^^

.. code-block:: python

   from highway_sdk import connect_device, create_device
   
   # 创建并连接设备
   device = await connect_device("dianming", "192.168.1.100", 9000)
   brightness = await device.get_brightness()
   
   # 仅创建实例（不连接）
   device = create_device("fenghai", "192.168.1.101", 9000)

注册自定义厂商
^^^^^^^^^^^^^^

.. code-block:: python

   from highway_sdk import VendorMetadata, register_vendor
   
   metadata = VendorMetadata(
       name="my_vendor",
       display_name="我的厂商",
       device_type="vms",
       description="自定义厂商协议实现",
       device_class=MyDevice,
       codec_class=MyCodec,
   )
   register_vendor(metadata)
