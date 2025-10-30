from dataclasses import dataclass
import struct


@dataclass
class DianMingPacket:
    """
    帧格式：【起始符1B】【目的地址2B】【源地址2B】【控制码2B】【数据nB】【校验码2B】【结束符1B】
    注：
    1. 校验码校验范围：目的地址，源地址，控制码，数据；发送时先校验后转义，接受时先转义后校验
    """

    what: bytes
    data: bytes
    crc: bytes
    start: bytes = b"\x02"
    dst_addr: bytes = b"\x30\x30"
    src_addr: bytes = b"\x30\x31"
    end: bytes = b"\x03"

    @classmethod
    def pack(cls, what: bytes, data: bytes, **kwargs) -> bytes:
        """
        打包
        :param what: 控制码
        :param data: 数据
        :param kwargs:
        :return:
        """
        if "dst_addr" in kwargs:
            cls.dst_addr = kwargs["dst_addr"]
        if "src_addr" in kwargs:
            cls.src_addr = kwargs["src_addr"]

        to_check = cls.dst_addr
        to_check += cls.src_addr
        to_check += what
        to_check += data

        crc_16 = DianMingCrc(to_check).crc()
        out_buffer = cls.start
        out_buffer += DianMingEscape(to_check + crc_16).byte_to_short()
        out_buffer += cls.end

        return out_buffer

    @classmethod
    def unpack(cls, message: bytes) -> "DianMingPacket":
        """
        解包
        :param message:
        :return:
        """
        dst_src_what_data_and_crc = DianMingEscape(message[1:-1]).short_to_byte()
        start = message[:1]
        end = message[-1:]
        crc = dst_src_what_data_and_crc[-2:]
        dst_src_what_and_data = dst_src_what_data_and_crc[:-2]

        crc_16 = DianMingCrc(dst_src_what_and_data).crc()
        if crc_16 != crc:
            raise ValueError("crc check failed")
        else:
            dst_addr = dst_src_what_and_data[:2]
            src_addr = dst_src_what_and_data[2:4]
            what = dst_src_what_and_data[4:6]
            data = dst_src_what_and_data[6:]

        return cls(
            start=start,
            dst_addr=dst_addr,
            src_addr=src_addr,
            what=what,
            data=data,
            crc=crc,
            end=end,
        )


class DianMingCrc:
    """英沙crc校验类"""

    crc_table = [
        0x0000,
        0x1021,
        0x2042,
        0x3063,
        0x4084,
        0x50A5,
        0x60C6,
        0x70E7,
        0x8108,
        0x9129,
        0xA14A,
        0xB16B,
        0xC18C,
        0xD1AD,
        0xE1CE,
        0xF1EF,
        0x1231,
        0x0210,
        0x3273,
        0x2252,
        0x52B5,
        0x4294,
        0x72F7,
        0x62D6,
        0x9339,
        0x8318,
        0xB37B,
        0xA35A,
        0xD3BD,
        0xC39C,
        0xF3FF,
        0xE3DE,
        0x2462,
        0x3443,
        0x0420,
        0x1401,
        0x64E6,
        0x74C7,
        0x44A4,
        0x5485,
        0xA56A,
        0xB54B,
        0x8528,
        0x9509,
        0xE5EE,
        0xF5CF,
        0xC5AC,
        0xD58D,
        0x3653,
        0x2672,
        0x1611,
        0x0630,
        0x76D7,
        0x66F6,
        0x5695,
        0x46B4,
        0xB75B,
        0xA77A,
        0x9719,
        0x8738,
        0xF7DF,
        0xE7FE,
        0xD79D,
        0xC7BC,
        0x48C4,
        0x58E5,
        0x6886,
        0x78A7,
        0x0840,
        0x1861,
        0x2802,
        0x3823,
        0xC9CC,
        0xD9ED,
        0xE98E,
        0xF9AF,
        0x8948,
        0x9969,
        0xA90A,
        0xB92B,
        0x5AF5,
        0x4AD4,
        0x7AB7,
        0x6A96,
        0x1A71,
        0x0A50,
        0x3A33,
        0x2A12,
        0xDBFD,
        0xCBDC,
        0xFBBF,
        0xEB9E,
        0x9B79,
        0x8B58,
        0xBB3B,
        0xAB1A,
        0x6CA6,
        0x7C87,
        0x4CE4,
        0x5CC5,
        0x2C22,
        0x3C03,
        0x0C60,
        0x1C41,
        0xEDAE,
        0xFD8F,
        0xCDEC,
        0xDDCD,
        0xAD2A,
        0xBD0B,
        0x8D68,
        0x9D49,
        0x7E97,
        0x6EB6,
        0x5ED5,
        0x4EF4,
        0x3E13,
        0x2E32,
        0x1E51,
        0x0E70,
        0xFF9F,
        0xEFBE,
        0xDFDD,
        0xCFFC,
        0xBF1B,
        0xAF3A,
        0x9F59,
        0x8F78,
        0x9188,
        0x81A9,
        0xB1CA,
        0xA1EB,
        0xD10C,
        0xC12D,
        0xF14E,
        0xE16F,
        0x1080,
        0x00A1,
        0x30C2,
        0x20E3,
        0x5004,
        0x4025,
        0x7046,
        0x6067,
        0x83B9,
        0x9398,
        0xA3FB,
        0xB3DA,
        0xC33D,
        0xD31C,
        0xE37F,
        0xF35E,
        0x02B1,
        0x1290,
        0x22F3,
        0x32D2,
        0x4235,
        0x5214,
        0x6277,
        0x7256,
        0xB5EA,
        0xA5CB,
        0x95A8,
        0x8589,
        0xF56E,
        0xE54F,
        0xD52C,
        0xC50D,
        0x34E2,
        0x24C3,
        0x14A0,
        0x0481,
        0x7466,
        0x6447,
        0x5424,
        0x4405,
        0xA7DB,
        0xB7FA,
        0x8799,
        0x97B8,
        0xE75F,
        0xF77E,
        0xC71D,
        0xD73C,
        0x26D3,
        0x36F2,
        0x0691,
        0x16B0,
        0x6657,
        0x7676,
        0x4615,
        0x5634,
        0xD94C,
        0xC96D,
        0xF90E,
        0xE92F,
        0x99C8,
        0x89E9,
        0xB98A,
        0xA9AB,
        0x5844,
        0x4865,
        0x7806,
        0x6827,
        0x18C0,
        0x08E1,
        0x3882,
        0x28A3,
        0xCB7D,
        0xDB5C,
        0xEB3F,
        0xFB1E,
        0x8BF9,
        0x9BD8,
        0xABBB,
        0xBB9A,
        0x4A75,
        0x5A54,
        0x6A37,
        0x7A16,
        0x0AF1,
        0x1AD0,
        0x2AB3,
        0x3A92,
        0xFD2E,
        0xED0F,
        0xDD6C,
        0xCD4D,
        0xBDAA,
        0xAD8B,
        0x9DE8,
        0x8DC9,
        0x7C26,
        0x6C07,
        0x5C64,
        0x4C45,
        0x3CA2,
        0x2C83,
        0x1CE0,
        0x0CC1,
        0xEF1F,
        0xFF3E,
        0xCF5D,
        0xDF7C,
        0xAF9B,
        0xBFBA,
        0x8FD9,
        0x9FF8,
        0x6E17,
        0x7E36,
        0x4E55,
        0x5E74,
        0x2E93,
        0x3EB2,
        0x0ED1,
        0x1EF0,
    ]

    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def crc(self) -> bytes:
        crc = 0
        for i in range(len(self._payload)):
            crc = self.crc_table[((crc >> 8) ^ self._payload[i]) & 0xFF] ^ (crc << 8)
            # 强制让crc符合unsigned short类型
            crc = crc & 0xFFFF
        return struct.pack(">H", crc)


