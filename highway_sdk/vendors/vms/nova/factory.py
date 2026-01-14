import struct

from .spec import ENCODING, Frame, What


class FrameFactory:
    @classmethod
    def send_file_name(cls, file_name: str = "play001.lst", block_size: int = 65535) -> Frame:
        """发送文件名

        上位机发送：
        AA FF FF 11 FF FF 70 6C 61 79 30 30 31 2E 6C 73 74 CC 5A 9B

        设备回复：
        AA FF FF 12 01 CC A1 B4

        Args:
            file_name (str): _description_
            block_size (int, optional): _description_. Defaults to 65535.

        Returns:
            bytes: _description_
        """
        data = struct.pack("<H", block_size)
        data += file_name.encode(ENCODING, "ignore")
        return Frame(what=What.SEND_FILE_NAME_REQ, data=data)

    @classmethod
    def send_file_content(cls, content: str, block_num: int = 1) -> Frame:
        """发送文件内容

        上位机发送：
        AA FF FF 13 01 00 5B 61 6C 6C 5D 0D 0A 69 74 65 6D 73 3D 31 0D 0A 5B 69 74 65 6D 31 5D 0D 0A 70 61 72 61 6D
        3D 31 30 30 2C 31 2C 31 2C 31 2C 30 2C 35 2C 31 0D 0A 74 78 74 65 78 74 31 3D 30 2C 30 2C 30 2C 32 38 30 2C 33 2C 34 38
        34 38 2C 30 2C 30 2C 30 2C 31 2C 30 2C 31 2C 38 2C 30 2C 32 2C 31 30 30 2C 31 2C E9 A9 AC E5 B0 94 E5 BA B7 E6 AC A2 E8
        BF 8E E6 82 A8 E3 80 82 2C 31 2C 31 2C 30 2C 35 2C 35 2C 35 CC 83 84

        设备回复：
        AA FF FF 14 01 00 01 CC 91 C4

        Args:
            content (str): _description_
            block_num (int, optional): _description_. Defaults to 1.

        Returns:
            bytes: _description_
        """
        data = struct.pack("<H", block_num)
        data += content.encode(ENCODING, "ignore")
        return Frame(what=What.SEND_FILE_CONTENT_REQ, data=data)

    @classmethod
    def select_play_list(cls, playlist_id: int = 1):
        """指定播放列表进行播放

        上位机发送：
        AA FF FF 1B 01 CC BF 28

        设备回复：
        AA FF FF 1C 01 CC BA A4

        Args:
            playlist_id (int, optional): _description_. Defaults to 1.

        Returns:
            _type_: _description_
        """
        data = struct.pack(">B", playlist_id)
        return Frame(what=What.SELECT_PLAY_LIST_REQ, data=data)

    @classmethod
    def get_play_item(cls) -> Frame:
        """获取当前播放项

        上位机发送：
        AA FF FF 2D CC EE 0A

        设备回复：
        AA FF FF 2E 01 01 01 5B 69 74 65 6D 31 5D 0A 70 61 72 61 6D 3D 31 30 30 2C 31 2C 31 2C 31 2C 30 2C 35 2C 31 2C
        30 2C 31 0A 74 78 74 31 3D 31 30 2C 30 2C 33 2C 31 36 31 36 2C 31 2C 38 2C 30 2C E8 BD A6 E7 89 8C EF BC 9A E5 86 80 41
        33 31 38 41 41 E5 A4 A7 E8 B4 A7 E8 BD A6 2C 31 39 32 2C 33 32 30 2C 30 0A 74 78 74 70 61 72 61 6D 31 3D 30 2C 30 CC 20
        DF

        Returns:
            bytes: _description_
        """
        return Frame(what=What.GET_PLAY_ITEM_REQ, data=b"")

    @classmethod
    def get_play_list(cls) -> Frame:
        """获取当前播放表

        上位机发送：
        AA FF FF 3A CC 77 D2

        设备回复：
        AA FF FF 3B 01 5B 61 6C 6C 5D 0A 69 74 65 6D 73 3D 31 0A 5B 69 74 65 6D 31 5D 0A 70 61 72 61 6D 3D 31 30 30 2C
        31 2C 31 2C 31 2C 30 2C 35 2C 31 2C 30 2C 31 0A 74 78 74 31 3D 31 30 2C 30 2C 33 2C 31 36 31 36 2C 31 2C 38 2C 30 2C E8
        BD A6 E7 89 8C EF BC 9A E5 86 80 41 33 31 38 41 41 E5 A4 A7 E8 B4 A7 E8 BD A6 2C 31 39 32 2C 33 32 30 2C 30 0A 74 78 74
        70 61 72 61 6D 31 3D 30 2C 30 CC D9 25

        Returns:
            bytes: _description_
        """
        return Frame(what=What.GET_PLAY_LIST_REQ, data=b"")

    @classmethod
    def get_screen_size(cls) -> Frame:
        """获取屏幕点阵大小

        上位机发送：
        AA FF FF 82 CC D9 26

        设备回复：
        AA FF FF 83 A0 02 C0 01 CC 05 20

        Returns:
            bytes: _description_
        """
        return Frame(what=What.GET_SCREEN_SIZE_REQ, data=b"")

    @classmethod
    def get_now_brightness(cls) -> Frame:
        """获取当前亮度

        上位机发送:
        AA FF FF C3 CC 67 79

        设备回复:
        AA FF FF C3 02 FF CC 3A 2F

        Returns:
            bytes: _description_
        """
        return Frame(what=What.GET_BRIGHTNESS_REQ, data=b"")
