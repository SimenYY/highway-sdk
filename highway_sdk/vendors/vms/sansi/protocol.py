from highway_sdk.core.protocols import DriverTCPClientProtocol
from highway_sdk.core.base import BaseTags
from .factory import FrameFactory
from .parser import Parser
from .spec import Frame, What


class VmsSansiProtocol(DriverTCPClientProtocol):
    """VMS Sansi 客户端协议

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
        02 30 30 39 37 10 F5 03

        接受：
        02 30 31 30 30 30 30 30 35 30 30 30 31 30 30 30 30 30 5C 66 73 32 34 32 34 5C 63 30 30 30 32 35 35 30 30 30 30 30 30 CB ED B5 C0 C2 B7 B6 CE 5C 6E BD F7 C9 F7 BC DD CA BB E7 4F 03

        """
        self.send(bytes(FrameFactory.get_play_item()))

    def download_file(self, file_name: str = "play.lst"):
        """下载播放表

        发送：
        02 30 30 30 39 70 6C 61 79 2E 6C 73 74 00 00 00 00 57 2A 03

        接受：
        02 30 31 5B 70 6C 61 79 6C 69 73 74 5D 0D 0A 6E 77 69 6E 64 6F 77 73 3D 32 0D 0A 77 69 6E 64 6F 77 73 30 5F 78 3D 30 0D 0A 77 69 6E 64 6F 77 73 30 5F 79 3D 30 0D 0A 77 69 6E 64 6F 77 73 30 5F 77 3D 35 31 32 0D 0A 77 69 6E 64 6F 77 73 30 5F 68 3D 33 30 30 0D 0A 69 74 65 6D 5F 6E 6F 3D 32 0D 0A 69 74 65 6D 30 3D 33 30 30 2C 31 2C 30 2C 5C 42 30 30 38 0D 0A 69 74 65 6D 31 3D 33 30 30 2C 31 2C 30 2C 5C 42 30 30 39 0D 0A 77 69 6E 64 6F 77 73 31 5F 78 3D 30 0D 0A 77 69 6E 64 6F 77 73 31 5F 79 3D 33 30 30 0D 0A 77 69 6E 64 6F 77 73 31 5F 77 3D 35 31 32 0D 0A 77 69 6E 64 6F 77 73 31 5F 68 3D 38 34 0D 0A 77 69 6E 64 6F 77 73 31 5F 69 74 65 6D 5F 6E 6F 3D 31 0D 0A 77 69 6E 64 6F 77 73 31 5F 69 74 65 6D 30 3D 35 30 30 2C 31 2C 30 2C 5C 66 73 33 32 33 32 5C 63 32 35 35 32 35 35 30 30 30 30 30 30 B8 DF CB D9 B9 AB C2 B7 20 D1 CF BD FB C4 E6 D0 D0 0D 0A 43 D8 03
        """
        self.send(bytes(FrameFactory.download_file(file_name)))

    def get_brightness_and_mode(self):
        """获取亮度和控制亮度模式

        发送：
        02 30 30 30 36 BA 4C 03

        接受：
        02 30 31 31 31 35 F4 74 03

        """
        self.send(bytes(FrameFactory.get_brightness_and_mode()))

    def set_brightness(self, brightness: int):
        """设置亮度"""
        self.send(bytes(FrameFactory.set_brightness(brightness)))

    def upload_file(self, content: str, file_name: str = "play.lst"):
        """上传播放表

        发送：
        02 30 30 31 30 70 6C 61 79 2E 6C 73 74 2B 00 00 00 00 5B 70 6C 61 79 6C 69 73 74 5D 0D 0A 6E 77 69 6E 64 6F 77 73 3D 32 0D 0A 77 69 6E 64 6F 77 73 30 5F 78 3D 30 0D 0A 77 69 6E 64 6F 77 73 30 5F 79 3D 30 0D 0A 77 69 6E 64 6F 77 73 30 5F 77 3D 35 31 32 0D 0A 77 69 6E 64 6F 77 73 30 5F 68 3D 33 30 30 0D 0A 69 74 65 6D 5F 6E 6F 3D 32 0D 0A 69 74 65 6D 30 3D 33 30 30 2C 31 2C 30 2C 5C 42 30 30 38 0D 0A 69 74 65 6D 31 3D 33 30 30 2C 31 2C 30 2C 5C 42 30 30 39 0D 0A 77 69 6E 64 6F 77 73 31 5F 78 3D 30 0D 0A 77 69 6E 64 6F 77 73 31 5F 79 3D 33 30 30 0D 0A 77 69 6E 64 6F 77 73 31 5F 77 3D 35 31 32 0D 0A 77 69 6E 64 6F 77 73 31 5F 68 3D 38 34 0D 0A 77 69 6E 64 6F 77 73 31 5F 69 74 65 6D 5F 6E 6F 3D 31 0D 0A 77 69 6E 64 6F 77 73 31 5F 69 74 65 6D 30 3D 35 30 30 2C 31 2C 30 2C 5C 66 73 33 32 33 32 5C 63 32 35 35 32 35 35 30 30 30 30 30 30 B8 DF CB D9 B9 AB C2 B7 20 D1 CF BD FB C4 E6 D0 D0 0D 0A EF BD 03

        接受：
        02 30 31 30 C5 52 03

        """
        self.send(bytes(FrameFactory.upload_file(content, file_name)))

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
