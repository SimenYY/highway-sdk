API参考
=========

本部分提供了 Highway SDK 的详细 API 参考文档，包括核心模块、厂商实现和工具函数等。

.. toctree::
   :maxdepth: 2
   :caption: API模块

   core
   registry
   devices/index
   utils

API设计原则
------------

- **一致性** - 所有 API 遵循一致的设计风格和命名规范
- **易用性** - API 设计简洁易用，减少用户的学习成本
- **类型安全** - 提供完整的类型提示，提升开发体验
- **可扩展性** - API 设计便于扩展和定制
- **向后兼容** - 保持 API 的向后兼容性，减少用户的迁移成本

版本管理
----------

API 版本管理采用语义化版本控制（Semantic Versioning），版本号格式为：X.Y.Z

- **X** - 主版本号，当 API 发生不兼容的改变时增加
- **Y** - 次版本号，当增加新功能且向后兼容时增加
- **Z** - 修订号，当修复 bug 且向后兼容时增加

核心模块API
------------

请参考 `core <core>`_ 模块的 API 文档。

厂商注册表API
--------------

请参考 `registry <registry>`_ 模块的 API 文档。

设备类型API
------------

请参考 `devices <devices/index>`_ 模块的 API 文档。

工具函数API
------------

请参考 `utils <utils>`_ 模块的 API 文档。
