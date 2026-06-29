```
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
```

## Highway SDK Codebase Guide

### Project Overview

The **Highway SDK** is a Python library for interfacing with highway electrical and mechanical devices and intelligent devices, with a strong focus on Variable Message Signs (VMS) systems. It's designed as a modular, extensible platform supporting multiple vendor protocols and communication standards.

- **Repository Type**: Python Package (Poetry-managed)
- **Version**: 2.0.0.post48.dev0+103e4b9 (dynamic versioning via git)
- **Python Version**: Python 3.10+
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
```

#### Build

```bash
poetry build               # Build package
poetry version             # Show version
```

#### Development Tools

```bash
pre-commit run --all-files # Run pre-commit hooks (linting, type checking)
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
│   ├── vendors/           # Vendor-specific VMS implementations
│   │   └── vms/           # VMS devices
│   │       ├── _base.py   # VMS base classes (VMSFrame)
│   │       ├── dianming/  # DianMing (电明)
│   │       ├── fenghai/   # FengHai (丰海)
│   │       ├── nova/      # Nova (诺瓦)
│   │       ├── sansi/     # SanSi (三思)
│   │       ├── xianke/    # XianKe (显科)
│   │       └── jinxiao/   # JinXiao (锦效)
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

**core/tags.py** - Tags base class

- `BaseTags`: Pydantic-based data structure for device responses

**core/log.py** - Logging system

- Loguru integration with custom handlers
- Colorized console output
- Log message prefixing

#### Vendor Implementations (vendors/vms/)

Each vendor module follows:

- `spec.py`: Frame definition (What enum, Frame class)
- `codec.py`: Codec implementation
- `device.py`: Device client

Supported vendors:

- **dianming/** (电明 VMS)
- **fenghai/** (丰海 VMS)
- **nova/** (诺瓦 VMS)
- **sansi/** (三思 VMS)
- **xianke/** (显科 VMS)

### Key Dependencies

Core: loguru, pydantic, httpx, platformdirs, python-dotenv, filelock, bidict
Async: pytest-asyncio

### Design Principles

1. **Protocol Abstraction**: Each vendor protocol is implemented as a separate module with shared interfaces
2. **Async-First Architecture**: Heavy use of asyncio for efficient I/O operations
3. **Modular Design**: Clear separation between core infrastructure and vendor implementations
4. **Tag-Based Data Structures**: `BaseTags` dataclass system for structured data exchange
5. **Comprehensive Logging**: Integrated loguru logging
6. **Automatic Recovery**: TCP reconnection with exponential backoff

### Common Development Tasks

1. **Adding a new VMS vendor protocol**:
   - Create vendor directory under `vendors/vms/`
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
- `highway_sdk/vendors/vms/*/device.py`: Vendor-specific VMS clients
- `tests/test_*.py`: Test suite

### Critical Rules

- **Async-first**: Always use async versions of libraries where available
- **Codec registration**: Use `CodecClass._decoders[what] = func` after class definition
- **Frame serialization**: Each vendor's Frame class must implement `__bytes__()`
- **Device inheritance**: Vendor devices inherit from `BaseDevice`, not `VMSDevice`
- **No VMSCodec/VMSDevice**: These intermediate classes were removed; inherit directly from BaseCodec/BaseDevice
