import asyncio
from highway_sdk.core.protocol import TcpClientSyncProtocol
from highway_sdk.core.client import AioTCPClient
from .spec import SanSiFrameReq, SanSiFrameResp, SanSiMsgBuilder
from highway_sdk.core.exceptions import (
    CrcValidationError,
    ConnectionLostError,
    HostResponseTimeoutError,
    HostResponseIncompleteError,
)


class VmsSanSiClient(AioTCPClient):
    """VMS SANSI 客户端

    通信协议 V7.0.18
    播放表格式 V4.8


    Args:
        AioTCPClient (_type_): _description_
    """

    async def request(self, msg: SanSiFrameReq) -> SanSiFrameResp:
        """请求-响应

        按照时序同步

        Args:
            msg (SanSiFrameReq): _description_

        Raises:
            ConnectionLostError: _description_
            HostResponseTimeoutError: _description_
            HostResponseIncompleteError: _description_
            CrcValidationError: _description_

        Returns:
            SanSiFrameResp: _description_
        """
        async with self._lock:  # 支持协程并发
            if not self.is_connected:
                raise ConnectionLostError("connection lost")

            assert self._writer is not None and self._reader is not None

            self._writer.write(bytes(msg))
            await self._writer.drain()

            coro = self._reader.read(self._bufsize)

            try:
                resp = await asyncio.wait_for(coro, self._timeout)
            except asyncio.TimeoutError:
                raise HostResponseTimeoutError("Host response timeout")
            except asyncio.IncompleteReadError:
                raise HostResponseIncompleteError("Host response incomplete")

            try:
                frame = SanSiFrameResp.unpack(resp)
            except ValueError as e:
                raise CrcValidationError(e)

            return frame

    async def download_file(self, file_name: str = "play.lst") -> SanSiFrameResp:
        """下载播放表，可以下载当前播放表

        send:
        02 30 30 30 39 70 6C 61 79 2E 6C 73 74 00 00 00 00 57 2A 03
        recv:
        02 30 31 5B 70 6C 61 79 6C 69 73 74 5D 0D 0A 6E 77 69 6E 64 6F 77 73 3D 32 0D 0A 77 69 6E 64 6F 77 73 30 5F 78 3D 30 0D 0A 77 69 6E 64 6F 77 73 30 5F 79 3D 30 0D 0A 77 69 6E 64 6F 77 73 30 5F 77 3D 35 31 32 0D 0A 77 69 6E 64 6F 77 73 30 5F 68 3D 33 30 30 0D 0A 69 74 65 6D 5F 6E 6F 3D 32 0D 0A 69 74 65 6D 30 3D 33 30 30 2C 31 2C 30 2C 5C 42 30 30 38 0D 0A 69 74 65 6D 31 3D 33 30 30 2C 31 2C 30 2C 5C 42 30 30 39 0D 0A 77 69 6E 64 6F 77 73 31 5F 78 3D 30 0D 0A 77 69 6E 64 6F 77 73 31 5F 79 3D 33 30 30 0D 0A 77 69 6E 64 6F 77 73 31 5F 77 3D 35 31 32 0D 0A 77 69 6E 64 6F 77 73 31 5F 68 3D 38 34 0D 0A 77 69 6E 64 6F 77 73 31 5F 69 74 65 6D 5F 6E 6F 3D 31 0D 0A 77 69 6E 64 6F 77 73 31 5F 69 74 65 6D 30 3D 35 30 30 2C 31 2C 30 2C 5C 66 73 33 32 33 32 5C 63 32 35 35 32 35 35 30 30 30 30 30 30 B8 DF CB D9 B9 AB C2 B7 20 D1 CF BD FB C4 E6 D0 D0 0D 0A 43 D8 03


        Returns:
            SanSiFrameResp: _description_
        """
        return await self.request(msg=SanSiMsgBuilder.build_download_file(file_name))

    async def get_item(self) -> SanSiFrameResp:
        """获取当前播放项

        send:
        02 30 30 39 37 10 F5 03
        recv:
        02 30 31 30 30 30 30 30 35 30 30 30 31 30 30 30 30 30 5C 66 73 32 34 32 34 5C 63 30 30 30 32 35 35 30 30 30 30 30 30 CB ED B5 C0 C2 B7 B6 CE 5C 6E BD F7 C9 F7 BC DD CA BB E7 4F 03


        Returns:
            SanSiFrameResp: _description_
        """
        return await self.request(msg=SanSiMsgBuilder.build_get_item())

    async def upload_file(self, content: str, file_name: str = "play.lst"):
        """上载文件，可以直接修改当前播放表

        send:
        02 30 30 31 30 70 6C 61 79 2E 6C 73 74 2B 00 00 00 00 5B 70 6C 61 79 6C 69 73 74 5D 0D 0A 6E 77 69 6E 64 6F 77 73 3D 32 0D 0A 77 69 6E 64 6F 77 73 30 5F 78 3D 30 0D 0A 77 69 6E 64 6F 77 73 30 5F 79 3D 30 0D 0A 77 69 6E 64 6F 77 73 30 5F 77 3D 35 31 32 0D 0A 77 69 6E 64 6F 77 73 30 5F 68 3D 33 30 30 0D 0A 69 74 65 6D 5F 6E 6F 3D 32 0D 0A 69 74 65 6D 30 3D 33 30 30 2C 31 2C 30 2C 5C 42 30 30 38 0D 0A 69 74 65 6D 31 3D 33 30 30 2C 31 2C 30 2C 5C 42 30 30 39 0D 0A 77 69 6E 64 6F 77 73 31 5F 78 3D 30 0D 0A 77 69 6E 64 6F 77 73 31 5F 79 3D 33 30 30 0D 0A 77 69 6E 64 6F 77 73 31 5F 77 3D 35 31 32 0D 0A 77 69 6E 64 6F 77 73 31 5F 68 3D 38 34 0D 0A 77 69 6E 64 6F 77 73 31 5F 69 74 65 6D 5F 6E 6F 3D 31 0D 0A 77 69 6E 64 6F 77 73 31 5F 69 74 65 6D 30 3D 35 30 30 2C 31 2C 30 2C 5C 66 73 33 32 33 32 5C 63 32 35 35 32 35 35 30 30 30 30 30 30 B8 DF CB D9 B9 AB C2 B7 20 D1 CF BD FB C4 E6 D0 D0 0D 0A EF BD 03
        recv:
        02 30 31 30 C5 52 03

        Returns:
            SanSiFrameResp: _description_
        """
        return await self.request(
            msg=SanSiMsgBuilder.build_upload_file(content, file_name)
        )

    async def set_brightness(self, brightness: int) -> SanSiFrameResp:
        """设置亮度

        send:
        02 30 30 30 35 31 35 31 35 31 35 5E A0 03
        recv:
        02 30 31 30 C5 52 03

        Args:
            brightness (int): _description_

        Returns:
            SanSiFrameResp: _description_
        """
        return await self.request(msg=SanSiMsgBuilder.build_set_brightness(brightness))

    async def get_brightness(self) -> SanSiFrameResp:
        """获取亮度

        send:
        02 30 30 30 36 BA 4C 03
        recv:
        02 30 31 31 31 35 F4 74 03

        Returns:
            SanSiFrameResp: _description_
        """
        return await self.request(msg=SanSiMsgBuilder.build_get_brightness())


class VmsSanSiClientProtocol(TcpClientSyncProtocol):
    pass
