"""点明厂商协议模块。

该模块提供了点明VMS设备的TCP客户端协议实现。
"""

from highway_sdk.core.base import BaseTags
from highway_sdk.core.protocols import DriverTCPClientProtocol

from .factory import FrameFactory
from .parser import Parser
from .spec import Frame


class VmsDianMingProtocol(DriverTCPClientProtocol):
    """点明VMS客户端协议。

    该类实现了点明VMS设备的TCP通信协议，提供了获取播放项、
    获取播放列表、设置播放列表等功能。

    Examples:
        >>> def on_data_received(self, data: bytes) -> None:
        ...    for message in self.reader.iter_read_between():
        ...        packet = Frame.from_bytes(message)
        ...        tags = self.parser.parse(packet.what, packet.data)
        ...        # 额外处理tags
    """

    parser = Parser

    def get_brightness_and_mode(self):
        """获取亮度和控制亮度模式。

        发送：
            02 30 30 30 31 32 31 B8 9B 03

        接收：
            02 30 31 30 30 32 32 46 46 46 46 46 46 30 31 36 65 03
        """
        self.send(bytes(FrameFactory.get_brightness_and_mode()))

    def set_brightness_or_mode(self, brightness: int | None = None):
        """设置亮度或控制亮度模式。

        发送：
            02 30 30 30 31 32 33 46 46 46 46 46 46 0E 04 03

        接收：
            02 30 31 30 30 32 34 31 57 40 03
        """
        self.send(bytes(FrameFactory.set_brightness_or_mode(brightness)))

    def get_item(self):
        """获取当前播放项。

        发送：
            02 30 31 30 31 37 33 CD 7D 03

        接收：
            02 30 31 30 31 37 34 30 30 31 30 30 30 35 30 30 30 30 30 30 30 30 30 5C 43 30 30 30 30 30 30 5C 46 73 33 32 33 32 5C 54 32 35 35 32 35 35 30 30 30 30 30 30 5C 4B 30 30 30 30 30 30 30 30 30 30 30 30 5C 57 B0 B2 C8 AB B5 DA D2 BB 5C 41 D4 A4 B7 C0 CE AA D6 F7 61 81 03
        """
        self.send(bytes(FrameFactory.get_play_item()))

    def get_play_list(self, play_id: int = 0):
        """获取播放列表。

        Args:
            play_id: 播放列表ID，默认为0。

        发送：
            02 30 30 30 31 35 37 30 30 30 30 30 30 30 30 70 6C 61 79 30 30 2E 6C 73 74 BC 91 03

        接受：
            02 30 31 30 30 35 38 2B 30 30 30 30 30 30 30 30 70 6C 61 79 30 30 2E 6C 73 74 5B 50 4C 41 59 4C 49 53 54 5D 0D 0A 49 54 45 4D 5F 4E 4F 3D 30 30 33 0D 0A 49 54 45 4D 30 30 30 3D 35 30 2C 30 2C 30 2C 30 2C 30 2C 5C 43 30 30 30 30 30 30 5C 46 73 33 32 33 32 5C 54 30 30 30 32 35 35 30 30 30 30 30 30 5C 4B 30 30 30 30 30 30 30 30 30 30 30 30 5C 57 D2 D4 C8 CB CE AA B1 BE 5C 41 B9 D8 B0 AE C9 FA C3 FC 0D 0A 49 54 45 4D 30 30 31 3D 35 30 2C 30 2C 30 2C 30 2C 30 2C 5C 43 30 30 30 30 30 30 5C 46 73 33 32 33 32 5C 54 32 35 35 32 35 35 30 30 30 30 30 30 5C 4B 30 30 30 30 30 30 30 30 30 30 30 30 5C 57 B0 B2 C8 AB B5 DA D2 BB 5C 41 D4 A4 B7 C0 CE AA D6 F7 0D 0A 49 54 45 4D 30 30 32 3D 35 30 2C 30 2C 30 2C 30 2C 30 2C 5C 43 30 30 30 30 30 30 5C 46 73 33 32 33 32 5C 54 32 35 35 30 30 30 30 30 30 30 30 30 5C 4B 30 30 30 30 30 30 30 30 30 30 30 30 5C 57 D7 F1 D5 C2 CA D8 B7 A8 5C 41 B0 B2 C8 AB BC DD CA BB 0D 0A 7F 3C 03
        """
        self.send(bytes(FrameFactory.get_play_list(play_id)))

    def set_play_list(self, content: str, play_id: int = 0):
        """设置播放列表。

        Args:
            content: 播放列表内容。
            play_id: 播放列表ID，默认为0。
        """
        self.send(bytes(FrameFactory.set_play_list(content, play_id)))

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
                self.log.exception(f"数据解析异常：{e}, 帧数据：{frame.data.hex(' ')}")
                return

            self.on_message_parsed(tags)

    def on_message_parsed(self, tags: BaseTags):
        """钩子函数：处理解析后的消息。

        可以转发数据。

        Args:
            tags: 解析后的标签对象。
        """
        pass
