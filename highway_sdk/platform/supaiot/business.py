from typing import List
from bidict import bidict
from .client import SupaiotAsyncClient


class SupaiotBusinessService:
    """物联智控业务服务类
    """
    def __init__(self, client: SupaiotAsyncClient) -> None:
        self._client = client

    async def get_code_ip_bidict(self, class_id: str) -> bidict:
        """获取物联智控中设备编码与IP的双向映射表

        Args:
            client (SupaiotAsyncClient): _description_
            prototype_id (str): _description_

        Returns:
            bidict: _description_
        """
        code_ip_dict = {}
        page_num, page_size = 1, 20
        while True:
            res = await self._client.list_devices(page_num, page_size, class_id=class_id)
            if isinstance(res.data, dict):
                device_list = res.data.get("data")

                if not device_list:
                    break

                for device in device_list:
                    ID = device.get("ID")
                    description: str = device.get("description", "") # 例如：ZK2+465/192.168.1.1
                    fields = description.split("/")
                    if len(fields) >= 2:
                        ip = fields[1]
                        code_ip_dict[ID] = ip

                page_num += 1
            else:
                break
        return bidict(code_ip_dict)
