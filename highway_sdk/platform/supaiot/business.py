import logging
import ipaddress
from pydantic.networks import IPvAnyAddress
from highway_sdk.utils.judge import is_ip, is_user_port, is_chainage
from .client import SupaiotAPIClient
from .models import DeviceInfoMode

logger = logging.getLogger(__name__)


class SupaiotBusinessService:
    """物联智控业务服务类"""

    def __init__(self, client: SupaiotAPIClient) -> None:
        self._client = client

    async def get_devices_info(self, class_id: str):
        """获取设备信息

        Args:
            class_id (str): _description_

        Returns:
            Dict[str, dict]: {ip: {"series": xxx, "sn": xxx, "device_id": xxx, "class_id": xxx}}
        """
        logger.info(f"获取设备信息，设备原型ID：{class_id}")
        devices_info: dict[
            IPvAnyAddress, DeviceInfoMode
        ] = {}  # {ip: {"series": xxx, "sn": xxx, "device_id": xxx, "class_id": xxx}}
        series = ""
        res = await self._client.get_device_class(class_id)
        if isinstance(res.data, dict):
            mqtt_info = res.data["mqttInfo"]
            for field in mqtt_info:
                if field["key"] == "SERIES":
                    series = field["default"]

        page_num, page_size = 1, 20
        while True:
            res = await self._client.list_devices(
                page_num, page_size, class_id=class_id
            )
            if isinstance(res.data, dict):
                device_list = res.data.get("data")

                if not device_list:
                    break

                for device in device_list:
                    device_id = device["ID"]
                    description: str = device.get(
                        "description", ""
                    )  # 例如：ZK105+200/33.74.39.15/5009/h64w128

                    fields = description.split("/")
                    ip, port, chainage = None, None, None
                    for field in fields:
                        if is_chainage(field):
                            chainage = field
                        elif is_ip(field):
                            ip = ipaddress.ip_address(field)
                        elif is_user_port(field):
                            port = int(field)
                    sn = device["mqttInfo"]["SN"]
                    if ip is None or port is None:
                        logger.error(f"缺失通信地址, 设备描述：{description}")
                        continue
                    devices_info[ip] = DeviceInfoMode(
                        series=series,
                        sn=sn,
                        port=port,
                        ip=ip,
                        device_id=device_id,
                        class_id=class_id,
                        chainage=chainage,
                    )

                page_num += 1
            else:
                break

        return devices_info

    async def get_devices_address(self, class_id: str):
        """获取设备通信地址

        {
            "port": 8888,
            "ip_list": [
                "127.0.0.1",
                "127.0.0.2"
            ]
        }

        Args:
            class_id (str): _description_

        Returns:
            _type_: _description_
        """
        logger.info(f"获取设备通信地址，设备原型ID：{class_id}")
        devices_address = {}
        devices_address["ip_list"] = []
        page_num, page_size = 1, 20
        while True:
            res = await self._client.list_devices(
                page_num, page_size, class_id=class_id
            )
            if isinstance(res.data, dict):
                device_list = res.data.get("data")

                if not device_list:
                    break

                for device in device_list:
                    description: str = device.get(
                        "description", ""
                    )  # 例如：ZK105+200/33.74.39.15/5009/h64w128
                    fields = description.split("/")
                    # 按照有则显示，无则静默，缺失需要软件查看
                    for field in fields:
                        if is_ip(field):
                            devices_address["ip_list"].append(field)
                        elif is_user_port(field):
                            devices_address["port"] = field
                page_num += 1
            else:
                break
        return devices_address

    async def get_mqtt_class_ids(self):
        """获取MQTT接入设备原型列表

        Returns:
            _type_: _description_
        """
        page_num, page_size = 1, 20
        mqtt_class_list = []
        while True:
            res = await self._client.list_class(page_num, page_size)
            if isinstance(res.data, dict):
                class_list = res.data.get("data")

                if not class_list:
                    break
                for class_ in class_list:
                    class_id = class_["classID"]
                    res = await self._client.get_device_class(class_id)
                    if isinstance(res.data, dict):
                        if "mqttInfo" in res.data.keys():
                            mqtt_class_list.append(class_id)
                    else:
                        break

                page_num += 1
            else:
                break
        return mqtt_class_list
