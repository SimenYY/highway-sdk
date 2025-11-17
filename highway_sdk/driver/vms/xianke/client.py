import asyncio
from highway_sdk.core.client import AioTCPClient
from highway_sdk.core.exceptions import (
    CrcValidationError,
    ResponseError,
    ConnectionLostError,
    HostResponseTimeoutError,
    HostResponseIncompleteError,
    DeviceOperationError,
)
from .spec import (
    XianKeCode,
    XianKeMsgBuilder,
    XianKeFrame,
)


class VmsXianKeClient(AioTCPClient):
    """VMS XIANKE V1.4.2 客户端"""

    chunk_size: int = 2**11  # 2kb

    async def request(self, msg: XianKeFrame, resp_len: int = 0) -> XianKeFrame:
        """请求-响应

        Args:
            data (bytes): _description_
            rsp_what (bytes): _description_
            rsp_len (int, optional): _description_. Defaults to 0.

        Raises:
            ValueError: _description_
            ConnectionLostError: _description_
            CrcValidationError: _description_
            ResponseError: _description_

        Returns:
            XianKeFrame: _description_
        """
        if not self._writer or not self._reader:
            raise ConnectionLostError("connection lost")

        self._writer.write(bytes(msg))
        await self._writer.drain()

        if resp_len > 0:
            coro = self._reader.readexactly(resp_len)
        else:
            coro = self._reader.read(self._bufsize)

        try:
            resp = await asyncio.wait_for(coro, self._timeout)
        except asyncio.TimeoutError:
            raise HostResponseTimeoutError("Host response timeout")
        except asyncio.IncompleteReadError:
            raise HostResponseIncompleteError("Host response incomplete")

        try:
            frame = XianKeFrame.unpack(resp)
        except ValueError as e:
            raise CrcValidationError(e)

        if frame.what != msg.what:
            raise ResponseError("what error")

        return frame

    async def upload_file(self, content: str, file_name: str = "list\\000.xkl") -> None:
        """上传文件

        帧数据，字节长度范围[0,2048]若总数据长度正好是 2048 的整数倍，
        那么数据部分在分多帧发送完毕后，还需再发送数据内容为 0 个字节的一
        帧数据，以确认数据传输完毕无误。

        data组成：【reserved 1B】【文件帧标记 1B】【文件名长度 3B】【文件名 nB】【文件偏移地址 4B】【数据 nB】

        上位机发送
        02 32 30 30 30 31 30 30 31 32 6C 69 73 74 5C 30 30 30 2E 78 6B 6C
        30 30 30 30 5B 4C 49 53 54 5D 0D 0A 49 74 65 6D 43 6F 75 6E 74 3D 30
        30 32 0D 0A 49 74 65 6D 30 30 3D 32 2C 31 2C 30 2C 31 2C 31 2C 5C 43
        30 30 30 30 30 30 5C 46 73 33 32 5C 54 32 35 35 30 30 30 30 30 30 30
        30 30 5C 42 30 30 30 30 30 30 30 30 30 30 30 30 5C 55 C9 EE DB DA CF
        D4 BF C6 BF C6 BC BC D3 D0 CF DE B9 AB CB BE 0D 0A 49 74 65 6D 30 31
        3D 32 2C 31 2C 30 2C 31 2C 31 2C 5C 43 30 30 30 30 30 30 5C 46 73 33
        32 5C 54 30 30 30 32 35 35 30 30 30 30 30 30 5C 42 30 30 30 30 30 30
        30 30 30 30 30 30 5C 55 C9 EE DB DA CF D4 BF C6 BF C6 BC BC D3 D0 CF
        DE B9 AB CB BE 0D 0A 4D EF 03

        设备响应：
        02 32 30 30 30 01 B4 95 03

        Args:
            content (str): _description_
            file_path (str, optional): _description_. Defaults to "list\000.xkl".
        """
        chunks = [
            content[i : i + self.chunk_size]
            for i in range(0, len(content), self.chunk_size)
        ]
        if len(chunks[-1]) == self.chunk_size:
            chunks.append("")

        for chunk in chunks:
            resp = await self.request(
                msg=XianKeMsgBuilder.build_upload_file(chunk, file_name),
                resp_len=9,
            )
            if resp.data == XianKeCode.FAILURE:
                raise DeviceOperationError("upload file fail")

    async def play_list(self, file_name: str = "000.xkl") -> None:
        """指定显示播放列表

        上位机发送
        02 32 32 30 30 30 30 30 2E 78 6B 6C 7A 93 03

        设备回复
        02 32 32 30 30 01 59 FD 03

        Args:
            file_name (str, optional): _description_. Defaults to "000.xkl".

        Raises:
            ResponseError: _description_
        """
        resp = await self.request(
            msg=XianKeMsgBuilder.build_play_list(file_name),
            resp_len=9,
        )
        if resp.data == XianKeCode.FAILURE:
            raise DeviceOperationError(f"{file_name} play list fail")

    async def download_file(self, file_name: str = "list\\000.xkl") -> XianKeFrame:
        """下载文件

        data组成：【文件名长度 3B】【文件名 nB】【文件偏移地址 4B】

        上位机发送
        02 32 31 30 30 30 31 32 6C 69 73 74 5C 30 30 30 2E 78 6B 6C 30 30
        30 30 3A 87 03

        设备响应
        02 32 31 30 30 01 30 31 32 6C 69 73 74 5C 30 30 30 2E 78 6B 6C 30
        30 30 30 5B 4C 49 53 54 5D 0D 0A 49 74 65 6D 43 6F 75 6E 74 3D 30 30
        32 0D 0A 49 74 65 6D 30 30 3D 32 2C 31 2C 30 2C 31 2C 31 2C 5C 43 30
        30 30 30 30 30 5C 46 73 33 32 5C 54 32 35 35 30 30 30 30 30 30 30 30
        30 5C 42 30 30 30 30 30 30 30 30 30 30 30 30 5C 55 C9 EE DB DA CF D4
        BF C6 BF C6 BC BC D3 D0 CF DE B9 AB CB BE 0D 0A 49 74 65 6D 30 31 3D
        32 2C 31 2C 30 2C 31 2C 31 2C 5C 43 30 30 30 30 30 30 5C 46 73 33 32
        5C 54 30 30 30 32 35 35 30 30 30 30 30 30 5C 42 30 30 30 30 30 30 30
        30 30 30 30 30 5C 55 C9 EE DB DA CF D4 BF C6 BF C6 BC BC D3 D0 CF DE
        B9 AB CB BE 0D 0A F2 52 03


        Args:
            file_path (str, optional): _description_. Defaults to "list\000.xkl".

        Returns:
            bytes: _description_
        """
        return await self.request(
            msg=XianKeMsgBuilder.build_download_file(file_name),
        )

    async def get_play(self) -> XianKeFrame:
        """获取当前播放列表(只是文件名)

        上位机发送
        02 32 33 30 30 6E B2 03

        设备响应
        02 32 33 30 30 01 30 30 30 2E 78 6B 6C 22 45 03

        Returns:
            XianKeFrame: _description_
        """
        return await self.request(msg=XianKeMsgBuilder.build_get_play())

    async def get_item(self) -> XianKeFrame:
        """获取当前播放项

        上位机发送
        02 32 34 30 30 EB 22 03

        设备回复
        02 32 34 30 30 01 34 2C 31 2C 30 2C 31 2C 31 2C 5C 43 30 30 30 30
        30 30 5C 49 30 30 30 3D B0 03

        Returns:
            XianKeFrame: _description_
        """
        return await self.request(msg=XianKeMsgBuilder.build_get_item())

    async def get_brightness(self) -> XianKeFrame:
        """获取当前显示亮度

        上位机发送
        02 30 35 30 30 31 7A 03

        设备回复
        02 30 35 30 30 01 31 30 30 30 30 30 30 30 30 10 40 03

        Returns:
            XianKeFrame: _description_
        """
        return await self.request(
            msg=XianKeMsgBuilder.build_get_brightness(),
        )
