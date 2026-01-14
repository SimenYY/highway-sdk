"""丰海厂商帧工厂模块。

该模块提供了丰海VMS设备的帧工厂类，用于创建各种请求帧。
"""

from .spec import ENCODING, Frame, What


class FrameFactory:
    """丰海VMS帧工厂类。

    该类提供了创建各种请求帧的静态方法，遵循工厂模式。
    """

    @classmethod
    def get_play_item(cls):
        """创建获取当前播放项的帧。

        Returns:
            Frame: 获取播放项请求帧。
        """
        return Frame(
            what=What.GET_PLAY_ITEM,
        )

    @classmethod
    def set_brightness(cls, brightness: int):
        """创建设置亮度的帧。

        Args:
            brightness: 亮度值，范围0-31。

        Returns:
            Frame: 设置亮度请求帧。
        """
        brightness = max(0, min(31, brightness))

        return Frame(
            what=What.SET_BRIGHTNESS,
            data=bytes([ord(c) for c in f"{brightness:02d}"]) * 3,
        )

    @classmethod
    def download_file(cls, file_name: str = "play.lst"):
        """创建下载文件的帧。

        Args:
            file_name: 文件名，默认为"play.lst"。

        Returns:
            Frame: 下载文件请求帧。
        """
        return Frame(
            what=What.DOWNLOAD_FILE,
            data=(file_name.encode(ENCODING, "ignore") + b"+" + b"\x00\x00\x00\x00"),
        )

    @classmethod
    def upload_file(cls, content: str, file_name: str = "play.lst"):
        """创建上传文件的帧。

        Args:
            content: 文件内容。
            file_name: 文件名，默认为"play.lst"。

        Returns:
            Frame: 上传文件请求帧。
        """
        return Frame(
            what=What.UPLOAD_FILE,
            data=(
                file_name.encode(ENCODING, "ignore") + b"+" + b"\x00\x00\x00\x00" + content.encode(ENCODING, "ignore")
            ),
        )

    @classmethod
    def get_birghtness_and_mode(cls):
        """创建获取亮度和模式的帧。

        Returns:
            Frame: 获取亮度和模式请求帧。
        """
        return Frame(what=What.GET_BRIGHTNESS_AND_MODE)
