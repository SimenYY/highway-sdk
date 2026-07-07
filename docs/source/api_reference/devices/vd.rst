VD设备API
==========

VD (Vehicle Detector) 是车检器设备，用于检测车辆流量、速度、占有率等信息。

VD设备支持状态
----------------

目前，Highway SDK的VD设备支持正在开发中，尚未正式发布。

我们计划在未来版本中添加以下VD设备厂商的支持：

- 厂商1
- 厂商2
- 厂商3

如果您需要使用VD设备，欢迎联系我们或贡献代码。

扩展VD设备支持
---------------

要扩展VD设备支持，需要：

1. 在 `highway_sdk/vendors/vd/` 目录下创建厂商实现目录
2. 参考CMS厂商实现的 ``spec.py / codec.py / device.py`` 三文件结构
3. 在厂商 ``__init__.py`` 中导出 ``metadata``（``VendorMetadata`` 实例），SDK 会在 ``vendors/__init__.py`` 自动注册
4. 编写测试用例
5. 更新文档

如果您有兴趣贡献VD设备的实现，欢迎提交PR或联系项目维护者。