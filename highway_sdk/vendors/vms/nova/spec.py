from dataclasses import dataclass
import struct


@dataclass(frozen=True)
class NovaCode:
    """Nova返回码"""

    SUCCESS: bytes = b"\x01"
    FAILURE: bytes = b"\x00"


@dataclass(frozen=True)
class NovaWhat:
    """Nova指令码

    注：
    1. req表示发送，rsp表示回复

    """

    # 获取当前内容
    GET_NOW_PLAY_CONTENT_REQ = b"\x2d"
    GET_NOW_PLAY_CONTENT_RSP = b"\x2e"
    # 获取当前列表
    GET_NOW_PLAY_ALL_CONTENT_REQ = b"\x3a"
    GET_NOW_PLAY_ALL_CONTENT_RSP = b"\x3b"

    # 发送文件名
    SEND_FILE_NAME_REQ = b"\x11"
    SEND_FILE_NAME_RSP = b"\x12"

    # 发送文件内容
    SEND_FILE_CONTENT_REQ = b"\x13"
    SEND_FILE_CONTENT_RSP = b"\x14"

    # 文件发送完毕
    FILE_SEND_END_RSP = b"\xf9"

    # 指定文件名播放
    PLAY_PLAYLIST_REQ = b"\x1b"
    PLAY_PLAYLIST_RSP = b"\x1c"

    # 获取当前截图
    SCREENSHOT_REQ = b"\x80"
    SCREENSHOT_RSP = b"\x81"

    # 获取屏幕高宽
    GET_SCREEN_SIZE_REQ = b"\x82"
    GET_SCREEN_SIZE_RSP = b"\x83"

    # 获取当前亮度
    GET_NOW_BRIGHTNESS_REQ = b"\xc3"
    GET_NOW_BRIGHTNESS_RSP = b"\xc3"

    # 获取开关屏状态
    GET_SCREEN_SWITCH_STATUS_REQ = b"\xba"
    GET_SCREEN_SWITCH_STATUS_RSP = b"\xba"


class NovaEscape:
    """转义类"""

    def __init__(self, payload: bytes) -> None:
        self._payload: bytes = payload

    def byte_to_short(self) -> bytes:
        escaped = self._payload
        escaped = escaped.replace(b"\xee", b"\xee\x0e")
        escaped = escaped.replace(b"\xaa", b"\xee\x0a")
        escaped = escaped.replace(b"\xcc", b"\xee\x0c")

        return escaped

    def short_to_byte(self) -> bytes:
        escaped = self._payload
        escaped = escaped.replace(b"\xee\x0a", b"\xaa")
        escaped = escaped.replace(b"\xee\x0c", b"\xcc")
        escaped = escaped.replace(b"\xee\x0e", b"\xee")

        return escaped


@dataclass
class NovaPacket:
    """Nova报文格式

    Nova数据帧格式：【起始符 1B】-【设备地址 2B】-【指令码 1B】-【数据域 nB】-【结束符 1B】-【校验码 2B】

    注：
    1. 校验码为校验前面全部，包括起始符和结束符
    2. 设备地址默认为0xFFFF
    """

    what: bytes
    data: bytes
    crc: bytes
    address: bytes = b"\xff\xff"
    start: bytes = b"\xaa"
    end: bytes = b"\xcc"

    @classmethod
    def pack(cls, what: bytes, data: bytes, **kwargs) -> bytes:
        """打包函数

        :param what:
        :param data:
        :param kwargs:
        :return: bytes
        """
        if "address" in kwargs:
            cls.address = kwargs["address"]

        payload = cls.start
        payload += cls.address
        payload += what
        payload += NovaEscape(data).byte_to_short()
        payload += cls.end

        crc = NovaCrc(payload).crc()
        out_buffer = payload
        out_buffer += crc

        return out_buffer

    @classmethod
    def unpack(cls, message: bytes) -> "NovaPacket":
        """解包函数

        :raise CrcError
        :param message:
        :return: NovaPacket
        """
        address_what_and_data = message[1:-3]

        start = message[:1]
        end = message[-3:-2]
        crc = message[-2:]

        payload = start
        payload += address_what_and_data
        payload += end

        res = NovaCrc(payload).crc()

        if res != crc:
            raise ValueError("crc error")
        else:
            address_what_and_data = NovaEscape(address_what_and_data).short_to_byte()
            address = address_what_and_data[:2]
            what = address_what_and_data[2:3]
            data = address_what_and_data[3:]

        return cls(start=start, address=address, what=what, data=data, end=end, crc=crc)

    def __repr__(self) -> str:
        return f"NovaPacket(start={self.start.hex().upper()}, address={self.address.hex().upper()}, what={self.what.hex().upper()}, data={self.data.hex().upper()}, end={self.end.hex().upper()}, crc={self.crc.hex().upper()})"


