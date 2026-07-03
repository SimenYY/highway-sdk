核心模块API
============

Highway SDK的核心模块提供了SDK的基础功能，包括传输层、编解码、设备抽象、帧定义和日志配置等。

模块概览
--------

.. automodule:: highway_sdk.core
   :members:
   :undoc-members:
   :show-inheritance:

核心类和函数
------------

Transport
^^^^^^^^^

.. autoclass:: highway_sdk.core.transport.Transport
   :members:
   :undoc-members:
   :show-inheritance:

BaseDevice
^^^^^^^^^^

.. autoclass:: highway_sdk.core.device.BaseDevice
   :members:
   :undoc-members:
   :show-inheritance:

BaseCodec
^^^^^^^^^

.. autoclass:: highway_sdk.core.codec.BaseCodec
   :members:
   :undoc-members:
   :show-inheritance:

BaseFrame
^^^^^^^^^

.. autoclass:: highway_sdk.core.frame.BaseFrame
   :members:
   :undoc-members:
   :show-inheritance:

BaseTags
^^^^^^^^

.. deprecated:: 3.0.0
   `BaseCodec.decode()` 现返回 `dict`，`BaseTags` 仅作为公共 API 兼容保留。

.. autoclass:: highway_sdk.core.tags.BaseTags
   :members:
   :undoc-members:
   :show-inheritance:

get_logger
^^^^^^^^^^

.. autofunction:: highway_sdk.core.log.get_logger

异常类
^^^^^^

.. autoclass:: highway_sdk.core.exceptions.HighwaySDKError
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.core.exceptions.ConnectionError
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.core.exceptions.ConnectionTimeoutError
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.core.exceptions.ConnectionLostError
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.core.exceptions.ResponseTimeoutError
   :members:
   :undoc-members:
   :show-inheritance:

.. autoclass:: highway_sdk.core.exceptions.ProtocolError
   :members:
   :undoc-members:
   :show-inheritance:
