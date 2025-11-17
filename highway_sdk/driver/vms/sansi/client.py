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

        Returns:
            SanSiFrameResp: _description_
        """
        return await self.request(msg=SanSiMsgBuilder.build_download_file(file_name))

    async def get_item(self) -> SanSiFrameResp:
        """获取当前播放项

        Returns:
            SanSiFrameResp: _description_
        """
        return await self.request(msg=SanSiMsgBuilder.build_get_item())

    async def upload_file(self, content: str, file_name: str = "play.lst"):
        """上载文件，可以直接修改当前播放表

        Returns:
            SanSiFrameResp: _description_
        """
        return await self.request(
            msg=SanSiMsgBuilder.build_upload_file(content, file_name)
        )

    async def set_brightness(self, brightness: int) -> SanSiFrameResp:
        """设置亮度

        Args:
            brightness (int): _description_

        Returns:
            SanSiFrameResp: _description_
        """
        return await self.request(msg=SanSiMsgBuilder.build_set_brightness(brightness))

    async def get_brightness(self) -> SanSiFrameResp:
        """获取亮度

        Returns:
            SanSiFrameResp: _description_
        """
        return await self.request(msg=SanSiMsgBuilder.build_get_brightness())



class VmsSanSiClientProtocol(TcpClientSyncProtocol):
    pass