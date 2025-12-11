from highway_sdk.vendors.vms.sansi.parse import SansiMessageParser
from highway_sdk.core.exceptions import DeviceOperationError
from .spec import ENCODING, FenghaiFrame, FenghaiWhatEnum, FenghaiCode


class FenghaiMessageParser(SansiMessageParser):
    @classmethod
    def parse(cls, message: bytes):
        frame = FenghaiFrame.unpack(message)

        match frame.what:
            case FenghaiWhatEnum.GET_ITEM.value:
                return cls._extract_item_tags(frame.data)
            case FenghaiWhatEnum.GET_BRIGHTNESS_AND_MODE.value:
                return cls._extract_brightness_and_mode_tags(frame.data)
            case FenghaiWhatEnum.DOWNLOAD_FILE.value:
                return cls._extract_play_tags(frame.data)
            case _:
                raise ValueError(f"{frame.what} is not supported")

    @classmethod
    def _extract_play_tags(cls, data: bytes):
        if not data.startswith(FenghaiCode.SUCCESS.value):
            raise DeviceOperationError("Failed to get play list")

        return cls._parse_play(data[(data.find(b"+") + 4 + 1) :].decode(ENCODING))
