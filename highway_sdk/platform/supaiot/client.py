import asyncio
from typing import List, Optional
import httpx
from .models import DeviceListRequest, DeviceRealtimeDataListRequest, SupaiotResponse


class SupaiotAsyncClient:
    """物联智控API 客户端"""

    def __init__(
        self,
        base_url: str,
        app_id: str,
        app_secret: str,
        project_id: Optional[str] = None,
        *,
        max_retries: int = 1,
        timeout: float = 5.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.app_id = app_id
        self.app_secret = app_secret
        self.project_id = project_id
        self._max_retries = max_retries

        self._lock = asyncio.Lock()
        self.timeout = timeout

        self._client = httpx.AsyncClient(
            base_url=self.base_url, timeout=self.timeout, follow_redirects=True
        )

    async def _login(self) -> None:
        payload = {
            "appID": self.app_id,
            "appSecret": self.app_secret,
        }
        if self.project_id is not None:
            payload["projectID"] = self.project_id

        async with httpx.AsyncClient() as client:  # 临时client方式cooikes污染
            resp = await client.post(
                f"{self.base_url}/supaiot/api/v2/app/sec/login",
                json=payload,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            supaiot_resp = SupaiotResponse.model_validate(resp.json())

            if supaiot_resp.result.resultCode != "0":
                raise ValueError(f"Login failed: {supaiot_resp.result.resultError}")

            token = supaiot_resp.data.get("token")

            if not token:
                raise KeyError("Token missing in login response")

            self._client.cookies.set("hypToken", token)

    async def _request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[dict] = None,
        json: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> SupaiotResponse:
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
        resp = await self._client.request(
            method,
            url,
            params=params,
            json=json,
            headers=headers,
            timeout=self.timeout,
        )
        resp.raise_for_status()

        return SupaiotResponse.model_validate(resp.json())

    async def _api_request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[dict] = None,
        json: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> SupaiotResponse:
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
            await self._login()

        for _ in range(2):
            resp = await self._request(
                method,
                url,
                params=params,
                json=json,
                headers=headers,
            )
            if resp.result.resultCode == "401":
                await self._login()
                continue

            return resp

        raise RuntimeError("Failed to get a vaild response from Supaiot.")

    # -----------------------------------------------------------------------------
    # 业务接口
    # -----------------------------------------------------------------------------
    async def list_devices(
        self,
        page_num: int = 1,
        page_size: int = 10,
        device_ids: Optional[List[str]] = None,
        app_id: Optional[str] = None,
        area_id: Optional[str] = None,
        class_id: Optional[str] = None,
        class_name: Optional[str] = None,
        class_type: Optional[str] = None,
        labels: Optional[List[dict]] = None,
        name: Optional[str] = None,
        project_id: Optional[str] = None,
        sub_off: Optional[bool] = None,
        type_: Optional[str] = None,
    ) -> SupaiotResponse:
        """条件查询多个设备实例列表(简化版)
        
        提供直接传参的方式查询设备列表，无需手动构造DeviceListRequest对象

        Args:
            page_num (int): 请求页码，默认为1
            page_size (int): 每页条数，默认为10
            device_ids (Optional[List[str]]): 设备实例ID列表
            app_id (Optional[str]): 应用ID
            area_id (Optional[str]): 区域ID
            class_id (Optional[str]): 原型ID
            class_name (Optional[str]): 原型名称
            class_type (Optional[str]): 设备类型
            labels (Optional[List[dict]]): 标签列表
            name (Optional[str]): 设备名称
            project_id (Optional[str]): 项目ID
            sub_off (Optional[bool]): 是否包含子集区域数据
            type_ (Optional[str]): 类型

        Returns:
            SupaiotResponse: 包含设备列表的响应结果
        """
        payload = DeviceListRequest(
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
        
        return await self._api_request(
            "POST",
            "/supaiot/api/v2/device/list",
            json=payload.model_dump(by_alias=True, exclude_none=True),
        )
        
    async def list_device_realtime_data(
        self, id_: list = []
    ) -> SupaiotResponse:
        """多设备实时状态查询

        Args:
            request (DeviceRealtimeDataListRequest): _description_

        Returns:
            SupaiotResponse: _description_
        """
        payload = DeviceRealtimeDataListRequest(ID=id_)
        return await self._api_request(
            "POST", "/supaiot/api/v2/data/real/device/list", json=payload.model_dump(by_alias=True, exclude_none=True)
        )

    async def get_device_realtime_data(
        self, id_: str
    ) -> SupaiotResponse:
        """获取设备实时数据

        Args:
            id_ (str): 设备ID

        Returns:
            SupaiotResponse: _description_
        """
        return await self._api_request("GET", "/supaiot/api/v2/data/real/device", params={"ID": id_})