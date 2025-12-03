from highway_sdk.driver.vms.sansi.parse import (
    SanSiGetItemParser,
    SanSiGetBrightnessParser,
    SanSiDownloadFileParser,
)
from highway_sdk.core.interface import BaseMessageChainParser
from .spec import FenghaiFrame, FenghaiWhatEnum, ENCODING


class FenghaiMessageParser(BaseMessageChainParser):
    """丰海报文默认解析器


    解析器是被驱动所依赖的，分为两部分：1、解包，2、业务解析

    Args:
        BaseMessageChainParser (_type_): _description_

    Returns:
        _type_: _description_
    """

    frame = FenghaiFrame

    def parse(self, frame: FenghaiFrame):
        if self._successor is not None:
            return self._successor.parse(frame)
        else:
            return frame

    def deserialize(self, message: bytes) -> FenghaiFrame:
        return self.frame.unpack(message)


class FenghaiGetItemParser(FenghaiMessageParser):
    def parse(self, frame: FenghaiFrame):
        if frame.what == FenghaiWhatEnum.GET_ITEM.value:
            data = frame.data[15:].decode(ENCODING)
            tags = SanSiGetItemParser._parse_media(data)
            tags.duration = int(int(data[3:8]) * 0.01)
            tags.screen_in = str(int(data[8:10]))
            tags.index = data[0:3]
            return tags
        return super().parse(frame)


class FenghaiGetBrightnessParser(FenghaiMessageParser):
    def parse(self, frame: FenghaiFrame):
        if frame.what == FenghaiWhatEnum.GET_BRIGHTNESS_AND_MODE.value:
            return SanSiGetBrightnessParser._parse_brightness_and_mode(frame.data)
        return super().parse(frame)


class FenghaiDownloadFileParser(FenghaiMessageParser):
    def parse(self, frame: FenghaiFrame):
        if frame.what == FenghaiWhatEnum.UPLOAD_FILE.value:
            return SanSiDownloadFileParser._parse_play(frame.data.decode(ENCODING))
        return super().parse(frame)