class NovaCrc:
    """诺瓦crc校验类

    Returns:
        _type_: _description_
    """

    crc_table = [
        0x0000,
        0x1189,
        0x2312,
        0x329B,
        0x4624,
        0x57AD,
        0x6536,
        0x74BF,
        0x8C48,
        0x9DC1,
        0xAF5A,
        0xBED3,
        0xCA6C,
        0xDBE5,
        0xE97E,
        0xF8F7,
        0x1081,
        0x0108,
        0x3393,
        0x221A,
        0x56A5,
        0x472C,
        0x75B7,
        0x643E,
        0x9CC9,
        0x8D40,
        0xBFDB,
        0xAE52,
        0xDAED,
        0xCB64,
        0xF9FF,
        0xE876,
        0x2102,
        0x308B,
        0x0210,
        0x1399,
        0x6726,
        0x76AF,
        0x4434,
        0x55BD,
        0xAD4A,
        0xBCC3,
        0x8E58,
        0x9FD1,
        0xEB6E,
        0xFAE7,
        0xC87C,
        0xD9F5,
        0x3183,
        0x200A,
        0x1291,
        0x0318,
        0x77A7,
        0x662E,
        0x54B5,
        0x453C,
        0xBDCB,
        0xAC42,
        0x9ED9,
        0x8F50,
        0xFBEF,
        0xEA66,
        0xD8FD,
        0xC974,
        0x4204,
        0x538D,
        0x6116,
        0x709F,
        0x0420,
        0x15A9,
        0x2732,
        0x36BB,
        0xCE4C,
        0xDFC5,
        0xED5E,
        0xFCD7,
        0x8868,
        0x99E1,
        0xAB7A,
        0xBAF3,
        0x5285,
        0x430C,
        0x7197,
        0x601E,
        0x14A1,
        0x0528,
        0x37B3,
        0x263A,
        0xDECD,
        0xCF44,
        0xFDDF,
        0xEC56,
        0x98E9,
        0x8960,
        0xBBFB,
        0xAA72,
        0x6306,
        0x728F,
        0x4014,
        0x519D,
        0x2522,
        0x34AB,
        0x0630,
        0x17B9,
        0xEF4E,
        0xFEC7,
        0xCC5C,
        0xDDD5,
        0xA96A,
        0xB8E3,
        0x8A78,
        0x9BF1,
        0x7387,
        0x620E,
        0x5095,
        0x411C,
        0x35A3,
        0x242A,
        0x16B1,
        0x0738,
        0xFFCF,
        0xEE46,
        0xDCDD,
        0xCD54,
        0xB9EB,
        0xA862,
        0x9AF9,
        0x8B70,
        0x8408,
        0x9581,
        0xA71A,
        0xB693,
        0xC22C,
        0xD3A5,
        0xE13E,
        0xF0B7,
        0x0840,
        0x19C,
        0x2B52,
        0x3ADB,
        0x4E64,
        0x5FED,
        0x6D76,
        0x7CFF,
        0x9489,
        0x8500,
        0xB79B,
        0xA612,
        0xD2AD,
        0xC324,
        0xF1BF,
        0xE036,
        0x18C1,
        0x0948,
        0x3BD3,
        0x2A5A,
        0x5EE5,
        0x4F6C,
        0x7DF7,
        0x6C7E,
        0xA50A,
        0xB483,
        0x8618,
        0x9791,
        0xE32E,
        0xF2A7,
        0xC03C,
        0xD1B5,
        0x2942,
        0x38CB,
        0x0A50,
        0x1BD9,
        0x6F66,
        0x7EEF,
        0x4C74,
        0x5DFD,
        0xB58B,
        0xA402,
        0x9699,
        0x8710,
        0xF3AF,
        0xE226,
        0xD0BD,
        0xC134,
        0x39C3,
        0x284A,
        0x1AD1,
        0x0B58,
        0x7FE7,
        0x6E6E,
        0x5CF5,
        0x4D7C,
        0xC60C,
        0xD785,
        0xE51E,
        0xF497,
        0x8028,
        0x91A1,
        0xA33A,
        0xB2B3,
        0x4A44,
        0x5BCD,
        0x6956,
        0x78DF,
        0x0C60,
        0x1DE9,
        0x2F72,
        0x3EFB,
        0xD68D,
        0xC704,
        0xF59F,
        0xE416,
        0x90A9,
        0x8120,
        0xB3BB,
        0xA232,
        0x5AC5,
        0x4B4C,
        0x79D7,
        0x685E,
        0x1CE1,
        0x0D68,
        0x3FF3,
        0x2E7A,
        0xE70E,
        0xF687,
        0xC41C,
        0xD595,
        0xA12A,
        0xB0A3,
        0x8238,
        0x93B1,
        0x6B46,
        0x7ACF,
        0x4854,
        0x59DD,
        0x2D62,
        0x3CEB,
        0x0E70,
        0x1FF9,
        0xF78F,
        0xE606,
        0xD49D,
        0xC514,
        0xB1AB,
        0xA022,
        0x92B9,
        0x8330,
        0x7BC7,
        0x6A4E,
        0x58D5,
        0x495C,
        0x3DE3,
        0x2C6A,
        0x1EF1,
        0x0F78,
    ]

    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def crc(self) -> bytes:
        fcs = 0xFFFF
        for i in range(len(self._payload)):
            fcs = (fcs >> 8) ^ self.crc_table[(fcs ^ self._payload[i]) & 0xFF]

        return struct.pack("<H", fcs)


