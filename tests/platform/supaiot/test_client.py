from flask import request
import pytest
from highway_sdk.platform.supaiot.client import SupaiotClient
from highway_sdk.platform.supaiot.models import DeviceListRequest, SupaiotResponse

class TestSupaiotClient:
    
    @pytest.fixture
    def client(self):
        
        return SupaiotClient(
            base_url="http://10.10.100.83:9080",
            app_id="d96161f66f204121b6b5371a3e386934",
            app_secret="wo0NCtPIzTluSmyN",
        )
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: SupaiotClient):
        await client._login()

        assert client._client.cookies.get("hypToken") is not None
    
    @pytest.mark.asyncio
    async def test_login_fail(self, client: SupaiotClient):
        client.app_id += "1" # 模拟 app_id 错误
        await client._login()
        
        
    
    @pytest.mark.asyncio
    async def test_list_devices(self, client: SupaiotClient):
        resp: SupaiotResponse = await client.list_device(
            DeviceListRequest(
                pageNum=1,
                pageSize=10
            )
        )
        
        assert resp.result.resultCode == "0"
        
        