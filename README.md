# Highway SDK

Highway SDK 是一个用于管理和控制 VMS (Variable Message Sign) 设备的统一接口库，支持多个厂商的协议实现（如丰海、Nova、 Xianke 等）。

## 功能特性

- **统一接口**：提供一致的 API 接口，屏蔽不同厂商协议的差异
- **多厂商支持**：集成多个 VMS 厂商的 SDK 实现
- **模块化设计**：采用模块化架构，易于扩展新厂商支持
- **完整的协议实现**：支持设备的配置、监控、媒体管理等功能
- **类型提示**：提供完整的 Python 类型提示，提升开发体验
- **代码质量**：使用 Ruff 进行代码检查和格式化，确保代码质量

## 支持的设备与厂商

### VMS (可变信息标志)
- [x] 丰海 (Fenghai)
- [x] Nova
- [x] Xianke
- [x] Yingsha
- [x] Sansi

### VD (车检器)
- [ ] 待添加

> **注**：支持的设备种类和厂商还在持续更新中，欢迎贡献。

## 安装

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/your-organization/highway-sdk.git

# 进入目录
cd highway-sdk

# 安装开发依赖
pip install -e ".[dev]"
```

### 从 PyPI 安装

```bash
pip install highway-sdk
```

## 快速开始

### 基本使用示例

```python
# 示例代码将在后续添加
```

## 项目结构

```
highway-sdk/
├── highway_sdk/                  # 主源码目录
│   ├── __init__.py               # 包初始化文件
│   └── vendors/                  # 厂商实现目录
│       └── vms/                  # VMS 设备实现
│           ├── _base.py          # 基础类和工具
│           ├── fenghai/          # 丰海厂商实现
│           ├── nova/             # Nova 厂商实现
│           ├── xianke/           # Xianke 厂商实现
│           ├── yingsha/          # Yingsha 厂商实现
│           └── sansi/            # Sansi 厂商实现
├── tests/                        # 测试目录
│   └── vendors/                  # 厂商测试
│       └── vms/                  # VMS 设备测试
├── .pre-commit-config.yaml       # pre-commit 配置
├── pyproject.toml                # 项目配置
└── README.md                     # 项目说明文档
```

## 开发指南

### 代码风格

项目使用 Ruff 进行代码检查和格式化，遵循 PEP 8 编码规范。

### 提交代码前的检查

1. 安装 pre-commit：
   ```bash
   pip install pre-commit
   ```

2. 安装 Git 钩子：
   ```bash
   pre-commit install
   ```

3. 运行所有检查：
   ```bash
   pre-commit run --all-files
   ```

### 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定厂商的测试
pytest tests/vendors/vms/fenghai/
```

## 扩展新厂商支持

要添加新的 VMS 厂商支持，请按照以下步骤操作：

1. 在 `highway_sdk/vendors/vms/` 目录下创建新厂商的目录（如 `new_vendor/`）
2. 实现以下文件：
   - `spec.py`：定义协议规范（如帧结构、指令码等）
   - `factory.py`：实现 `FrameFactory` 类，用于创建请求帧
   - `parser.py`：实现 `Parser` 类，用于解析响应帧
   - `protocol.py`：实现协议客户端，处理网络通信
   - `media.py`：实现媒体相关的类和工具

3. 参考现有厂商的实现方式，确保与统一接口保持一致。

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 联系方式

- 项目维护者：Adz Lovelace
- 邮箱：heyinyu.butterfly.11@gmail.com
- 问题反馈：[GitHub Issues](https://github.com/your-organization/highway-sdk/issues)