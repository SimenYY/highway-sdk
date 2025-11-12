import pytest
from highway_sdk.platform.supaiot.client import SupaiotAsyncClient
from highway_sdk.platform.supaiot.models import (
    DeviceListRequest,
    SupaiotResponse,
    DeviceRealtimeDataListRequest,
)


class TestSupaiotClient:
    @pytest.fixture
    def client(self):
        return SupaiotAsyncClient(
            base_url="http://10.10.100.83:9080",
            app_id="d96161f66f204121b6b5371a3e386934",
            app_secret="wo0NCtPIzTluSmyN",
        )

    @pytest.mark.asyncio
    async def test_login_success(self, client: SupaiotAsyncClient):
        await client.login()

        assert client._client.cookies.get("hypToken") is not None

    @pytest.mark.asyncio
    async def test_login_fail(self, client: SupaiotAsyncClient):
        client.app_id += "1"  # 模拟 app_id 错误
        with pytest.raises(ValueError):
            await client.login()

        client.app_secret += "1"  # 模拟 app_secret 错误
        with pytest.raises(ValueError):
            await client.login()

    @pytest.mark.asyncio
    async def test_list_devices(self, client: SupaiotAsyncClient):
        resp: SupaiotResponse = await client.list_device(
            DeviceListRequest(pageNum=1, pageSize=1)
        )

        assert resp.result.resultCode == "0"
        
        
    @pytest.mark.asyncio
    async def test_list_device_realtime_data(self, client: SupaiotAsyncClient):
        resp: SupaiotResponse = await client.list_device(
            DeviceListRequest(pageNum=1, pageSize=1)
        )
        # 验证设备列表响应
        assert resp.result.resultCode == "0"
        assert resp.data is not None
        assert "data" in resp.data
        assert len(resp.data["data"]) > 0

        # 获取设备ID
        id_ = resp.data["data"][0]["ID"]
        assert id_ is not None
        
        resp = await client.list_device_realtime_data(
            DeviceRealtimeDataListRequest(ID=[id_])
        )

        assert resp.result.resultCode == "0"