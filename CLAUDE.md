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
poetry run pytest          # Run all tests
poetry run pytest tests/driver/vms/dianming/v2_3_0/  # Run specific vendor tests
poetry run pytest tests/core/test_connector.py -v    # Run individual test file with verbose output
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
│   ├── core/              # Core infrastructure (TCP/UDP, logging, config)
│   ├── interface/         # Abstract interfaces
│   ├── platform/          # Platform integrations (SupaIoT, Central Monitoring)
│   ├── vendors/           # Vendor-specific VMS implementations
│   ├── brokers/           # Message broker clients (MQTT, Kafka, Redis)
│   ├── transport/         # Transport layer
│   └── utils/             # Utility functions (locks, decorators, validation)
├── tests/                 # Test suite with vendor-specific tests
├── pyproject.toml         # Poetry configuration
└── README.md              # Documentation
```

#### Core Modules

**core/driver.py** - Asyncio-based TCP/UDP communication
- `AioTCPClient`: Async TCP client with request-response pattern
- `TCPReconnectingConnector`: Auto-reconnect with exponential backoff
- `UDPConnector`: UDP protocol implementation
- Various connection management classes

**core/interface.py** - Protocol interfaces
- `BaseMessageParser`: Message parsing protocol
- `BaseTags`: Dataclass base for tag-based data structures

**core/log.py** - Logging system
- Loguru integration with custom handlers
- Colorized console output
- Log message prefixing

**core/settings.py** - Configuration
- YAML/JSON file-based config
- pydantic-settings for environment variable support

#### Vendor Implementations (vendors/vms/)

Multiple VMS vendor protocols are supported, each with version-specific implementations:
- **dianming/** (DianMing VMS) - v2_3_0
- **fenghai/** (FengHai VMS)
- **nova/** (Nova VMS) - v3_11_5
- **sansi/** (SanSi VMS)
- **xianke/** (XianKe VMS) - v1_4_2
- **yingsha/** (YingSha VMS) - v2_2_0

Each vendor module follows:
- `client.py`: Main client interface
- `media.py`: Media/playlist management
- `spec.py`: Protocol specifications and packet structures
- `parse.py`: Message parsing utilities (optional)

#### Platform Integrations

**platform/supaiot/** - SupaIoT Platform
- MQTT-based client for device communication
- Gateway and business logic layers
- Protocol implementations and data models

**platform/center/** - Central Monitoring System
- Device data models
- Protocol specifications

#### Brokers (brokers/)

- **mqtt.py**: MQTT v5.0 client wrapper (paho-mqtt v2+)
- **kafka.py**: Apache Kafka client
- **redis.py**: Redis client
- **config.py**: Broker configuration management

### Testing

Comprehensive test coverage with pytest:
- Tests organized by module: `tests/core/`, `tests/driver/vms/<vendor>/`, `tests/platform/`
- Asyncio testing with `pytest-asyncio`
- Mock servers for integration testing
- Each vendor has tests for client, media, and protocol functionality

### Key Dependencies

Core: loguru, pydantic, paho-mqtt, twisted, click, requests
Async: httpx, aiomqtt, pytest-asyncio
Databases: sqlalchemy[asyncio], aioodbc
Brokers: confluent-kafka, redis
Utilities: filelock, apscheduler, bidict

### Design Principles

1. **Protocol Abstraction**: Each vendor protocol is implemented as a separate module with shared interfaces
2. **Async-First Architecture**: Heavy use of asyncio for efficient I/O operations
3. **Modular Design**: Clear separation between core infrastructure, vendor implementations, and platform integrations
4. **Tag-Based Data Structures**: `BaseTags` dataclass system for structured data exchange
5. **Comprehensive Logging**: Integrated loguru logging with support for intercepting standard logging
6. **Automatic Recovery**: TCP reconnection with exponential backoff

### Common Development Tasks

1. **Adding a new VMS vendor protocol**:
   - Create vendor directory under `vendors/vms/`
   - Implement `client.py`, `media.py`, and `spec.py`
   - Add tests in `tests/driver/vms/<vendor>/`
   - Follow existing patterns from other vendor implementations

2. **Implementing a new platform integration**:
   - Create module under `platform/`
   - Implement client, protocol, and data model files
   - Add tests in `tests/platform/`

3. **Testing changes**:
   - Run affected tests using `poetry run pytest`
   - Add new tests for changes
   - Ensure all tests pass before committing

### Important Files

- `pyproject.toml`: Project configuration and dependencies
- `highway_sdk/core/driver.py`: Core asyncio-based TCP/UDP protocol implementation
- `highway_sdk/core/exceptions.py`: Exception hierarchy
- `highway_sdk/core/log.py`: Logging system configuration
- `highway_sdk/vendors/vms/*/client.py`: Vendor-specific VMS clients
- `highway_sdk/platform/supaiot/client.py`: SupaIoT platform integration
- `tests/*/test_*.py`: Comprehensive test suite
