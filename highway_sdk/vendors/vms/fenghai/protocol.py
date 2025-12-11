from highway_sdk.core.driver import (
    DriverTCPClientProtocol,
)
from highway_sdk.core.interface import BaseTags

from .parse import FenghaiMessageParser
from .spec import (
    FenghaiMsgDirector,
    FenghaiMsgDownLoadFileBuilder,
    FenghaiMsgGetBrightnessAndModeBuilder,
    FenghaiMsgGetItemBuilder,
    FenghaiMsgSetBrightnessBuilder,
    FenghaiMsgUploadFileBuilder,
)


class VmsFenghaiProtocol(DriverTCPClientProtocol):
    """VMS Fenghai 客户端 v1.31

    Example:
        >>> def on_data_received(self, data: bytes) -> None:
        ...    for message in self.reader.iter_read_between():
        ...        tags = self.parser.parse(self.parser.deserialize(message)
        ...        额外处理tags


    """

    parser = FenghaiMessageParser

    def read_get_item(self):
        """获取当前播放项

        发送：
        02 30 30 39 37 10 F5 03

        接收：
        02 30 30 39 37 30 30 31 30 33 30 30 30 30 31 30 30 30 30 30 3C CB ED B5 C0 C4 DA CA A9 B9 A4 BC F5 CB D9 C2 FD D0 D0 20 CF DE CB D9 33 30 6B 6D 2F 68 3E 00 13 C1 03
        """
        builder = FenghaiMsgGetItemBuilder()
        director = FenghaiMsgDirector(builder)
        message = bytes(director.get_result())
        self.send(message)

    def read_get_brightness_and_mode(self):
        """获取亮度和播放模式

        发送：
        02 30 30 30 36 BA 4C 03

        接收：
        02 30 30 30 36 30 30 31 36 78 CB 03
        """
        builder = FenghaiMsgGetBrightnessAndModeBuilder()
        director = FenghaiMsgDirector(builder)
        message = bytes(director.get_result())
        self.send(message)

    def read_download_file(self, file_name: str = "play.lst"):
        """获取播放表

        Args:
            file_name (str, optional): _description_. Defaults to "play.lst".
        """
        builder = FenghaiMsgDownLoadFileBuilder(file_name)
        director = FenghaiMsgDirector(builder)
        message = bytes(director.get_result())
        self.send(message)

    def write_set_brightness(self, brightness: int):
        builder = FenghaiMsgSetBrightnessBuilder(brightness)
        director = FenghaiMsgDirector(builder)
        message = bytes(director.get_result())
        self.send(message)

    def write_upload_file(self, content: str, file_name: str = "play.lst"):
        builder = FenghaiMsgUploadFileBuilder(content, file_name)
        director = FenghaiMsgDirector(builder)
        message = bytes(director.get_result())
        self.send(message)

    def on_data_received(self, data: bytes) -> None:
        for message in self.reader.iter_read_between():
            try:
                tags = self.parser.parse(message)
            except Exception as e:
                self.log.exception(f"数据解析异常：{e}")
            else:
                self.on_message_parsed(tags)

    def on_message_parsed(self, tags: BaseTags):
        """钩子函数：处理解析后的消息

        可以转发数据

        Args:
            tags (dict): _description_
        """
        ...
