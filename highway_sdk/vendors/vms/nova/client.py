import logging
from typing import Optional
from highway_sdk.core.driver import TCPClient
from highway_sdk.core.exceptions import ResponseError, CrcValidationError
from highway_sdk.vendors.vms.nova.spec import (
    NovaCode,
    NovaMsg,
    NovaWhat,
    NovaPacket,
)

logger = logging.getLogger(__name__)


class VmsNovaClient(TCPClient):
    """VMS NOVA V3.11.5 客户端

    在线协议网址：https://docapi.vnnox.com/web/#/20?page_id=2289

    Args:
        TcpClient (_type_): _description_

    Returns:
        _type_: _description_
    """

    def __init__(
        self,
        host: str,
        port: int,
        *,
        buffer_size: int = 2**16,
        timeout: float = 10.0,
        chunk_size: int = 2**16 - 2,
        max_retries: int = 3,
    ):
        super().__init__(host, port, buffer_size=buffer_size, timeout=timeout)

        self.chunk_size = chunk_size  # 文件块
        self.max_retries = max_retries  # 文件块发送失败重试次数

    async def arequest(
        self, data: Optional[bytes], rsp_what: bytes, rsp_len: int = 0
    ) -> NovaPacket:
        """请求，返回原始响应

        如果data 为 None 则不发送数据，只接受响应

        如果是固定长度响应则获取固定长度，否则就尽可能多的获取返回响应
        通过响应码进行校验

        Args:
            data (bytes): _description_
            res_what (bytes): _description_
            res_len (int, optional): _description_. Defaults to -1.

        Raises:
            ResponseError: _description_

        Returns:
            _type_: _description_
        """

        if data is not None:
            await self.asend(data)

        if rsp_len > 0:
            res = await self.arecv(rsp_len, is_exactly=True)
        else:
            res = await self.arecv()

        try:
            p = NovaPacket.unpack(res)
        except ValueError as e:
            raise CrcValidationError(str(e))

        if p.what != rsp_what:
            raise ResponseError("what error")

        return p

    # -----------------------------------------------------------------------------
    # 异步方式
    # -----------------------------------------------------------------------------
    async def asend_file_name(self, file_name: str = "play001.lst"):
        """发送文件名

        指令 0x11 中的块大小表示下发文件内容时的 0x13 中数据内容的长度，该块大小
        可根据网络和串行通讯物理连接情况进行调整，但最大不能超过 65535 字节。这
        样，对于物理连接较好时，可以将小于 65535 字节的文件一次性下发。

        上位机发送内容：
        指令码：0x11，数据域内容：块大小 2B + 文件名 n B。（UTF8 格式）

        设备回复内容：
        指令码：0x12，数据域内容为执行结果：1B，1-成功，0-失败，2-文件已存在。

        Args:
            file_name (str): _description_
            block_size (int, optional): _description_. Defaults to 65535.

        Returns:
            _type_: _description_
        """

        rsp = await self.arequest(
            data=NovaMsg.make_send_file_name(file_name, self.chunk_size),
            rsp_what=NovaWhat.SEND_FILE_NAME_RSP,
            rsp_len=8,
        )

        if rsp.data == NovaCode.FAILURE:
            raise ResponseError("发送文件名失败")

    async def asend_file_content(self, content: str):
        """发送文件内容

        块号是从文件读出数据块（指定的块大小）的顺序号，编号从 1 开始连续编号，数
        据内容固定长度为指定的块大小。

        文件发送完毕的情况为，若发送的文件块大小小于指定块大小，则说明文件发送完
        毕。另外，若发送的最后一个块大小刚好等于指定块大小时，上位机需在下发一个
        空的数据块示文件下发完成，否则设备不会知道文件已经下发完成。

        文件下发时，先使用 0x11 命令下发文件名，收到 0x12 命令时，如果返回成功，
        再使用 0x13 命令下发文件内容，收到 0x14 的成功回应时，认为该块下发成功，
        否则需要重发该块，直到发完整个文件

        发送按序号发送文件块，发送失败时重试

        上位机发送内容：
        指令码：0x13；数据域内容：块号 2B + 数据内容。

        设备回复内容：
        指令码：0x14；数据域内容：块号 2B + 执行结果：1B，1-成功，0-失败，表示文件块传输结束
        指令码：0xF9: 数据域内容：1B，1-成功，0-失败，表示文件传输结束

        Args:
            content (str): _description_

        Returns:
            _type_: _description_
        """

        chunks = [
            content[i : i + self.chunk_size]
            for i in range(0, len(content), self.chunk_size)
        ]

        if (
            len(chunks[-1]) == self.chunk_size
        ):  # 如果最后一块文件块长度刚好等于block_size，则添加一个空块
            chunks.append("")

        for i, chunk in enumerate(chunks, start=1):
            retries = 0
            while retries < self.max_retries:
                rsp = await self.arequest(
                    data=NovaMsg.make_send_file_content(chunk, i),
                    rsp_what=NovaWhat.SEND_FILE_CONTENT_RSP,
                    rsp_len=10,
                )
                if rsp.data[-1:] == NovaCode.FAILURE:
                    retries += 1
                    continue
                else:
                    break

            if retries >= self.max_retries:
                raise ResponseError(
                    f"发送第{i}块文件块失败，块大小为{self.chunk_size}，最大重试次数为{self.max_retries}，请检查网络状况"
                )

        rsp = await self.arequest(
            data=None, rsp_what=NovaWhat.FILE_SEND_END_RSP, rsp_len=8
        )
        if rsp.data == NovaCode.FAILURE:
            raise ResponseError("文件发送结束失败")

    async def aplay_playlist(self, play_id: int = 1):
        """指定播放表播放

        Args:
            play_id (int, optional): _description_. Defaults to 1.

        Raises:
            ResponseError: _description_
        """
        rsp = await self.arequest(
            data=NovaMsg.make_play_playlist(play_id),
            rsp_what=NovaWhat.PLAY_PLAYLIST_RSP,
            rsp_len=8,
        )
        if rsp.data == NovaCode.FAILURE:
            raise ResponseError(f"指定播放文件(id={play_id})失败")

    async def aget_play(self):
        """获取当前播放表

        内容	              字节数   备注
        当前播放节目的列表编号	1	    0x01 代表 play001.lst
        当前播放节目的所有内容	N	    UTF8 编码，格式同附录的播放内容的单个 item 内所有内容

        Returns:
            _type_: _description_
        """
        rsp = await self.arequest(
            data=NovaMsg.make_get_play(),
            rsp_what=NovaWhat.GET_NOW_PLAY_ALL_CONTENT_RSP,
        )

        return rsp.data

    async def aget_item(self):
        """获取当前播放内容

        内容	       字节数	备注
        开关屏标志	    1	    1-表示开屏 2-表示关屏，关屏时以下内容无效
        播放类型标志    1	    1-列表播放
        播放列表号	    1	    当前播放的列表编号或测试编号
        内容头	       8	    [itemN]\r\n,N 为播放清单中 item 编号
        当前播放内容	n	    参见附录一 播放文件列表说明


        Returns:
            _type_: _description_
        """
        rsp = await self.arequest(
            data=NovaMsg.make_get_item(),
            rsp_what=NovaWhat.GET_NOW_PLAY_CONTENT_RSP,
        )
        return rsp.data

    async def aget_now_brightness(self):
        """获取当前亮度

        内容	       字节数	备注
        亮度控制模式	1	     0-获取亮度异常；
                                1-自动；
                                2-手动；
                                3-定时
        亮度值	       1        当前亮度值；当亮度控制模式获取失败时，无该值
        """
        rsp = await self.arequest(
            data=NovaMsg.make_get_now_brightness(),
            rsp_what=NovaWhat.GET_NOW_BRIGHTNESS_RSP,
        )
        if rsp.data[:1] == NovaCode.FAILURE:
            raise ResponseError("获取当前亮度异常")

        return rsp.data

    async def aget_screen_size(self):
        """获取屏幕分辨率

        内容	  字节数	备注
        显示屏宽	2	显示屏像素宽度，低字节在前，高字节在后
        显示屏高	2	显示屏像素高度，低字节在前，高字节在后

        Returns:
            _type_: _description_
        """
        rsp = await self.arequest(
            data=NovaMsg.make_get_screen_size(),
            rsp_what=NovaWhat.GET_SCREEN_SIZE_RSP,
            rsp_len=11,
        )
        return rsp.data

    # -----------------------------------------------------------------------------
    # 同步方式
    # -----------------------------------------------------------------------------
    def send_file_name(self, file_name: str = "play001.lst"):
        if self._sync_loop is None:
            raise RuntimeError("Use sync_connect() to initialize sync client")
        return self._sync_loop.run_until_complete(self.asend_file_name(file_name))

    def send_file_content(self, content: str):
        if self._sync_loop is None:
            raise RuntimeError("Use sync_connect() to initialize sync client")
        return self._sync_loop.run_until_complete(self.asend_file_content(content))

    def play_playlist(self, playlist_id: int = 1):
        if self._sync_loop is None:
            raise RuntimeError("Use sync_connect() to initialize sync client")
        return self._sync_loop.run_until_complete(self.aplay_playlist(playlist_id))

    def get_item(self):
        if self._sync_loop is None:
            raise RuntimeError("Use sync_connect() to initialize sync client")
        return self._sync_loop.run_until_complete(self.aget_item())

    def get_play(self):
        if self._sync_loop is None:
            raise RuntimeError("Use sync_connect() to initialize sync client")
        return self._sync_loop.run_until_complete(self.aget_play())

    def get_now_brightness(self):
        if self._sync_loop is None:
            raise RuntimeError("Use sync_connect() to initialize sync client")
        return self._sync_loop.run_until_complete(self.aget_now_brightness())

    def get_screen_size(self):
        if self._sync_loop is None:
            raise RuntimeError("Use sync_connect() to initialize sync client")
        return self._sync_loop.run_until_complete(self.aget_screen_size())

