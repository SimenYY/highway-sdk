安装指南
==========

Highway SDK 提供了多种安装方式，您可以根据需要选择适合的安装方式。

从 PyPI 安装
------------

推荐使用 `pip` 从 PyPI 安装 Highway SDK：

.. code-block:: bash

    pip install highway-sdk

从源码安装
------------

如果您需要最新的开发版本或希望修改源码，可以从 GitHub 克隆仓库并从源码安装：

.. code-block:: bash

    # 克隆仓库
    git clone https://github.com/your-organization/highway-sdk.git

    # 进入目录
    cd highway-sdk

    # 安装开发依赖
    pip install -e "[dev]"

    # 或使用 poetry 安装
    poetry install

依赖要求
----------

Highway SDK 需要 Python 3.11 或更高版本。

主要依赖包：

- pydantic - 数据验证和序列化
- filelock - 文件锁
- pydantic-settings - 配置管理
- platformdirs - 平台特定目录

开发依赖：

- pytest - 测试框架
- pytest-asyncio - 异步测试支持
- sphinx-rtd-theme - Sphinx 主题
- furo - 现代化 Sphinx 主题
- sphinx-autobuild - 自动构建文档
- sphinx-copybutton - 代码复制功能
- sphinx-tabs - 选项卡功能
- pre-commit - 预提交钩子

验证安装
----------

安装完成后，您可以通过以下方式验证安装是否成功：

.. code-block:: python

    import highway_sdk
    print(f"Highway SDK 版本: {highway_sdk.__version__}")

如果输出了版本号，则说明安装成功。

升级 Highway SDK
----------------

使用 pip 升级 Highway SDK：

.. code-block:: bash

    pip install --upgrade highway-sdk

卸载 Highway SDK
----------------

使用 pip 卸载 Highway SDK：

.. code-block:: bash

    pip uninstall highway-sdk