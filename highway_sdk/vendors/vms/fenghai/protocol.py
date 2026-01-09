from highway_sdk.core.protocols import (
    DriverTCPClientProtocol,
)
from highway_sdk.core.base import BaseTags
from .factory import FrameFactory
from .parser import Parser
from .spec import Frame


class VmsFenghaiProtocol(DriverTCPClientProtocol):
    """丰海VMS客户端协议。

    该类实现了丰海VMS设备的TCP通信协议，提供了获取播放项、
    获取播放列表、设置亮度、上传文件等功能。

    Examples:
        >>> def on_data_received(self, data: bytes) -> None:
        ...    for message in self.reader.iter_read_between():
        ...        tags = self.parser.parse(self.parser.deserialize(message))
        ...        # 额外处理tags
    """

    parser = Parser

    def get_play_item(self):
        """获取当前播放项。

        发送：
            02 00 00 39 37 F9 B9 03

        接收：
            02 00 00 39 37 30 30 30 30 30 33 30 30 30 31 30 30 30 30 30 3C D7 A2 D2 E2 B0 B2 C8 AB 3E 00 B2 E9 03
        """
        self.send(bytes(FrameFactory.get_play_item()))

    def get_brightness_and_mode(self):
        """获取亮度和播放模式。

        发送：
            02 00 00 30 36 53 00 03

        接收：
            02 00 00 30 36 30 30 31 35 57 F9 03
        """
        self.send(bytes(FrameFactory.get_birghtness_and_mode()))

    def download_file(self, file_name: str = "play.lst"):
        """获取播放表。

        Args:
            file_name: 文件名，默认为"play.lst"。

        发送：
            02 00 00 30 39 70 6C 61 79 2E 6C 73 74 2B 00 00 00 00 A3 44 03

        接收：
            02 00 00 30 39 30 6C 73 74 00 00 00 00 00 2B 00 00 00 00 5B 70 6C 61 79 6C 69 73 74 5D 0D 0A 69 74 65 6D 5F 6E 6F 3D 31 0D 0A 69 74 65 6D 30 3D 33 30 30 2C 31 2C 30 2C 5C 43 30 30 30 30 30 30 5C 63 32 35 35 30 30 30 30 30 30 30 30 30 5C 62 30 30 30 30 30 30 30 30 30 30 30 5C 66 73 32 34 32 34 D7 A2 D2 E2 B0 B2 C8 AB 0D 0A 2F 52 03
        """
        self.send(bytes(FrameFactory.download_file()))

    def set_brightness(self, brightness: int):
        """设置亮度。

        Args:
            brightness: 亮度值，范围0-31。
        """
        self.send(bytes(FrameFactory.set_brightness(brightness)))

    def upload_file(self, file_content: str, file_name: str = "play.lst"):
        """上载文件。

        Args:
            file_content: 文件内容。
            file_name: 文件名，默认为"play.lst"。
        """
        self.send(bytes(FrameFactory.upload_file(file_content, file_name)))

    def on_data_fed(self) -> None:
        """处理接收到的数据。

        该方法会自动解析接收到的帧数据，并调用on_message_parsed处理解析结果。
        """
        for message in self.reader.iter_read_between():
            try:
                frame = Frame.from_bytes(message)
            except Exception as e:
                self.log.exception(f"数据解包异常：{e}, 报文：{message.hex(' ')}")
                return

            try:
                tags = self.parser.parse(frame)
            except Exception as e:
                self.log.exception(
                    f"数据解析异常：{e}, 帧数据：{frame.model_dump(mode='json')}"
                )
                return

            self.on_message_parsed(tags)

    def on_message_parsed(self, tags: BaseTags):
        """钩子函数：处理解析后的消息。

        可以转发数据。

        Args:
            tags: 解析后的标签对象。
        """
        ...
