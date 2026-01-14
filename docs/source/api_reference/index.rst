API参考
=========

本部分提供了Highway SDK的详细API参考文档，包括核心模块、厂商实现、平台集成和工具函数等。

.. toctree::
   :maxdepth: 2
   :caption: API模块

   core
   devices/index
   platforms
   brokers
   utils

API设计原则
------------

- **一致性** - 所有API遵循一致的设计风格和命名规范
- **易用性** - API设计简洁易用，减少用户的学习成本
- **类型安全** - 提供完整的类型提示，提升开发体验
- **可扩展性** - API设计便于扩展和定制
- **向后兼容** - 保持API的向后兼容性，减少用户的迁移成本

版本管理
----------

API版本管理采用语义化版本控制（Semantic Versioning），版本号格式为：X.Y.Z

- **X** - 主版本号，当API发生不兼容的改变时增加
- **Y** - 次版本号，当增加新功能且向后兼容时增加
- **Z** - 修订号，当修复bug且向后兼容时增加

核心模块API
------------

请参考 `core <core>`_ 模块的API文档。

设备类型API
------------

请参考 `devices <devices/index>`_ 模块的API文档。

平台集成API
------------

请参考 `platforms <platforms>`_ 模块的API文档。

Broker集成API
--------------

请参考 `brokers <brokers>`_ 模块的API文档。

工具函数API
------------

请参考 `utils <utils>`_ 模块的API文档。