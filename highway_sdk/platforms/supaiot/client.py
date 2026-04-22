import asyncio
import logging
from datetime import datetime
from typing import Any

import httpx
from pydantic import ValidationError

from highway_sdk.brokers.mqtt import MqttClientV2

from .exceptions import (
    SupaiotAPIconnectError,
    SupaiotAPIError,
    SupaiotAPILoginError,
    SupaiotAPIResponseValidateError,
)
from .models import (
    APIResponse,
    ClassListRequest,
    ControlReqSubscribeModel,
    ControlRespPublishModel,
    Devices,
    DevicesRealtimeData,
    HistoryDataPublishModel,
    RealtimeDataPublishModel,
)

logger = logging.getLogger(__name__)

__all__ = ["SupaiotAPIClient", "SupaiotMQTTClient"]


# ==============================================================================
# API Client
# ==============================================================================
class SupaiotAPIClient:
    """物联智控API 客户端"""

    def __init__(
        self,
        base_url: str,
        app_id: str,
        app_secret: str,
        project_id: str | None = None,
        *,
        max_retries: int = 3,
        timeout: float = 5.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.app_id = app_id
        self.app_secret = app_secret
        self.project_id = project_id
        self._max_retries = max_retries

        self._lock = asyncio.Lock()
        self.timeout = timeout

        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout, follow_redirects=True)

    async def login(self) -> None:
        payload = {
            "appID": self.app_id,
            "appSecret": self.app_secret,
        }
        if self.project_id is not None:
            payload["projectID"] = self.project_id

        async with httpx.AsyncClient() as client:  # 临时client方式cooikes污染
            try:
                resp = await client.post(
                    f"{self.base_url}/supaiot/api/v2/app/sec/login",
                    json=payload,
                    timeout=self.timeout,
                )
            except httpx.ConnectError as e:
                raise SupaiotAPIconnectError(e) from e

            resp.raise_for_status()
            supaiot_resp = APIResponse.model_validate(resp.json())

            if supaiot_resp.result.resultCode != "0":
                raise SupaiotAPILoginError(f"Login failed: {supaiot_resp.result.resultError}")

            if not isinstance(supaiot_resp.data, dict):
                raise SupaiotAPILoginError("Invalid login response")

            token = supaiot_resp.data.get("token")

            if not token:
                raise SupaiotAPILoginError("Token missing in login response")

            self._client.cookies.set("hypToken", token)

    async def request(
        self,
        method: str,
        url: str,
        *,
        params: dict | None = None,
        json: dict | None = None,
        headers: dict | None = None,
    ) -> APIResponse:
        """物联智控请求，校验响应

        Args:
            method (str): _description_
            url (str): _description_
            params (Optional[dict], optional): _description_. Defaults to None.
            json (Optional[dict], optional): _description_. Defaults to None.
            headers (Optional[dict], optional): _description_. Defaults to None.

        Returns:
            SupaiotResponse: _description_
        """
        try:
            resp = await self._client.request(
                method,
                url,
                params=params,
                json=json,
                headers=headers,
                timeout=self.timeout,
            )
            resp.raise_for_status()
        except httpx.ConnectError as e:
            raise SupaiotAPIconnectError(e) from e
        except Exception as e:
            raise SupaiotAPIError(e) from e

        try:
            return APIResponse.model_validate(resp.json())
        except ValidationError as e:
            raise SupaiotAPIResponseValidateError(e) from e

    async def request_with_login(
        self,
        method: str,
        url: str,
        *,
        params: dict | None = None,
        json: dict | None = None,
        headers: dict | None = None,
    ) -> APIResponse:
        """物联智控api请求，懒加载cookies

        Args:
            method (str): _description_
            url (str): _description_
            params (Optional[dict], optional): _description_. Defaults to None.
            json (Optional[dict], optional): _description_. Defaults to None.
            headers (Optional[dict], optional): _description_. Defaults to None.

        Raises:
            RuntimeError: _description_

        Returns:
            SupaiotResponse: _description_
        """
        if self._client.cookies.get("hypToken") is None:
            await self.login()

        for _ in range(2):
            resp = await self.request(
                method,
                url,
                params=params,
                json=json,
                headers=headers,
            )
            # 如果登录失效，则重新登录
            if resp.result.resultCode == "401":
                await self.login()
                continue

            return resp

        raise SupaiotAPIError("Failed to get a vaild response from Supaiot.")

    # -----------------------------------------------------------------------------
    # 业务接口
    # -----------------------------------------------------------------------------
    async def get_devices(
        self,
        page_num: int = 1,
        page_size: int = 10,
        device_ids: list[str] | None = None,
        app_id: str | None = None,
        area_id: str | None = None,
        class_id: str | None = None,
        class_name: str | None = None,
        class_type: str | None = None,
        labels: list[dict] | None = None,
        name: str | None = None,
        project_id: str | None = None,
        sub_off: bool | None = None,
        type_: str | None = None,
    ) -> APIResponse:
        """条件查询多个设备实例列表(简化版)

        提供直接传参的方式查询设备列表，无需手动构造DeviceListRequest对象

        Args:
            page_num (int): 请求页码，默认为1
            page_size (int): 每页条数，默认为10
            device_ids (Optional[List[str]]): 设备实例ID列表
            app_id (str | None): 应用ID
            area_id (str | None): 区域ID
            class_id (str | None): 原型ID
            class_name (str | None): 原型名称
            class_type (str | None): 设备类型
            labels (list[str] | None): 标签列表
            name (str | None): 设备名称
            project_id (str | None): 项目ID
            sub_off (bool | None): 是否包含子集区域数据
            type_ (str | None): 类型

        Returns:
            SupaiotResponse: 包含设备列表的响应结果
        """
        payload = Devices(
            pageNum=page_num,
            pageSize=page_size,
            ID=device_ids,
            appId=app_id,
            areaID=area_id,
            classID=class_id,
            className=class_name,
            classType=class_type,
            label=labels,
            name=name,
            projectID=project_id,
            subOff=sub_off,
            type=type_,
        )
        return await self.request_with_login(
            "POST",
            "/supaiot/api/v2/device/list",
            json=payload.model_dump(by_alias=True, exclude_none=True),
        )

    async def get_device_class(self, class_id: str) -> APIResponse:
        """查询指定设备原型详情

        Args:
            class_id (str): 原型ID

        Returns:
            SupaiotResponse: _description_
        """
        return await self.request_with_login(
            "GET",
            "/supaiot/api/v2/class",
            params={"classID": class_id},
        )

    async def get_devices_realtime_data(self, device_ids: list | None = None) -> APIResponse:
        """多设备实时状态查询

        Args:
            request (DeviceRealtimeDataListRequest): _description_

        Returns:
            SupaiotResponse: _description_
        """
        if device_ids is None:
            device_ids = []
        payload = DevicesRealtimeData(ID=device_ids)
        return await self.request_with_login(
            "POST",
            "/supaiot/api/v2/data/real/device/list",
            json=payload.model_dump(by_alias=True, exclude_none=True),
        )

    async def get_device_realtime_data(self, id_: str) -> APIResponse:
        """获取设备实时数据

        Args:
            id_ (str): 设备ID

        Returns:
            SupaiotResponse: _description_
        """
        return await self.request_with_login("GET", "/supaiot/api/v2/data/real/device", params={"ID": id_})

    async def get_class_list(
        self,
        page_num: int = 1,
        page_size: int = 10,
        class_id: str | None = None,
        detail_level: int | None = None,
        class_type: str | None = None,
        labels: list[dict] | None = None,
        name: str | None = None,
        project_id: str | None = None,
        type_: str | None = None,
    ) -> APIResponse:
        """条件查询设备原型列表

        Args:
            page_num (int, optional): _description_. Defaults to 1.
            page_size (int, optional): _description_. Defaults to 10.
            class_id (str | None, optional): _description_. Defaults to None.
            class_type (str | None, optional): _description_. Defaults to None.
            labels (list[str] | None, optional): _description_. Defaults to None.
            name (str | None, optional): _description_. Defaults to None.
            project_id (str | None, optional): _description_. Defaults to None.
            type_ (str | None, optional): _description_. Defaults to None.
        """
        payload = ClassListRequest(
            pageNum=page_num,
            pageSize=page_size,
            detailLevel=detail_level,
            classID=class_id,
            classType=class_type,
            label=labels,
            name=name,
            projectID=project_id,
            type=type_,
        )

        return await self.request_with_login(
            "POST",
            "/supaiot/api/v2/class/list",
            json=payload.model_dump(by_alias=True, exclude_none=True),
        )


