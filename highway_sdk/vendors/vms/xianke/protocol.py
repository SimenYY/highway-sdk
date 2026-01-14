from highway_sdk.core.base import BaseTags
from highway_sdk.core.protocols import DriverTCPClientProtocol

from .factory import FrameFactory
from .parser import Parser
from .spec import Frame, What


class VmsXiankeProtocol(DriverTCPClientProtocol):
    """VMS XianKe 客户端协议

    Example:
    >>> def on_data_received(self, data: bytes) -> None:
    ...    for message in self.reader.iter_read_between():
    ...        frame = Frame.from_bytes(message)
    ...        tags = self.parser.parse(What.GET_ITEM, frame)
    ...        # 额外处理tags

    """

    parser = Parser

    def get_play_item(self):
        """获取当前播放项

        发送：
        02 32 34 30 30 EB 22 03

        接受：
        02 32 34 30 30 01 34 2C 31 2C 30 2C 31 2C 31 2C 5C 43 30 30 30 30
        30 30 5C 49 30 30 30 3D B0 03

        """
        self.send(bytes(FrameFactory.get_play_item()))

    def get_play_list_name(self):
        """获取当前播放列表名称

        发送：
        02 32 33 30 30 6E B2 03

        接受：
        02 32 33 30 30 01 30 30 30 2E 78 6B 6C 22 45 03

        """
        self.send(bytes(FrameFactory.get_play_list_name()))

    def upload_file(self, content: str, file_name: str = "list\\000.xkl"):
        """上传文件

        发送：
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

        接受：
        02 32 30 30 30 01 B4 95 03
        """
        self.send(bytes(FrameFactory.upload_file(content, file_name)))

    def download_file(self, file_name: str = "list\\000.xkl"):
        """下载文件

        发送：
        02 32 31 30 30 30 31 32 6C 69 73 74 5C 30 30 30 2E 78 6B 6C 30 30
        30 30 3A 87 03

        接受：
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
        """
        self.send(bytes(FrameFactory.download_file(file_name)))

    def select_play_list(self, file_name: str = "000.xkl"):
        """播放列表
        此功能是用来设置要显示的节目列表的。在功能“20”成功后不会立即显示上传的节目列
        表，需要调用此指令来显示节目列表。

        发送：
        02 32 32 30 30 30 30 30 2E 78 6B 6C 7A 93 03

        接受：
        02 32 32 30 30 01 59 FD 03

        """
        self.send(bytes(FrameFactory.select_play_list(file_name)))

    def get_brightness_and_mode(self):
        """获取当前亮度

        发送：
        02 30 35 30 30 31 7A 03

        接受：
        02 30 35 30 30 01 31 30 30 30 30 30 30 30 30 10 40 03
        """
        self.send(bytes(FrameFactory.get_brightness_and_mode()))

    def on_data_fed(self) -> None:
        for message in self.reader.iter_read_between():
            try:
                frame = Frame.from_bytes(message)
                # 这里需要根据实际情况获取请求帧类型
                # 假设我们知道这是GET_ITEM请求的响应
                tags = self.parser.parse(What.GET_PLAY_ITEM, frame)
            except Exception as e:
                self.log.exception(f"数据解析异常：{e}, 报文：{message.hex(' ')}")
                return

            self.on_message_parsed(tags)

    def on_message_parsed(self, tags: BaseTags):
        """钩子函数：处理解析后的消息

        可以转发数据

        Args:
            tags (BaseTags): _description_
        """
        pass
