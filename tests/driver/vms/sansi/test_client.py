import pytest
import pytest_asyncio
from highway_sdk.vendors.vms.sansi.client import VmsSanSiClient


class TestVmsSanSiClient:
    @pytest_asyncio.fixture(scope="class")
    async def client(self):
        async with VmsSanSiClient(host="127.0.0.1", port=8888) as client:
            yield client

    @pytest.mark.asyncio
    async def test_download_file(self, client: VmsSanSiClient):
        await client.download_file()

    @pytest.mark.asyncio
    async def test_get_item(self, client: VmsSanSiClient):
        await client.get_item()

    @pytest.mark.asyncio
    async def test_upload_file(self, client: VmsSanSiClient):
        await client.upload_file("")

    @pytest.mark.asyncio
    async def test_get_brightness(self, client: VmsSanSiClient):
        await client.get_brightness()

    @pytest.mark.asyncio
    async def test_set_brightness(self, client: VmsSanSiClient):
        await client.set_brightness(50)