# ==============================================================================
# MQTT Client
# ==============================================================================
class SupaiotMQTTClient(MqttClientV2):
    """物联智控 MQTT Client

    Args:
        MqttClientV2 (_type_): _description_
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 9312,
        client_id: str | None = None,
        auth: tuple[str, str] | None = ("mviotroot", "mviotroot123"),
        user_data: Any = None,
        qos: int = 0,
    ) -> None:
        super().__init__(host, port, client_id, auth, user_data, qos)

    def publish_real_data(self, series: str, sn: str, data: dict):
        prmm = RealtimeDataPublishModel(series=series, sn=sn, time=datetime.now(), timestamp=None, data=data)
        return self.publish(topic=prmm.get_topic(), payload=prmm.model_dump_json(exclude_none=True))

    def subscribe_control_req(self, series: str, sn: str):
        return self.subscribe(topic=ControlReqSubscribeModel.get_topic(series, sn))

    def publish_history_data(self, series: str, sn: str, data: list):
        phm = HistoryDataPublishModel(series=series, sn=sn, time=datetime.now(), data=data)
        return self.publish(topic=phm.get_topic(), payload=phm.model_dump_json(exclude_none=True))

    def publish_control_res(self, series: str, sn: str, sequence: int, data: dict):
        pcrm = ControlRespPublishModel(series=series, sn=sn, time=datetime.now(), sequence=sequence, data=data)
        return self.publish(topic=pcrm.get_topic(), payload=pcrm.model_dump_json(exclude_none=True))
