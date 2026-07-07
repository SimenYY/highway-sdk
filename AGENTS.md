```
# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.
```

## Highway SDK Codebase Guide

### Project Overview

The **Highway SDK** is a Python library for interfacing with highway electrical and mechanical devices and intelligent devices, with a strong focus on Variable Message Signs (CMS) systems. It's designed as a modular, extensible platform supporting multiple vendor protocols and communication standards.

- **Repository Type**: Python Package (Poetry-managed)
- **Version**: 2.0.0.post48.dev0+103e4b9 (dynamic versioning via git)
- **Python Version**: Python 3.11+
- **License**: GPL-3.0

### Key Development Commands

#### Installation

```bash
poetry install              # Install dependencies
```

#### Testing

```bash
poetry run pytest tests/    # Run all tests
poetry run pytest tests/test_transport.py -v    # Run specific test file
# 覆盖率（CI 阈值 45%，目标 70%；配置见 pyproject.toml [tool.coverage.report]）
poetry run pytest --cov=highway_sdk --cov-branch --cov-report=term
```

#### Build

```bash
poetry build               # Build package
poetry version             # Show version
```

#### Development Tools

```bash
pre-commit run --all-files # Run pre-commit hooks (ruff lint + format)
poetry run ruff check .    # Lint
poetry run ruff format --check .   # Format check
poetry run pyright         # Type check (standard mode, 0 errors expected)
poetry run pip-audit --strict  # Dependency vulnerability scan (non-blocking)
```

### Codebase Architecture

#### Directory Structure

```
highway_sdk/
├── highway_sdk/           # Main package source
│   ├── core/              # Core infrastructure
│   │   ├── transport.py   # TCP transport with auto-reconnect
│   │   ├── codec.py       # Base codec with decorator registration
│   │   ├── device.py      # Base device class
│   │   ├── frame.py       # Base frame class
│   │   ├── tags.py        # Base tags class
│   │   ├── exceptions.py  # Exception hierarchy
│   │   ├── log.py         # Logging configuration
│   │   ├── reader.py      # Data reader utilities
│   │   ├── settings.py    # Configuration management
│   │   └── constants.py   # Global constants
│   ├── vendors/           # Vendor-specific CMS implementations
│   │   ├── registry.py    # Vendor registry and factory
│   │   └── cms/           # CMS devices
│   │       ├── _base.py   # CMS base classes (CMSFrame)
│   │       ├── dianming/  # DianMing (电明)
│   │       ├── fenghai/   # FengHai (丰海)
│   │       ├── nova/      # Nova (诺瓦)
│   │       ├── sansi/     # SanSi (三思)
│   │       └── xianke/    # XianKe (显科)
│   └── utils/             # Utility functions
├── tests/                 # Test suite
├── examples/              # Demo scripts
├── docs/                  # Documentation
├── pyproject.toml         # Poetry configuration
└── README.md              # Documentation
```

#### Core Modules

**core/transport.py** - TCP transport layer

- `Transport`: Async TCP client with request-response pattern
- Built-in auto-reconnect with exponential backoff
- Supports async context manager

**core/codec.py** - Codec base class

- `BaseCodec`: Base codec with decorator-based registration
- `register()`: Class method decorator to register decoders

**core/device.py** - Device base class

- `BaseDevice`: Abstract device class with unified interface
- `connect()`: Class method to create and connect device
- Supports custom transport factory

**core/frame.py** - Frame base class

- `BaseFrame`: Pydantic-based frame structure
- `__bytes__()`: Abstract method for frame serialization

**core/tags.py** - Tags base class (deprecated for codec decode path since v3.0.0)

- `BaseTags`: Pydantic-based data structure (kept for public API compatibility; `BaseCodec.decode()` now returns `dict`)

**core/log.py** - Logging system

- `get_logger(name)`: Returns standard logging.Logger instance
- Library provides logging interface only, does not configure log output
- Application should use logging or loguru to configure all log output

**vendors/registry.py** - Vendor registry and factory

- `VendorMetadata`: Frozen dataclass for vendor info (name, display_name, device_type, device_class, codec_class)
- `VendorRegistry`: Registry class managing vendor registration and device creation
- `list_vendors()`: List all registered vendors
- `get_vendor(name)`: Get vendor metadata
- `create_device(vendor, host, port)`: Create device instance (unconnected)
- `connect_device(vendor, host, port)`: Create and connect device

#### Vendor Implementations (vendors/cms/)

Each vendor module follows:

- `spec.py`: Frame definition (What enum, Frame class)
- `codec.py`: Codec implementation
- `device.py`: Device client

Supported vendors:

