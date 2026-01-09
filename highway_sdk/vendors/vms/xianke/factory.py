from .spec import Frame, What, ENCODING


class FrameFactory:
    @classmethod
    def get_play_item(cls):
        """获取播放项"""
        return Frame(what=What.GET_PLAY_ITEM)

    @classmethod
    def get_play_list_name(cls):
        """获取当前播放列表名称"""
        return Frame(what=What.GET_PLAY_LIST_NAME)

    @classmethod
    def select_play_list(cls, file_name: str = "000.xkl"):
        """选择播放列表"""
        data = file_name.encode(ENCODING)
        return Frame(what=What.SELECT_PLAY_LIST, data=data)

    @classmethod
    def upload_file(cls, content: str, file_name: str = "list\\000.xkl"):
        """上传播放表"""
        data = b"10"
        data += str(len(file_name)).encode("ascii").rjust(3, b"\x30")
        data += file_name.encode(ENCODING)
        data += b"\x30\x30\x30\x30"  # 文件偏移地址
        data += content.encode(ENCODING)

        return Frame(what=What.UPLOAD_FILE, data=data)

    @classmethod
    def download_file(cls, file_name: str = "list\\000.xkl"):
        """下载播放表"""
        data = str(len(file_name)).encode("ascii").rjust(3, b"\x30")
        data += file_name.encode(ENCODING)
        data += b"\x30\x30\x30\x30"

        return Frame(what=What.DOWNLOAD_FILE, data=data)

    @classmethod
    def get_brightness_and_mode(cls):
        """获取当前显示亮度"""
        return Frame(what=What.GET_BRIGHTNESS_AND_MODE)
