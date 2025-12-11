import asyncio
from typing import Any
from collections.abc import Callable

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic.networks import IPvAnyAddress
from functools import partial

from highway_sdk.core.config import LogConfig
from highway_sdk.core.driver import (
    TCPClientProtocol,
    TCPReconnectingConnector,
    BaseConnector,
    UDPConnector,
    UDPProtocol,
)

from .business import SupaiotBusinessService
from .client import SupaiotAPIClient, SupaiotMQTTClient
from .config import SupaiotConfig
from .models import SubscribeControlReqModel, DeviceInfoMode
from .protocols import SupaiotMQTTGatewayProtocol


class SupaiotMQTTGatewayConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="GATEWAY_", env_file=[".env.local", ".env"], extra="allow"
    )
    supaiot: SupaiotConfig = SupaiotConfig()
    log: LogConfig = LogConfig()


class SupaiotMQTTGateway:
    """物联智控MQTT接入设备网关

    Notes:
        1. 北向依赖：api-client, mqtt-client
        2. 南向依赖：connector, protocol_class
    """

    def __init__(
        self, protocol_cls: type[SupaiotMQTTGatewayProtocol], class_ids: list[str]
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
        self.settings = SupaiotMQTTGatewayConfig()  # load settings

    def enable_log(self):
        """启用日志"""
        self.settings.log.config_loguru()

    async def north_connect(self):
        """北向连接，平台连接"""

        self.api_client = SupaiotAPIClient(
            self.settings.supaiot.API_BASE_URL,
            self.settings.supaiot.API_APP_ID,
            self.settings.supaiot.API_APP_SECRET,
        )
        await self.api_client.login()

        self.service = SupaiotBusinessService(self.api_client)
        for class_id in self.class_ids:
            self.devices_info.update(await self.service.get_devices_info(class_id))

        self.mqtt_client = SupaiotMQTTClient(
            self.settings.supaiot.MQTT_BROKER_HOST,
            self.settings.supaiot.MQTT_BROKER_PORT,
            auth=(
                self.settings.supaiot.MQTT_BROKER_USR,
                self.settings.supaiot.MQTT_BROKER_PWD,
            ),
            qos=self.settings.supaiot.MQTT_QOS,
        )

        # 批量订阅控制主题
        def batch_subscribe():
            for _, info in self.devices_info.items():
                # 订阅控制主题, 在mqtt回调时订阅主题以增加稳定性
                self.mqtt_client.subscribe_control_req(info.series, info.sn)

        self.mqtt_client.set_on_connect(on_sucess=batch_subscribe)
        self.mqtt_client.connect()
        self.north_finished = True

    def set_on_message(self, callback: Callable[..., Any]):
        """设置控制消息回调函数"""
        self.mqtt_client.set_on_message(callback)

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
                    SubscribeControlReqModel.get_topic(info.series, info.sn)
                ] = conn

    async def run(self):
        await self.north_connect()
        await asyncio.sleep(0.1)
        await self.south_connect()
