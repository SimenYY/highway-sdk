from typing import Optional
from highway_sdk.core.clients import TcpClient
from highway_sdk.core.exceptions import CrcValidationError, ResponseError
from highway_sdk.driver.vms.xianke.v1_4_2.spec import XianKeCode, XianKeMsg, XianKePacket, XianKeWhat


class VmsXianKeClient(TcpClient):
    """VMS XIANKE V1.4.2 客户端

    Args:
        TcpClient (_type_): _description_
    """

    chunk_size: int = 2**11  # 2K

    max_retries: int = 3
    
    #-----------------------------------------------------------------------------
    # 异步
    #-----------------------------------------------------------------------------
    async def arequest(self, data: Optional[bytes], rsp_what: bytes, rsp_len: int = 0):
        if data is not None:
            await self.asend(data)
        
        if rsp_len > 0:
            res = await self.arecv(rsp_len, is_exactly=True)
        else:
            res = await self.arecv()
            
        try:
            p = XianKePacket.unpack(res)
        except ValueError as e:
            raise CrcValidationError(str(e))

        if p.what != rsp_what:
            raise ResponseError("what error")

        return p
    async def aupload_file(self, content: str, file_path: str = "list\\000.xkl"):
        """上传文件

        帧数据，字节长度范围[0,2048]若总数据长度正好是 2048 的整数倍，
        那么数据部分在分多帧发送完毕后，还需再发送数据内容为 0 个字节的一
        帧数据，以确认数据传输完毕无误。

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
            rsp = await self.arequest(
                data=XianKeMsg.make_upload_file(chunk, file_path),
                rsp_what=XianKeWhat.UPLOAD_FILE,
                rsp_len=9
            )
            if rsp.data == XianKeCode.FAILURE:
                raise ResponseError("文件块上传异常")
        
    async def aplay_playlist(self, file_name: str = "000.xkl"):
        """设置显示的播放表

        Args:
            file_name (str): _description_. Defaults to "000.xkl".
        """
        rsp = await self.arequest(
            data=XianKeMsg.make_play_playlist(file_name),
            rsp_what=XianKeWhat.PLAY_LIST,
            rsp_len=9
        )
        if rsp.data == XianKeCode.FAILURE:
            raise ResponseError(f"{file_name} 播放表设置异常")
        
    #-----------------------------------------------------------------------------
    # 同步
    #-----------------------------------------------------------------------------
    def upload_file(self, content: str, file_path: str = "list\\000.xkl") -> None:
        if self._sync_loop is None:
            raise RuntimeError("Use sync_connect() to initialize sync client")
        return self._sync_loop.run_until_complete(self.aupload_file(content, file_path))
    
    def play_playlist(self, file_name: str = "000.xkl"):
        if self._sync_loop is None:
            raise RuntimeError("Use sync_connect() to initialize sync client")
        return self._sync_loop.run_until_complete(self.aplay_playlist(file_name))    
        
