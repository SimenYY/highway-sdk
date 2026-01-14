核心模块API
============

Highway SDK的核心模块提供了SDK的基础功能，包括协议定义、连接器、日志配置和监控等。

模块概览
--------

.. automodule:: highway_sdk.core
   :members:
   :undoc-members:
   :show-inheritance:

核心类和函数
------------

BaseTags
^^^^^^^^

.. autoclass:: highway_sdk.core.base.BaseTags
   :members:
   :undoc-members:
   :show-inheritance:

LogConfig
^^^^^^^^^

.. autoclass:: highway_sdk.core.config.LogConfig
   :members:
   :undoc-members:
   :show-inheritance:

TCPReconnectingConnector
^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: highway_sdk.core.connectors.TCPReconnectingConnector
   :members:
   :undoc-members:
   :show-inheritance:

UDPConnector
^^^^^^^^^^^

.. autoclass:: highway_sdk.core.connectors.UDPConnector
   :members:
   :undoc-members:
   :show-inheritance:

HighwaySDKException
^^^^^^^^^^^^^^^^^^

.. autoclass:: highway_sdk.core.exceptions.HighwaySDKException
   :members:
   :undoc-members:
   :show-inheritance:

LoguruConfig
^^^^^^^^^^^

.. autoclass:: highway_sdk.core.log.LoguruConfig
   :members:
   :undoc-members:
   :show-inheritance:

MetricsMixin
^^^^^^^^^^^

.. autoclass:: highway_sdk.core.metrics.MetricsMixin
   :members:
   :undoc-members:
   :show-inheritance:

start_prometheus_server
^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: highway_sdk.core.metrics.start_prometheus_server

DriverTCPClientProtocol
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: highway_sdk.core.protocols.DriverTCPClientProtocol
   :members:
   :undoc-members:
   :show-inheritance:

MonitoredDriverTCPClientProtocol
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: highway_sdk.core.protocols.MonitoredDriverTCPClientProtocol
   :members:
   :undoc-members:
   :show-inheritance:

ReqRespTCPClientProtocol
^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: highway_sdk.core.protocols.ReqRespTCPClientProtocol
   :members:
   :undoc-members:
   :show-inheritance:

MonitoredReqRespTCPClientProtocol
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: highway_sdk.core.protocols.MonitoredReqRespTCPClientProtocol
   :members:
   :undoc-members:
   :show-inheritance:

Reader
^^^^^^

.. autoclass:: highway_sdk.core.reader.Reader
   :members:
   :undoc-members:
   :show-inheritance: