import logging
from datetime import datetime

from prometheus_client import (
    CollectorRegistry,
    Gauge,
)
from prometheus_client.exposition import start_http_server

logger = logging.getLogger(__name__)

# 创建Prometheus注册表
REGISTRY = CollectorRegistry()

# 监控指标定义 - 设备连接状态指标，适用于所有协议类型
CONNECTION_STATUS = Gauge(
    "connection_status",
    "设备连接状态指标 (0=断开, 1=连接)",
    ["device_id"],
    registry=REGISTRY,
)


async def start_prometheus_server(host: str = "0.0.0.0", port: int = 8000) -> None:
    """启动异步Prometheus HTTP服务器

    Args:
        host: 监听地址
        port: 监听端口
    """
    # 使用同步服务器实现，简单可靠
    logger.info(f"启动Prometheus监控服务器，监听 {host}:{port}")
    start_http_server(port=port, addr=host, registry=REGISTRY)


class MetricsMixin:
    """监控指标混入类，用于为协议类提供监控功能"""

    def __init__(self, device_id: str | None = None):
        self.device_id = device_id if device_id is not None else f"device_{datetime.now()}"

    def update_connection_status(self, status: bool) -> None:
        """更新设备连接状态

        Args:
            status: 连接状态，True为连接，False为断开
        """
        CONNECTION_STATUS.labels(device_id=self.device_id).set(1 if status else 0)
