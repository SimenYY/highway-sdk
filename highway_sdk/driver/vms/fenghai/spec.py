from dataclasses import dataclass
from typing import Self

from highway_sdk.core.protocol import ETX, STX
from highway_sdk.driver.vms.sansi.spec import (
    SansiMessageFactory,
    SansiWhatEnum,
    SansiEscape,
    SansiCRC,
)
from highway_sdk.core.exceptions import CrcValidationError

# ==============================================================================
# 枚举&常量定义
# ==============================================================================
ENCODING = "gbk"

FenghaiWhatEnum = SansiWhatEnum


# ==============================================================================
# 帧格式
# ==============================================================================
@dataclass
class FenghaiFrame:
    """帧格式"""

    what: bytes
    data: bytes
    address: bytes
    crc: bytes
    start: bytes = STX
    end: bytes = ETX

    @classmethod
    def unpack(cls, message: bytes) -> Self:
        """解包

        :param message:
        :raise CrcError
        :return:
        """
        escaped = SansiEscape(message[1:-1]).short_to_byte()
        address = escaped[:2]
        what = escaped[2:4]
        data = escaped[4:-2]
        crc = escaped[-2:]

        crc_16 = SansiCRC(address + what + data).crc()
        if crc_16 != crc:
            raise CrcValidationError("crc check failed")

        return cls(address=address, what=what, data=data, crc=crc)

    @classmethod
    def pack(cls, what: bytes, data: bytes, address: bytes = b"\x00\x00") -> Self:
        crc = SansiCRC(address + what + data).crc()
        return cls(address=address, what=what, data=data, crc=crc)


# ==============================================================================
# Message
# ==============================================================================
FenghaiMessageFactory = SansiMessageFactory
