import asyncio
from highway_sdk.core.client import AioTCPClient, TCPClientSequenceDriverProtocol
from highway_sdk.core.exceptions import (
    CrcValidationError,
    ConnectionLostError,
    HostResponseTimeoutError,
)
from .spec import SanSiFrameResp, SanSiMessageFactory, SanSiWhat
from .parse import (
    SanSiGetItemParser,
    SanSiGetBrightnessParser,
    SanSiDownloadFileParser,
    SanSiMessageParser,
)


class VmsSanSiClient(AioTCPClient):
    """VMS SANSI 客户端

    通信协议 V7.0.18
    播放表格式 V4.8


    Args:
        AioTCPClient (_type_): _description_
    """

    async def request(
        self, what: bytes, *, timeout: float = 3.0, **kwargs
    ) -> SanSiFrameResp:
        """请求-响应

        Note:
            SteamReader不是协程安全的

        Args:
            msg (SanSiFrameReq): _description_

        Raises:
            ConnectionLostError: _description_
            HostResponseTimeoutError: _description_
            CrcValidationError: _description_

        Returns:
            SanSiFrameResp: _description_
        """
        if not self.is_connected:
            raise ConnectionLostError("connection lost")

        assert self._writer is not None and self._reader is not None

        message = bytes(SanSiMessageFactory.create(what, **kwargs))

        async with self._lock:
            self._writer.write(message)
            await self._writer.drain()

            coro = self._reader.read(self._bufsize)  # 不能协程并发
            try:
                resp = await asyncio.wait_for(coro, timeout)
            except asyncio.TimeoutError:
                raise HostResponseTimeoutError("Host response timeout")

        try:
            frame = SanSiFrameResp.unpack(resp)
        except ValueError as e:
            raise CrcValidationError(e)

        return frame

    async def get_item(self, **kwargs) -> SanSiFrameResp:
        """获取当前播放项

        send:
        02 30 30 39 37 10 F5 03

        recv:
        02 30 31 30 30 30 30 30 35 30 30 30 31 30 30 30 30 30 5C 66 73 32 34 32 34 5C 63 30 30 30 32 35 35 30 30 30 30 30 30 CB ED B5 C0 C2 B7 B6 CE 5C 6E BD F7 C9 F7 BC DD CA BB E7 4F 03


        Returns:
            SanSiFrameResp: _description_
        """
        return await self.request(SanSiWhat.GET_ITEM, **kwargs)

    async def get_brightness(self, **kwargs) -> SanSiFrameResp:
        """获取亮度

        send:
        02 30 30 30 36 BA 4C 03

        recv:
        02 30 31 31 31 35 F4 74 03

        Returns:
            SanSiFrameResp: _description_
        """
        return await self.request(SanSiWhat.GET_BRIGHTNESS, **kwargs)

    async def set_brightness(self, brightness: int, **kwargs) -> SanSiFrameResp:
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
        return await self.request(
            SanSiWhat.SET_BRIGHTNESS, brightness=brightness, **kwargs
        )

    async def upload_file(
        self, content: str, file_name: str = "play.lst", **kwargs
    ) -> SanSiFrameResp:
        """载文件，可以直接修改当前播放表

        send:
        02 30 30 31 30 70 6C 61 79 2E 6C 73 74 2B 00 00 00 00 5B 70 6C 61 79 6C 69 73 74 5D 0D 0A 6E 77 69 6E 64 6F 77 73 3D 32 0D 0A 77 69 6E 64 6F 77 73 30 5F 78 3D 30 0D 0A 77 69 6E 64 6F 77 73 30 5F 79 3D 30 0D 0A 77 69 6E 64 6F 77 73 30 5F 77 3D 35 31 32 0D 0A 77 69 6E 64 6F 77 73 30 5F 68 3D 33 30 30 0D 0A 69 74 65 6D 5F 6E 6F 3D 32 0D 0A 69 74 65 6D 30 3D 33 30 30 2C 31 2C 30 2C 5C 42 30 30 38 0D 0A 69 74 65 6D 31 3D 33 30 30 2C 31 2C 30 2C 5C 42 30 30 39 0D 0A 77 69 6E 64 6F 77 73 31 5F 78 3D 30 0D 0A 77 69 6E 64 6F 77 73 31 5F 79 3D 33 30 30 0D 0A 77 69 6E 64 6F 77 73 31 5F 77 3D 35 31 32 0D 0A 77 69 6E 64 6F 77 73 31 5F 68 3D 38 34 0D 0A 77 69 6E 64 6F 77 73 31 5F 69 74 65 6D 5F 6E 6F 3D 31 0D 0A 77 69 6E 64 6F 77 73 31 5F 69 74 65 6D 30 3D 35 30 30 2C 31 2C 30 2C 5C 66 73 33 32 33 32 5C 63 32 35 35 32 35 35 30 30 30 30 30 30 B8 DF CB D9 B9 AB C2 B7 20 D1 CF BD FB C4 E6 D0 D0 0D 0A EF BD 03

        recv:
        02 30 31 30 C5 52 03

        Args:
            content (str): _description_
            file_name (str, optional): _description_. Defaults to "play.lst".

        Returns:
            _type_: _description_
        """
        return await self.request(
            SanSiWhat.UPLOAD_FILE, content=content, file_name=file_name, **kwargs
        )

    async def download_file(
        self, file_name: str = "play.lst", **kwargs
    ) -> SanSiFrameResp:
        """下载播放表，可以下载当前播放表

        send:
        02 30 30 30 39 70 6C 61 79 2E 6C 73 74 00 00 00 00 57 2A 03

        recv:
        02 30 31 5B 70 6C 61 79 6C 69 73 74 5D 0D 0A 6E 77 69 6E 64 6F 77 73 3D 32 0D 0A 77 69 6E 64 6F 77 73 30 5F 78 3D 30 0D 0A 77 69 6E 64 6F 77 73 30 5F 79 3D 30 0D 0A 77 69 6E 64 6F 77 73 30 5F 77 3D 35 31 32 0D 0A 77 69 6E 64 6F 77 73 30 5F 68 3D 33 30 30 0D 0A 69 74 65 6D 5F 6E 6F 3D 32 0D 0A 69 74 65 6D 30 3D 33 30 30 2C 31 2C 30 2C 5C 42 30 30 38 0D 0A 69 74 65 6D 31 3D 33 30 30 2C 31 2C 30 2C 5C 42 30 30 39 0D 0A 77 69 6E 64 6F 77 73 31 5F 78 3D 30 0D 0A 77 69 6E 64 6F 77 73 31 5F 79 3D 33 30 30 0D 0A 77 69 6E 64 6F 77 73 31 5F 77 3D 35 31 32 0D 0A 77 69 6E 64 6F 77 73 31 5F 68 3D 38 34 0D 0A 77 69 6E 64 6F 77 73 31 5F 69 74 65 6D 5F 6E 6F 3D 31 0D 0A 77 69 6E 64 6F 77 73 31 5F 69 74 65 6D 30 3D 35 30 30 2C 31 2C 30 2C 5C 66 73 33 32 33 32 5C 63 32 35 35 32 35 35 30 30 30 30 30 30 B8 DF CB D9 B9 AB C2 B7 20 D1 CF BD FB C4 E6 D0 D0 0D 0A 43 D8 03


        Args:
            file_name (str, optional): _description_. Defaults to "play.lst".

        Returns:
            SanSiFrameResp: _description_
        """
        return await self.request(
            SanSiWhat.DOWNLOAD_FILE, file_name=file_name, **kwargs
        )


