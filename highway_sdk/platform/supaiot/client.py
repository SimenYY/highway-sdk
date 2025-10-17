import asyncio
from typing import Optional
import httpx
from .models import DeviceListRequest, DeviceRealtimeDataListRequest, SupaiotResponse


class SupaiotClient:
    """物联智控API 客户端
    """
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

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/supaiot/api/v2/app/sec/login",
                json=payload,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            supaiot_resp = SupaiotResponse.model_validate(resp.json())

            if supaiot_resp.result.resultCode != "0":
                raise httpx.RequestError(f"Login failed: {supaiot_resp.result.resultError}")

            token = supaiot_resp.data.get("token")

            if not token:
                raise httpx.RequestError("Token missing in login response")

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
    async def list_device(self, request: DeviceListRequest) -> SupaiotResponse:
        """条件查询多个设备实例列表

        Args:
            request (DeviceListRequest): _description_

        Returns:
            SupaiotResponse: _description_
        """
        payload = request.model_dump(by_alias=True, exclude_none=True)

        return await self._api_request("POST", "/supaiot/api/v2/device/list", json=payload)

    async def list_device_real_data(self, request: DeviceRealtimeDataListRequest) -> SupaiotResponse:
        """多设备实时状态查询

        Args:
            request (DeviceRealtimeDataListRequest): _description_

        Returns:
            SupaiotResponse: _description_
        """
        payload = request.model_dump(by_alias=True, exclude_none=True)

        return await self._api_request("POST", "/supaiot/api/v2/data/real/device/list", json=payload)