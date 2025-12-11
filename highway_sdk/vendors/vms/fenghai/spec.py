from dataclasses import dataclass
import struct
from typing import Self

from highway_sdk.core.exceptions import CrcValidationError
from highway_sdk.vendors.vms.sansi.spec import (
    BaseSansiMsgReqBuilder,
    SansiCode,
    SansiMsgDirector,
    SansiMsgDownloadFileBuilder,
    SansiMsgGetBrightnessAndModeBuilder,
    SansiMsgGetItemBuilder,
    SansiMsgSetBrightnessBuilder,
    SansiMsgUploadFileBuilder,
    SansiWhatEnum,
    SansiReqFrame,
)

# ==============================================================================
# 枚举&常量定义
# ==============================================================================
ENCODING = "gbk"

FenghaiWhatEnum = SansiWhatEnum

FenghaiCode = SansiCode


# ==============================================================================
# 帧格式
# ==============================================================================
@dataclass(slots=True)
class FenghaiFrame(SansiReqFrame):
    """帧格式"""

    @classmethod
    def unpack(cls, message: bytes) -> Self:
        """解包

        :param message:
        :raise CrcError
        :return:
        """
        cls.validate_start_end(message)

        unescaped = cls.escape(message[1:-1], reverse=True)
        address = unescaped[:2]
        what = unescaped[2:4]
        data = unescaped[4:-2]
        crc = unescaped[-2:]

        crc_calc = cls.calc_crc(address + what + data)
        if crc_calc != crc:
            raise CrcValidationError("crc check failed")

        return cls(address=address, what=what, data=data, crc=crc)

    @classmethod
    def pack(
        cls, what: FenghaiWhatEnum, data: bytes, address: bytes = b"\x00\x00"
    ) -> Self:
        crc = cls.calc_crc(address + what.value + data)
        return cls(address=address, what=what.value, data=data, crc=crc)

    @classmethod
    def calc_crc(cls, payload: bytes):
        crc = 0x0000
        for byte in payload:
            crc ^= byte << 8
            for _ in range(8):
                crc = (crc << 1) ^ 0x1021 if (crc & 0x8000) else (crc << 1)
                crc &= 0xFFFF                       # 保持在 16 bit
        # 转成大端 bytes
        return crc.to_bytes(2, 'big')
                


# ==============================================================================
# Message
# ==============================================================================
class FenghaiMsgBuilderMixin:
    def build(self) -> FenghaiFrame:
        return FenghaiFrame.pack(**self.kwargs)  # type: ignore


class FenghaiMsgSetBrightnessBuilder(
    FenghaiMsgBuilderMixin, SansiMsgSetBrightnessBuilder
): ...


class FenghaiMsgGetBrightnessAndModeBuilder(
    FenghaiMsgBuilderMixin, SansiMsgGetBrightnessAndModeBuilder
): ...


class FenghaiMsgGetItemBuilder(FenghaiMsgBuilderMixin, SansiMsgGetItemBuilder): ...


class FenghaiMsgDownLoadFileBuilder(
    FenghaiMsgBuilderMixin, SansiMsgDownloadFileBuilder
):
    def set_data(self) -> Self:
        data = self.file_name.encode(ENCODING)
        data += b"+"
        data += b"\x00\x00\x00\x00"  # 文件指针偏移
        self.kwargs["data"] = data
        return self


class FenghaiMsgUploadFileBuilder(
    FenghaiMsgBuilderMixin, SansiMsgUploadFileBuilder
): ...


class FenghaiMsgDirector(SansiMsgDirector):
    """控制报文产生"""

    ...
