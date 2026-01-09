# GitHub Copilot 指南 — highway-sdk

以下说明面向在本仓库中工作的 AI coding agents（例如 Copilot / Agents）。目标是让 Agent 能快速理解项目结构、常见模式、测试和运行方式，并给出可执行、低风险的改动建议。

## 一句话概览 ✅
- 这是一个基于 asyncio 的硬件/网关 SDK，包含 `brokers`（MQTT/Kafka/Redis）、`core`（协议、连接器、日志）、`platform`（平台接入实现，如 `supaiot`）、`vendors` / `vms`（厂商设备驱动）和 `tests`（pytest）。

## 快速起步（环境与测试） 🔧
- 使用 Poetry 管理依赖：`poetry install`。或激活本仓库的虚拟环境然后使用 `pytest`。
- 运行测试（含 asyncio）：
  - 全量：`poetry run pytest` 或（激活 venv 后）`pytest`
  - 单测示例：`pytest tests/platform/supaiot/test_client.py::TestSupaiotClient::test_login_success -q`
- 注意：项目依赖 `pytest-asyncio`（异步测试普遍存在）。

## 最重要的代码位置（阅读优先级） 📁
- `highway_sdk/core/` — 网络协议、连接器、日志、通用异常与接口。
  - `protocols.py`：Protocol/Driver 的实现（Req/Resp 队列、DriverTCPClientProtocol、调度器等）。
  - `connectors.py`：TCP/UDP 及重连逻辑。
  - `log.py`：基于 loguru 的日志策略与适配器（PrefixLoggerAdapter）。
- `highway_sdk/brokers/` — MQTT/Kafka/Redis 封装（注意 `mqtt.py` 使用 paho-mqtt v2 callback API）。
- `highway_sdk/platform/supaiot/` — 平台 API 客户端、MQTT 消息模型与 pydantic 示例（重要用于外部接口约定）。
  - `client.py`, `models.py`, `prototypes.py`（示例：序列化别名/扁平化/反扁平化）。
- `vendors/` 与 `vms/` — 厂商驱动与版本文件。
- `tests/` — 含大量示例，Agent 修改后务必运行相关测试。

## 项目约定与风格（对 AI 很重要） 💡
- Pydantic v2用法：
  - 校验/序列化约定：在构造 HTTP/MQTT 负载时通常使用 `model_dump(by_alias=True, exclude_none=True)`；响应使用 `APIResponse.model_validate(resp.json())`。
  - `platform/supaiot/prototypes.py` 使用 `validation_alias` / `serialization_alias` 来在外部平面字段与内部字段间做映射（修改/新增接口字段时按此约定）。
- 环境配置：使用 `pydantic-settings.BaseSettings`，常见 env 前缀：`HIGHWAY_SDK_`（通用）、`SUPAIOT_`（平台）。请通过这些类（例如 `core/config.py`、`platform/supaiot/config.py`）读取配置。
- 异步和通信模式：
  - 常驻连接使用 Protocol + Connector 模式（`DriverTCPClientProtocol`、`TCPReconnectingConnector`）。
  - 简单请求-响应可用 `AioTCPClient`（短连接/一次性请求）。
  - Req/Resp 有队列（futures）实现：见 `ReqRespTCPClientProtocol`。
- 日志：项目使用 loguru，建议在修改代码时保持 `PrefixLoggerAdapter` 用法以保留带前缀的设备上下文日志。
- MQTT：`MqttClientV2` 使用 paho-mqtt Callback API v2（MQTT 5.0）— 注意 `connect(is_async=True)` 与阻塞 `loop_forever()` 的差别。

## 可执行示例（可直接用于测试或快速验证）
- 调用 Supaiot API 并校验：
  - 使用 `SupaiotAPIClient(...).get_devices(...)`，传入 Pydantic Request Model，发送时用 `model_dump(by_alias=True)`。
- 发布实时数据到 MQTT：
  - `SupaiotMQTTClient.publish_real_data(series, sn, data)` 会构建 `RealtimeDataPublishModel` 并调用 `publish(topic, payload)`（payload 已经 `model_dump_json(exclude_none=True)`).

## 对 Agent 的工作建议（安全、低风险） 🎯
- 任何改动后先运行受影响目录下的测试（优先 test 文件），若改动协议/驱动，则运行 `tests/driver/**`。
- 修改外部交互接口（API/消息主题/字段）时：
  - 增加/修改对应 Pydantic 模型（`models.py` 或 `prototypes.py`），并添加/更新单元测试来描述 / 断言新行为。
  - 保持 `by_alias` 的序列化策略；不要直接修改外部字段名到代码内部字段，应该使用 alias/serialization_alias。
- 避免改动全局日志初始化或替换 loguru 的策略，除非需要，并在 PR 中注明原因与回滚计划。
- 对于网络/连接重连逻辑，优先遵循 `TCPReconnectingConnector` 与 `DriverTCPClientProtocol` 的既有重连/退避策略。

## 参考文件（按用途） 🔍
- 配置与日志：`highway_sdk/core/config.py`、`highway_sdk/core/log.py`
- 协议/连接：`highway_sdk/core/protocols.py`、`highway_sdk/core/connectors.py`
- 平台示例：`highway_sdk/platform/supaiot/client.py`、`highway_sdk/platform/supaiot/models.py`、`highway_sdk/platform/supaiot/prototypes.py`
- Broker：`highway_sdk/brokers/mqtt.py`（阅读 MQTT 封装细节）
- 测试模板：`tests/platform/supaiot/test_client.py`（示例 async API 测试）

---

如果你希望我把该文件合并到仓库（我已准备好提交），或者需要我把某些段落改写为英文/精简/扩展示例，请告诉我你想优先改进的部分。💬
