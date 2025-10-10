from dataclasses import dataclass
import struct
from typing import Self


@dataclass
class YingShaFrame:
    """帧格式"""

    what: bytes
    data_len: bytes
    data: bytes
    crc: bytes
    address: bytes 
    start: bytes = b"\x02"
    end: bytes = b"\x03"

    @classmethod
    def pack(cls, what: bytes, data: bytes, address: bytes = b"\x30\x30") -> bytes:
        """打包函数

        Args:
            what (bytes): 帧类型
            data (bytes): 数据

        Returns:
            bytes: 字节类型
        """
        cls.address = address

        payload = cls.start
        payload += cls.address
        payload += what
        data_len = struct.pack(">H", len(data))
        crc = YingShaCrc(cls.address + what + data_len + data).crc()
        payload += data_len
        payload += data
        payload += crc
        payload += cls.end

        return payload

    @classmethod
    def unpack(cls, message: bytes) -> Self:
        """解包函数

        Args:
            message (bytes): 报文

        Raises:
            ValueError: crc校验失败

        Returns:
            Self: 帧对象
        """
        address = message[1:3]
        what = message[3:5]
        data_len = message[5:7]
        data = message[7:-3]
        crc = message[-3:-1]

        res = YingShaCrc(address + what + data_len + data).crc()
        if res != crc:
            raise ValueError("crc error")
        else:
            start = message[:1]
            end = message[-1:]

        return cls(
            start=start,
            address=address,
            what=what,
            data_len=data_len,
            data=data,
            crc=crc,
            end=end,
        )

    def __repr__(self) -> str:
        return f"YingShaFrame(start={self.start.hex().upper()}, address={self.address.hex().upper()}, what={self.what.hex().upper()}, data_len={self.data_len.hex().upper()}, data={self.data.hex().upper()}, crc={self.crc.hex().upper()}, end={self.end.hex().upper()})"


class YingShaCrc:
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


@dataclass(frozen=True)
class YingShaWhat:
    """英沙帧类型"""

    GET_ERROR_INFO = b"01"  # 获取故障信息

    UPLOAD_FILE = b"10"  # 上载文件

    DOWNLOAD_FILE = b"20"  # 下载文件

    PLAY_PLAY_LIST = b"98"  # 播放播放表

    GET_ITEM = b"97"  # 获取当前播放项

    GET_BRIGHTNESS = b"06"  # 获取亮度调节方式和显示亮度

    SET_BRIGHTNESS = b"05"  # 设置显示亮度


@dataclass(frozen=True)
class YingShaCode:
    """英沙帧返回码"""

    SUCCESS = b"0"
    FAILURL = b"1"


# ==============================================================================
# 报文类
# ==============================================================================
class YingShaMsg:
    """英沙报文类"""

    encoding: str = "gbk"

    @classmethod
    def make_upload_file(cls, content: str, file_name: str = "000.LST"):
        """上传文件

        Args:
            content (str): _description_
            file_name (str, optional): _description_. Defaults to "000.LST".
        """
        data = file_name.encode(cls.encoding)
        data += b"\x00"  # 作为文件名的结束
        data += b"\x00\x00\x00\x00"  # 文件指针偏移
        data += content.encode(cls.encoding)

        return YingShaFrame.pack(what=YingShaWhat.UPLOAD_FILE, data=data)

    @classmethod
    def make_download_file(cls, file_name: str = "000.LST") -> bytes:
        """下载文件

        Args:
            file_name (str, optional): _description_. Defaults to "000.LST".

        Returns:
            bytes: _description_
        """
        data = file_name.encode(cls.encoding)
        data += b"\x00"
        data += b"\x00\x00\x00\x00"

        return YingShaFrame.pack(what=YingShaWhat.DOWNLOAD_FILE, data=data)

    @classmethod
    def make_play_playlist(cls, file_id: str = "000") -> bytes:
        """播放播放表

        Args:
            file_name (str, optional): _description_. Defaults to "000.LST".

        Returns:
            bytes: _description_
        """
        data = file_id.encode(cls.encoding)
        return YingShaFrame.pack(what=YingShaWhat.PLAY_PLAY_LIST, data=data)
    
    @classmethod
    def make_get_item(cls) -> bytes:
        """获取当前播放项

        Returns:
            bytes: _description_
        """
        return YingShaFrame.pack(what=YingShaWhat.GET_ITEM, data=b"")
    
    @classmethod
    def make_get_brightness(cls) -> bytes:
        """获取亮度调节方式及亮度

        Returns:
            bytes: _description_
        """
        return YingShaFrame.pack(what=YingShaWhat.GET_BRIGHTNESS, data=b"")

    
    @classmethod
    def make_set_brightness(cls, value: int) -> bytes:
        """设置亮度

        Args:
            value (int): 亮度百分比 0~100

        Returns:
            bytes: _description_
        """
        brightness = max(min(31, value), 0)
        
        data = 3 * f"{brightness:02d}".encode("ascii")
        
        return YingShaFrame.pack(what=YingShaWhat.SET_BRIGHTNESS, data=data)