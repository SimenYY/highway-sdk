from typing import Protocol
from highway_sdk.core.interface import BaseTags
from highway_sdk.vendors.vms.fenghai.protocol import VmsFenghaiProtocol
from .client import SupaiotMQTTClient
from .tags import to_supaiot_tags
from .models import DeviceInfoMode


class SupaiotMQTTGatewayProtocol(Protocol):
    """用于接入物联智控MQTT网关的协议"""

    def mqtt_real_publish(self, series: str, sn: str, data: dict):
        """发送实时数据"""
        ...

#==============================================================================
# 情报板
#==============================================================================
class SupaiotVmsFenghaiProtocol(VmsFenghaiProtocol):
    """物联智控 情报板 丰海协议"""
    def __init__(
        self, *, device_info: DeviceInfoMode, mqtt_client: SupaiotMQTTClient, **kwargs
    ):
        super().__init__(**kwargs)

        self.device_info = device_info
        self.mqtt_client = mqtt_client

    def on_message_parsed(self, tags: BaseTags):
        try:
            self.mqtt_real_publish(
                self.device_info.series, self.device_info.sn, to_supaiot_tags(tags)
            )
        except Exception as e:
            self.log.exception(e)

    def on_connected(self) -> None:
        self.add_interval_jobs(
            [
                self.read_download_file,
                self.read_get_item,
            ]
        )

    def mqtt_real_publish(self, series: str, sn: str, data: dict):
        self.mqtt_client.publish_real_data(series, sn, data)


