工具函数API
============

Highway SDK提供了一系列通用的工具函数，用于简化开发。

工具函数概述
--------------

工具函数模块包含各种通用的工具函数，便于在开发过程中使用。

**主要功能**：

- 装饰器工具
- 判断工具函数
- 文件锁工具

装饰器工具
------------

装饰器工具提供了各种装饰器，用于简化函数的开发和使用。

**核心函数**：

.. automodule:: highway_sdk.utils.decorator
   :members:
   :undoc-members:
   :show-inheritance:

**使用示例**：

.. code-block:: python

    from highway_sdk.utils.decorator import singleton, retry

    # 使用单例装饰器
    @singleton
    class MySingletonClass:
        def __init__(self):
            self.value = 0

    # 使用重试装饰器
    @retry(max_retries=3, delay=1)
    def my_function():
        # 可能失败的操作
        pass

判断工具函数
------------

判断工具函数提供了各种判断功能，用于简化条件判断。

**核心函数**：

.. automodule:: highway_sdk.utils.judge
   :members:
   :undoc-members:
   :show-inheritance:

**使用示例**：

.. code-block:: python

    from highway_sdk.utils.judge import is_valid_ip, is_valid_port

    # 判断IP地址是否有效
    if is_valid_ip("192.168.1.1"):
        print("IP地址有效")
    
    # 判断端口是否有效
    if is_valid_port(8080):
        print("端口有效")

文件锁工具
----------

文件锁工具提供了文件锁定功能，用于处理并发访问文件的情况。

**核心类**：

.. automodule:: highway_sdk.utils.lock
   :members:
   :undoc-members:
   :show-inheritance:

**使用示例**：

.. code-block:: python

    from highway_sdk.utils.lock import FileLock

    # 创建文件锁
    with FileLock("data.txt"):
        # 操作文件，此时文件被锁定
        with open("data.txt", "a") as f:
            f.write("new data\n")
    # 退出with块，文件锁自动释放

扩展新工具函数
--------------

要扩展新的工具函数，需要：

1. 在 `highway_sdk/utils/` 目录下的相应文件中添加新的工具函数
2. 确保函数具有良好的文档字符串
3. 编写测试用例
4. 更新文档

如果您有兴趣贡献新的工具函数，欢迎提交PR或联系项目维护者。