- **dianming/** (电明 CMS)
- **fenghai/** (丰海 CMS)
- **nova/** (诺瓦 CMS)
- **sansi/** (三思 CMS)
- **xianke/** (显科 CMS)

### Key Dependencies

Core: pydantic, pydantic-settings, filelock, platformdirs
Async: pytest-asyncio

### Design Principles

1. **Protocol Abstraction**: Each vendor protocol is implemented as a separate module with shared interfaces
2. **Async-First Architecture**: Heavy use of asyncio for efficient I/O operations
3. **Modular Design**: Clear separation between core infrastructure and vendor implementations
4. **Dict-Based Codec Returns**: `BaseCodec.decode()` returns `dict` (since v3.0.0); `BaseTags` kept for public API compatibility only
5. **Standard Logging**: Uses Python's built-in logging module
6. **Automatic Recovery**: TCP reconnection with exponential backoff

### Common Development Tasks

1. **Adding a new CMS vendor protocol**:
   - Create vendor directory under `vendors/cms/`
   - Implement `spec.py`, `codec.py`, and `device.py`
   - Add tests in `tests/`

2. **Testing changes**:
   - Run affected tests using `poetry run pytest`
   - Add new tests for changes
   - Ensure all tests pass before committing

### Important Files

- `pyproject.toml`: Project configuration and dependencies
- `highway_sdk/core/transport.py`: Core TCP transport implementation
- `highway_sdk/core/codec.py`: Codec base class with registration mechanism
- `highway_sdk/core/device.py`: Device base class
- `highway_sdk/vendors/cms/*/device.py`: Vendor-specific CMS clients
- `tests/test_*.py`: Test suite

### Critical Rules

- **Async-first**: Always use async versions of libraries where available
- **Codec registration**: Use `@BaseCodec.register(what)` decorator on classmethod
- **Frame serialization**: Each vendor's Frame class must implement `__bytes__()`
- **Device inheritance**: Vendor devices inherit from `BaseDevice`, not `CMSDevice`
- **No CMSCodec/CMSDevice**: These intermediate classes were removed; inherit directly from BaseCodec/BaseDevice
- **Vendor metadata**: Each vendor module must export `metadata` (VendorMetadata instance) and auto-register in `vendors/__init__.py`
- **CI 门禁**: 改动 `.gitlab-ci.yml` 时务必保持 6 个 stage 顺序：code_quality → test → type_check → security → build_docs → publish；publish 必须 `needs` 测试 job，禁止 `except: tags` 让发布跳过测试
- **覆盖率阈值**: 在 `pyproject.toml [tool.coverage.report] fail_under` 修改时同步更新 `.gitlab-ci.yml` 的 `COVERAGE_FAIL_UNDER` 变量；当前 45%，目标 70%
- **真实报文测试**: 厂商接口测试必须基于真实设备通信日志或协议标准报文，禁止凭空构造；测试文件 docstring 注明报文来源（"实际日志" / "协议标准 Vx.x.x" / "sdk-v2.x.x protocol.py"）
- **set_play_list 签名**: 所有 vendor 的 `set_play_list` 接收 `items: list[CmsPlayItem]`，不接收 `content: str`；内部 `_items_to_content()` 负责将 CmsPlayItem 转为协议字符串（Play/Item 模型降为内部编码器）
- **异常/日志中文化**: 所有 `raise` 和 `logger` 消息必须用中文，格式为"操作失败 + 可能原因"，不包含技术黑话；调试日志中的 hex 数据保留但描述用中文
- **颜色格式转换**: CmsPlayItem 的 `font_color` 用 `#RRGGBB` 格式，vendor 的 Color 枚举用 12 位 `RRRGGGBBB000` 格式；`_hex_color_to_vendor` 必须生成 12 字符而非 15 字符
- **异常命名禁遮蔽**: 禁止用 `ConnectionError`（遮蔽内建 OSError 子类）和 `ValidationError`（遮蔽 pydantic.ValidationError）作为 SDK 异常类名；连接异常基类用 `DeviceConnectionError`，帧校验异常基类用 `FrameValidationError`
- **disconnect 不篡改配置**: `Transport.disconnect()` 不准覆写 `auto_reconnect` 字段；用 `_closing` 标志区分「主动断开」与「被动断连可重连」，保留用户初始 auto_reconnect 配置
- **超时默认 None**: `Transport.request` / `BaseDevice.request` / vendor `_request` 的 `timeout` 参数默认 `None`（回退 Transport 初始化超时），禁止 4 处各硬编码 `3.0` 导致漂移；FakeTransport 测试子类也必须用 `float | None = None` 否则 pyright reportIncompatibleMethodOverride
- **BaseDevice 不继承 ABC**: 无抽象方法，惯例是 `raise NotImplementedError`；只继承 `Generic[CodecT]`