class DianMingEscape:
    """
    对发送报文，接受报文进行转义
    """

    def __init__(self, payload: bytes) -> None:
        self._payload: bytes = payload

    def byte_to_short(self) -> bytes:
        escaped = self._payload
        escaped = escaped.replace(b"\x1b", b"\x1b\x00")
        escaped = escaped.replace(b"\x02", b"\x1b\xe7")
        escaped = escaped.replace(b"\x03", b"\x1b\xe8")

        return escaped

    def short_to_byte(self) -> bytes:
        escaped = self._payload
        escaped = escaped.replace(b"\x1b\xe7", b"\x02")
        escaped = escaped.replace(b"\x1b\xe8", b"\x03")
        escaped = escaped.replace(b"\x1b\x00", b"\x1b")

        return escaped


@dataclass(frozen=True)
class DianMingWhat:
    """
    指令码
    """

    # 获取当前内容
    GET_NOW_PLAY_CONTENT_REQ = b"\x37\x33"
    GET_NOW_PLAY_CONTENT_RSP = b"\x37\x34"

    # 获取播放列表
    GET_NOW_ALL_PLAY_CONTENT_REQ = b"\x35\x37"
    GET_NOW_PLAY_ALL_CONTENT_RSP = b"\x35\x38"

    # 播放列表下发并立即显示
    SET_PLAY_LIST_AND_PLAY_REQ = b"\x37\x31"
    SET_PLAY_LIST_AND_PLAY_RSP = b"\x37\x32"


@dataclass(frozen=True)
class DianMingCode:
    SUCCESS: bytes = b"1"
    FAILURE: bytes = b"0"


# ==============================================================================
# 报文类
# ==============================================================================
class DianMingMsgBuilder:
    """电明报文类"""

    encoding: str = "gbk"

    @classmethod
    def build_set_play_list(cls, content: str, play_id: int = 0):
        """播放列表下发并立即显示

        Args:
            content (str): _description_
            play_id (int, optional): _description_. Defaults to 0.
        """
        file_name = f"play{play_id:02d}.lst"

        # 文件下载项，默认
        data = b"\x2b"
        # 文件偏移地址，默认
        data += b"\x30\x30\x30\x30\x30\x30\x30\x30"
        data += file_name.encode(cls.encoding)
        data += content.encode(cls.encoding)

        return DianMingPacket.pack(
            what=DianMingWhat.SET_PLAY_LIST_AND_PLAY_REQ, data=data
        )

    @classmethod
    def build_get_now_play_content(cls):
        return DianMingPacket.pack(what=DianMingWhat.GET_NOW_PLAY_CONTENT_REQ, data=b"")

    @classmethod
    def build_get_now_play_all_content(cls, play_id: int = 0):
        data = b"\x30\x30\x30\x30\x30\x30\x30\x30"
        data += f"play{play_id:02d}.lst".encode(cls.encoding)  # 写死
        return DianMingPacket.pack(
            what=DianMingWhat.GET_NOW_ALL_PLAY_CONTENT_REQ, data=data
        )