class NovaMsg:
    """Nova报文类

    Returns:
        _type_: _description_
    """

    encoding: str = "utf-8" 

    @classmethod
    def make_send_file_name(cls, file_name: str = "play001.lst", block_size: int = 65535) -> bytes:
        """发送文件名

        上位机发送：AA FF FF 11 FF FF 70 6C 61 79 30 30 31 2E 6C 73 74 CC 5A 9B
        设备回复：AA FF FF 12 01 CC A1 B4
        
        Args:
            file_name (str): _description_
            block_size (int, optional): _description_. Defaults to 65535.

        Returns:
            bytes: _description_
        """
        data = struct.pack("<H", block_size)
        data += file_name.encode(cls.encoding, "ignore")
        return NovaPacket.pack(NovaWhat.SEND_FILE_NAME_REQ, data)

    @classmethod
    def make_send_file_content(cls, content: str, block_num: int = 1) -> bytes:
        """发送文件内容

        上位机发送：AA FF FF 13 01 00 5B 61 6C 6C 5D 0D 0A 69 74 65 6D 73 3D 31 0D 0A 5B 69 74 65 6D 31 5D 0D 0A 70 61 72 61 6D 
        3D 31 30 30 2C 31 2C 31 2C 31 2C 30 2C 35 2C 31 0D 0A 74 78 74 65 78 74 31 3D 30 2C 30 2C 30 2C 32 38 30 2C 33 2C 34 38 
        34 38 2C 30 2C 30 2C 30 2C 31 2C 30 2C 31 2C 38 2C 30 2C 32 2C 31 30 30 2C 31 2C E9 A9 AC E5 B0 94 E5 BA B7 E6 AC A2 E8 
        BF 8E E6 82 A8 E3 80 82 2C 31 2C 31 2C 30 2C 35 2C 35 2C 35 CC 83 84
        
        设备回复：AA FF FF 14 01 00 01 CC 91 C4
        
        设备回复：AA FF FF F9 01 CC A6 94
        
        Args:
            content (str): _description_
            block_num (int, optional): _description_. Defaults to 1.

        Returns:
            bytes: _description_
        """
        data = struct.pack("<H", block_num)
        data += content.encode(cls.encoding, "ignore")
        return NovaPacket.pack(NovaWhat.SEND_FILE_CONTENT_REQ, data)

    @classmethod
    def make_play_playlist(cls, playlist_id: int = 1):
        """指定播放列表进行播放

        上位机发送：AA FF FF 1B 01 CC BF 28
        设备回复：AA FF FF 1C 01 CC BA A4
        
        Args:
            playlist_id (int, optional): _description_. Defaults to 1.

        Returns:
            _type_: _description_
        """
        data = struct.pack(">B", playlist_id)
        return NovaPacket.pack(NovaWhat.PLAY_PLAYLIST_REQ, data)

    @classmethod
    def make_get_item(cls) -> bytes:
        """获取当前播放项

        上位机发送：AA FF FF 2D CC EE 0A
        设备回复：AA FF FF 2E 01 01 01 5B 69 74 65 6D 31 5D 0A 70 61 72 61 6D 3D 31 30 30 2C 31 2C 31 2C 31 2C 30 2C 35 2C 31 2C 
        30 2C 31 0A 74 78 74 31 3D 31 30 2C 30 2C 33 2C 31 36 31 36 2C 31 2C 38 2C 30 2C E8 BD A6 E7 89 8C EF BC 9A E5 86 80 41 
        33 31 38 41 41 E5 A4 A7 E8 B4 A7 E8 BD A6 2C 31 39 32 2C 33 32 30 2C 30 0A 74 78 74 70 61 72 61 6D 31 3D 30 2C 30 CC 20 
        DF
        
        Returns:
            bytes: _description_
        """
        return NovaPacket.pack(what=NovaWhat.GET_NOW_PLAY_CONTENT_REQ, data=b"")

    @classmethod
    def make_get_play(cls) -> bytes:
        """获取当前播放表

        上位机发送：AA FF FF 3A CC 77 D2
        设备回复：AA FF FF 3B 01 5B 61 6C 6C 5D 0A 69 74 65 6D 73 3D 31 0A 5B 69 74 65 6D 31 5D 0A 70 61 72 61 6D 3D 31 30 30 2C
        31 2C 31 2C 31 2C 30 2C 35 2C 31 2C 30 2C 31 0A 74 78 74 31 3D 31 30 2C 30 2C 33 2C 31 36 31 36 2C 31 2C 38 2C 30 2C E8
        BD A6 E7 89 8C EF BC 9A E5 86 80 41 33 31 38 41 41 E5 A4 A7 E8 B4 A7 E8 BD A6 2C 31 39 32 2C 33 32 30 2C 30 0A 74 78 74
        70 61 72 61 6D 31 3D 30 2C 30 CC D9 25

        Returns:
            bytes: _description_
        """
        return NovaPacket.pack(what=NovaWhat.GET_NOW_PLAY_ALL_CONTENT_REQ, data=b"")

    @classmethod
    def make_get_screen_size(cls) -> bytes:
        """获取屏幕点阵大小

        上位机发送：AA FF FF 82 CC D9 26
        设备回复：AA FF FF 83 A0 02 C0 01 CC 05 20
        
        Returns:
            bytes: _description_
        """
        return NovaPacket.pack(what=NovaWhat.GET_SCREEN_SIZE_REQ, data=b"")

    @classmethod
    def make_get_now_brightness(cls) -> bytes:
        """获取当前亮度

        上位机发送: AA FF FF C3 CC 67 79
        设备回复: AA FF FF C3 02 FF CC 3A 2F

        Returns:
            bytes: _description_
        """
        return NovaPacket.pack(what=NovaWhat.GET_NOW_BRIGHTNESS_REQ, data=b"")
