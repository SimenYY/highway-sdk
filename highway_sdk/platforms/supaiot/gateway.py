import asyncio
from typing import Any
from collections.abc import Callable
import logging

from pydantic.networks import IPvAnyAddress
from functools import partial
import aiomqtt

from highway_sdk.core.protocols import (
    TCPClientProtocol,
    UDPProtocol,
)
from highway_sdk.core.connectors import (
    TCPReconnectingConnector,
    BaseConnector,
    UDPConnector,
)
from .business import SupaiotBusinessService
from .client import SupaiotAPIClient
from .config import SupaiotConfig
from .models import ControlReqSubscribeModel, DeviceInfoMode
from .protocols import MQTTGatewayProtocol

logger = logging.getLogger(__name__)

__all__ = ["SupaiotMQTTGateway"]


class SupaiotMQTTGateway:
    """物联智控MQTT接入设备网关

    Notes:
        1. 北向依赖：api-client, mqtt-client
        2. 南向依赖：connector, protocol_class
    """

    def __init__(
        self, protocol_cls: type[MQTTGatewayProtocol], class_ids: list[str]
    ) -> None:
        self.connector_cls: type[BaseConnector]

        if issubclass(protocol_cls, TCPClientProtocol):
            self.connector_cls = TCPReconnectingConnector
        elif issubclass(protocol_cls, UDPProtocol):
            self.connector_cls = UDPConnector
        else:
            raise ValueError(
                "protocol_class must be a subclass of TCPClientProtocol or UDPProtocol"
            )

        self.protocol_cls = protocol_cls
        self.class_ids = class_ids  # 设备原型编码
        self.devices_info: dict[IPvAnyAddress, DeviceInfoMode] = {}  # ip: device_info
        self.control_connectors: dict[str, BaseConnector] = {}
        self.north_finished: bool = False
        self.settings = SupaiotConfig()  # load settings

        # 物联智控api客户端
        self.api_client = SupaiotAPIClient(
            self.settings.API_BASE_URL,
            self.settings.API_APP_ID,
            self.settings.API_APP_SECRET,
        )
        # 物联智控mqtt客户端
        self.mqtt_client = aiomqtt.Client(
            hostname=self.settings.MQTT_BROKER_HOST,
            port=self.settings.MQTT_BROKER_PORT,
            username=self.settings.MQTT_BROKER_USR,
            password=self.settings.MQTT_BROKER_PWD,
            logger=logger,
        )

    async def north_connect(self, need_subsribe: bool = True) -> None:
        """北向连接，平台连接"""

        # 通过获取设备描述以构建设备信息
        self.service = SupaiotBusinessService(self.api_client)
        for class_id in self.class_ids:
            self.devices_info.update(await self.service.get_devices_info(class_id))

        if need_subsribe:
            await self.mqtt_client.__aenter__()
            for _, info in self.devices_info.items():
                await self.mqtt_client.subscribe(
                    ControlReqSubscribeModel.get_topic(info.series, info.sn)
                )

        self.north_finished = True

    def set_on_message(self, callback: Callable[..., Any]):
        """设置控制消息回调函数"""
        ...

    async def south_connect(self, **kwargs):
        """南向连接，设备连接

        Raises:
            RuntimeError: _description_
        """
        if not self.north_finished:
            raise RuntimeError("North connection not finished")

        async with asyncio.TaskGroup() as tg:
            for ip, info in self.devices_info.items():
                # 注入设备信息，以便能够在实例中访问，需要protocol支持注入
                protocol_cls = partial(
                    self.protocol_cls,
                    device_info=info,
                    mqtt_client=self.mqtt_client,
                )

                conn = self.connector_cls(str(ip), info.port, protocol_cls, **kwargs)

                tg.create_task(conn.create())
                self.control_connectors[
                    ControlReqSubscribeModel.get_topic(info.series, info.sn)
                ] = conn

    async def run(self):
        await self.north_connect()
        await asyncio.sleep(0.1)
        await self.south_connect()
