"""点明厂商帧工厂模块。

该模块提供了点明VMS设备的帧工厂类，用于创建各种请求帧。
"""

from .spec import ENCODING, Frame, What


class FrameFactory:
    """点明VMS帧工厂类。

    该类提供了创建各种请求帧的静态方法，遵循工厂模式。
    """

    @classmethod
    def set_play_list(cls, content: str, play_id: int = 0):
        """创建播放列表下发并立即显示的帧。

        Args:
            content: 播放列表内容。
            play_id: 播放列表ID，默认为0。

        Returns:
            Frame: 播放列表下发帧。
        """
        file_name = f"play{play_id:02d}.lst"

        data = b"+"
        data += b"00000000"
        data += file_name.encode(ENCODING)
        data += content.encode(ENCODING)

        return Frame(what=What.SET_PLAY_LIST_AND_PLAY_REQ, data=data)

    @classmethod
    def get_play_item(cls):
        """创建获取当前播放项的帧。

        Returns:
            Frame: 获取播放项请求帧。
        """
        return Frame(what=What.GET_PLAY_ITEM_REQ, data=b"")

    @classmethod
    def get_play_list(cls, play_id: int = 0):
        """创建获取播放列表的帧。

        Args:
            play_id: 播放列表ID，默认为0。

        Returns:
            Frame: 获取播放列表请求帧。
        """
        data = b"\x30\x30\x30\x30\x30\x30\x30\x30"
        data += f"play{play_id:02d}.lst".encode(ENCODING)
        return Frame(what=What.GET_PLAY_LIST_REQ, data=data)

    @classmethod
    def upload_file(cls, file_name: str):
        """创建上传文件的帧。

        Args:
            file_name: 文件名。

        Returns:
            Frame: 上传文件请求帧。
        """
        data = file_name.encode(ENCODING)
        data += b"+"
        data += b"\x30\x30\x30\x30\x30\x30\x30\x30"
        return Frame(what=What.DOWNLOAD_FILE_REQ, data=data)

    @classmethod
    def get_brightness_and_mode(cls):
        """获取亮度和控制亮度模式"""
        return Frame(what=What.GET_BRIGHTNESS_AND_MODE_REQ)

    @classmethod
    def set_brightness_or_mode(cls, brightness: int | None = None):
        """设置亮度或控制亮度模式"""
        if brightness is None:
            data = b"FFFFFF"  # 自动调节亮度
        else:
            brightness = max(0, min(31, brightness))
            first = brightness // 10
            second = brightness % 10
            # 红，绿，蓝三基色相同
            data = b"".join([bytes([ord(str(first)), ord(str(second))])] * 3)
        return Frame(what=What.SET_BRIGHTNESS_OR_MODE_REQ, data=data)
