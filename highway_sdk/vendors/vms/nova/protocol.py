from highway_sdk.core.protocols import DriverTCPClientProtocol
from highway_sdk.core.base import BaseTags
from .factory import FrameFactory
from .parser import Parser
from .spec import Frame


class VmsNovaProtocol(DriverTCPClientProtocol):
    """VMS Nova 客户端协议

    Example:
        >>> def on_data_received(self, data: bytes) -> None:
        ...    for message in self.reader.iter_read_between():
        ...        packet = Frame.from_bytes(message)
        ...        tags = self.parser.parse(packet.what, packet.data)
        ...        # 额外处理tags

    """

    parser = Parser

    def get_play_item(self):
        """获取当前播放项"""
        self.send(bytes(FrameFactory.get_play_item()))

    def get_play_list(self):
        """获取当前播放列表"""
        self.send(bytes(FrameFactory.get_play_list()))

    def send_file_name(self, file_name: str = "play001.lst", block_size: int = 65535):
        """发送文件名"""
        self.send(bytes(FrameFactory.send_file_name(file_name, block_size)))

    def send_file_content(self, content: str, block_num: int = 1):
        """发送文件内容"""
        self.send(bytes(FrameFactory.send_file_content(content, block_num)))

    def select_play_list(self, playlist_id: int = 1):
        """指定播放列表播放"""
        self.send(bytes(FrameFactory.select_play_list(playlist_id)))

    def get_screen_size(self):
        """获取屏幕大小"""
        self.send(bytes(FrameFactory.get_screen_size()))

    def get_now_brightness(self):
        """获取当前亮度"""
        self.send(bytes(FrameFactory.get_now_brightness()))

    def on_data_fed(self) -> None:
        for message in self.reader.iter_read_between():
            try:
                packet = Frame.from_bytes(message)
            except Exception as e:
                self.log.exception(f"数据解包异常：{e}, 报文：{message.hex(' ')}")
                return

            try:
                tags = self.parser.parse(packet.what, packet.data)
            except Exception as e:
                self.log.exception(f"数据解析异常：{e}, 帧数据：{packet.data.hex(' ')}")
                return

            self.on_message_parsed(tags)

    def on_message_parsed(self, tags: BaseTags | dict):
        """钩子函数：处理解析后的消息

        可以转发数据

        Args:
            tags (BaseTags | dict): _description_
        """
        pass