class VmsSanSiClientDriverProtocol(TCPClientSequenceDriverProtocol):
    parser: SanSiMessageParser = (
        SanSiMessageParser()
        | SanSiDownloadFileParser()
        | SanSiGetItemParser()
        | SanSiGetBrightnessParser()
    )

    async def read_get_item(self):
        """获取当前播放项"""
        what = SanSiWhat.GET_ITEM
        message = bytes(SanSiMessageFactory.create(what))
        resp = await self.request("get_item", message)
        return self.parser.parse(what, resp)

    async def read_get_brightness(self):
        """获取亮度"""
        what = SanSiWhat.GET_BRIGHTNESS
        message = bytes(SanSiMessageFactory.create(what))
        resp = await self.request("get_brightness", message)
        return self.parser.parse(what, resp)

    async def read_download_file(self, file_name: str = "play.lst"):
        """下载播放表，可以下载当前播放表"""
        what = SanSiWhat.DOWNLOAD_FILE
        message = bytes(SanSiMessageFactory.create(what, file_name=file_name))
        resp = await self.request("download_file", message)
        return self.parser.parse(what, resp)

    def write_set_brightness(self, brightness: int):
        """设置亮度"""
        message = bytes(
            SanSiMessageFactory.create(SanSiWhat.SET_BRIGHTNESS, brightness=brightness)
        )
        self.send(message)

    def write_upload_file(self, content: str, file_name: str = "play.lst"):
        """上载文件，可以直接修改当前播放表"""
        message = bytes(
            SanSiMessageFactory.create(
                SanSiWhat.UPLOAD_FILE, content=content, file_name=file_name
            )
        )
        self.send(message)

    def on_connected(self) -> None:
        self.add_interval_jobs(
            [self.read_download_file, self.read_get_item, self.read_get_brightness],
            delay_seconds=2.0,
        )

        if not self.scheduler.running:
            self.scheduler.start()

    def on_disconnected(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown()
