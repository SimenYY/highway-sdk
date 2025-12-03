from highway_sdk.core.client import TCPClientDriverProtocol
from .parse import (
    FenghaiMessageParser,
    FenghaiGetItemParser,
    FenghaiGetBrightnessParser,
    FenghaiDownloadFileParser,
)
from .spec import FenghaiMessageFactory, FenghaiWhatEnum


class VmsFenghaiClientDriverProtocol(TCPClientDriverProtocol):
    """VMS Fenghai 客户端 v1.31

    Args:
        TCPClientDriverProtocol (_type_): _description_
    """

    parser: FenghaiMessageParser = (
        FenghaiMessageParser()
        | FenghaiGetItemParser()
        | FenghaiGetBrightnessParser()
        | FenghaiDownloadFileParser()
    )

    def on_data_received(self, data: bytearray) -> None:
        for message in self.reader.iter_read_between():
            self.parser.parse(self.parser.deserialize(message))

    def read_get_item(self):
        message = bytes(FenghaiMessageFactory.create(FenghaiWhatEnum.GET_ITEM.value))
        self.send(message)

    def read_get_brightness_and_mode(self):
        message = bytes(
            FenghaiMessageFactory.create(FenghaiWhatEnum.GET_BRIGHTNESS_AND_MODE.value)
        )
        self.send(message)

    def read_download_file(self, file_name: str = "play.lst"):
        message = bytes(
            FenghaiMessageFactory.create(
                FenghaiWhatEnum.DOWNLOAD_FILE.value, file_name=file_name
            )
        )
        self.send(message)

    def write_set_brightness(self, brightness: int):
        message = bytes(
            FenghaiMessageFactory.create(
                FenghaiWhatEnum.SET_BRIGHTNESS.value, brightness=brightness
            )
        )
        self.send(message)

    def write_upload_file(self, content: str, file_name: str = "play.lst"):
        message = bytes(
            FenghaiMessageFactory.create(
                FenghaiWhatEnum.UPLOAD_FILE.value, content=content, file_name=file_name
            )
        )
        self.send(message)

    def on_connected(self) -> None:
        self.add_interval_jobs(
            [
                self.read_download_file,
                self.read_get_brightness_and_mode,
                self.read_get_item,
            ],
            delay_seconds=2.0,
        )


class VmsFenghaiDriver:

    
    def run(self):
        pass
