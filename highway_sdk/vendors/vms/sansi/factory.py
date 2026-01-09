from .spec import Frame, What, ENCODING


class FrameFactory:
    @classmethod
    def get_play_item(cls):
        """获取播放项        
        """
        return Frame(what=What.GET_PLAY_ITEM)

    @classmethod
    def download_file(cls, file_name: str = "play.lst"):
        """下载播放表
        """
        data = file_name.encode(ENCODING, "ignore")
        data += b"\x00\x00\x00\x00"  # 文件指针偏移
        return Frame(what=What.DOWNLOAD_FILE, data=data)

    @classmethod
    def get_brightness_and_mode(cls):
        """获取亮度和控制亮度模式
        """
        return Frame(what=What.GET_BRIGHTNESS_AND_MODE)

    @classmethod
    def set_brightness(cls, brightness: int):
        """设置亮度
        """
        brightness = max(0, min(31, brightness))
        first = brightness // 10
        second = brightness % 10
        # 红，绿，蓝三基色相同
        data = b"" .join([bytes([ord(str(first)), ord(str(second))])] * 3)
        return Frame(what=What.SET_BRIGHTNESS, data=data)           

    @classmethod
    def upload_file(cls, content: str, file_name: str = "play.lst"):
        """上传播放表
        """
        data = file_name.encode(ENCODING, "ignore")
        data += b"+"  # 分隔符，代表文件名结束
        data += b"\x00\x00\x00\x00"  # 文件指针偏移
        data += content.encode(ENCODING, "ignore")  # 文件内容
        return Frame(what=What.UPLOAD_FILE, data=data)           
