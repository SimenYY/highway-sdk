"""三思厂商设备模块。"""

from datetime import datetime

from highway_sdk.core.device import BaseDevice

from ..tags import CmsPlayItem, CmsTags
from .codec import SanSiCodec
from .spec import ENCODING, BaseMedia, Bmp, Color, Font, FontSize, Frame, Gif, Item, Jpg, Mpg, Play, Png, Text, What

# 中文字体名 → Font 枚举映射
_FONT_NAME_MAP = {
    "黑体": Font.HEI_TI,
    "楷体": Font.KAI_TI,
    "宋体": Font.SONG_TI,
    "仿宋": Font.FANG_SONG,
}

# 字号 → FontSize 枚举映射
_FONT_SIZE_MAP = {
    16: FontSize._16,
    24: FontSize._24,
    32: FontSize._32,
    48: FontSize._48,
    64: FontSize._64,
}


class SanSiDevice(BaseDevice[SanSiCodec]):
    """三思CMS设备客户端。

    所有方法成功返回业务数据（dict）或 None，失败抛 ``DeviceOperationError`` 等
    ``HighwaySDKError`` 子类异常，由调用方捕获处理。
    """

    codec = SanSiCodec

    async def _request(self, frame: Frame, timeout: float | None = None) -> Frame:
        """发送请求帧并返回解析后的响应帧（SanSi 响应无 what 字段）。"""
        response = await self.request(frame, timeout)
        return Frame.from_bytes(response)

    # ------------------------------------------------------------------
    # 数据采集 API（返回 CmsTags.model_dump()，失败抛异常）
    # ------------------------------------------------------------------

    async def get_brightness(self) -> dict:
        """获取亮度百分比和亮度控制模式。

        Returns:
            dict: ``CmsTags.model_dump()``，仅填充 brightness、brightness_mode、timestamp。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。
        """
        frame = Frame(what=What.GET_BRIGHTNESS_AND_MODE)
        response = await self._request(frame)
        data = self.codec.decode_get_brightness(response.data)
        cms_tags = CmsTags(
            brightness=data["brightness"],
            brightness_mode="auto" if data["mode"] == 0 else "manual",
            timestamp=datetime.now(),
        )
        return cms_tags.model_dump()

    async def get_play_item(self) -> dict:
        """获取当前播放项（结构化 + 原始格式）。

        Returns:
            dict: ``CmsTags.model_dump()``，填充 play_item（含 index）、orig_play_item、timestamp。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。
        """
        frame = Frame(what=What.GET_PLAY_ITEM)
        response = await self._request(frame)
        data = self.codec.decode_get_play_item(response.data)

        orig_play_item = data.get("media") or ""
        play_item = self._dict_to_cms_play_item(data)

        cms_tags = CmsTags(
            orig_play_item=orig_play_item,
            play_item=play_item,
            timestamp=datetime.now(),
        )
        return cms_tags.model_dump()

    async def get_play_list(self, file_name: str = "play.lst") -> dict:
        """获取当前播放列表（结构化 + 原始格式）。

        SanSi 无直接获取播放列表指令，通过 DOWNLOAD_FILE 下载文件实现，
        默认下载 ``play.lst``。

        请求 data 域格式：``file_name`` + 4 字节文件偏移（``\\x00\\x00\\x00\\x00``）
        真实报文（用户提供）：
            02 30 30 30 39 70 6C 61 79 2E 6C 73 74 00 00 00 00 57 2A 03
            data = "play.lst" + b"\\x00\\x00\\x00\\x00"

        Args:
            file_name: 文件名，默认为 "play.lst"。

        Returns:
            dict: ``CmsTags.model_dump()``，填充 play_list、orig_play_list、timestamp。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。
        """
        data = file_name.encode(ENCODING) + b"\x00\x00\x00\x00"
        frame = Frame(what=What.DOWNLOAD_FILE, data=data)
        response = await self._request(frame)
        play_data = self.codec.decode_download_file(response.data)

        play_list = []
        orig_play_list_parts = []
        for window in play_data.get("windows", []):
            for item in window.get("items", []):
                play_list.append(self._dict_to_cms_play_item(item))
                orig_play_list_parts.append(item.get("media") or "")

        cms_tags = CmsTags(
            orig_play_list="\r\n".join(orig_play_list_parts),
            play_list=play_list,
            timestamp=datetime.now(),
        )
        return cms_tags.model_dump()

    # ------------------------------------------------------------------
    # 控制类 API（成功返回 None，失败抛异常）
    # ------------------------------------------------------------------

    async def set_brightness(self, brightness: int) -> None:
        """设置亮度。

        Args:
            brightness: 亮度值，范围0-31。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。
        """
        brightness = max(0, min(31, brightness))
        data = (f"{brightness:02d}".encode("ascii")) * 3
        frame = Frame(what=What.SET_BRIGHTNESS, data=data)
        response = await self._request(frame)
        self.codec.decode_set_brightness(response.data)

    async def upload_file(self, content: str, file_name: str = "play.lst") -> None:
        """上传播放列表文件。

        Args:
            content: 文件内容。
            file_name: 文件名，默认为 "play.lst"。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。
        """
        data = file_name.encode(ENCODING) + b"+" + b"\x00\x00\x00\x00" + content.encode(ENCODING)
        frame = Frame(what=What.UPLOAD_FILE, data=data)
        response = await self._request(frame)
        self.codec.decode_upload_file(response.data)

    async def set_play_list(self, items: list[CmsPlayItem], file_name: str = "play.lst") -> None:
        """下发播放列表并立即播放。

        SanSi 上传文件即自动更改当前播放表，无需额外播放指令。

        Args:
            items: 播放项列表。
            file_name: 文件名，默认为 "play.lst"。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。
        """
        content = self._items_to_content(items)
        await self.upload_file(content, file_name)

    # ------------------------------------------------------------------
    # 内部工具方法
    # ------------------------------------------------------------------

    @staticmethod
    def _dict_to_cms_play_item(item: dict) -> CmsPlayItem:
        """将厂商解析结果转换为统一 CmsPlayItem。"""
        index = None
        if item.get("index") and str(item["index"]).isdigit():
            index = int(item["index"])

        text = item.get("text")
        font = item.get("font")
        font_color = item.get("font_color")
        font_size = item.get("font_size")

        # 从多个可能的图片字段中获取第一个非空的
        image_name = None
        for key in ("bmp", "jpg", "png", "gif"):
            if item.get(key):
                image_name = item[key]
                break

        duration = None
        if item.get("duration") is not None:
            duration = item["duration"]  # 三思已经转换为秒

        return CmsPlayItem(
            index=index,
            text=text,
            font=font,
            font_color=font_color,
            font_size=font_size,
            image_name=image_name,
            duration=duration,
        )

    @staticmethod
    def _hex_color_to_vendor(hex_color: str | None) -> Color:
        """将 '#RRGGBB' 转换为厂商 Color 枚举（'RRRGGGBBB000'）。"""
        if hex_color is None:
            return Color.BLACK
        hex_color = hex_color.lstrip("#")
        if len(hex_color) != 6:
            return Color.BLACK
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
        except ValueError:
            return Color.BLACK
        return Color(f"{r:03d}{g:03d}{b:03d}000")

    @staticmethod
    def _font_size_to_enum(font_size: int | None) -> FontSize:
        """将字号映射到 FontSize 枚举，缺失或非法时默认 32。"""
        if font_size is None:
            return FontSize._32
        return _FONT_SIZE_MAP.get(font_size, FontSize._32)

    @classmethod
    def _item_to_media_list(cls, item: CmsPlayItem) -> list[BaseMedia]:
        """将单个 CmsPlayItem 转换为媒体对象列表。"""
        media_list: list[BaseMedia] = []
        if item.text is not None:
            font_enum = _FONT_NAME_MAP.get(item.font or "黑体", Font.HEI_TI)
            text = Text(
                x=0,
                y=0,
                font=font_enum,
                font_size=cls._font_size_to_enum(item.font_size),
                font_color=cls._hex_color_to_vendor(item.font_color),
                background_color=Color.BLACK,
                text=item.text,
            )
            media_list.append(text)
        if item.image_name:
            ext = item.image_name.lower().rsplit(".", 1)[-1] if "." in item.image_name else ""
            if ext == "png":
                media_list.append(Png(x=0, y=0, png_file_name=item.image_name))
            elif ext in ("jpg", "jpeg"):
                media_list.append(Jpg(x=0, y=0, jpg_file_name=item.image_name))
            elif ext == "gif":
                media_list.append(Gif(x=0, y=0, gif_file_name=item.image_name))
            elif ext == "mpg":
                media_list.append(Mpg(x=0, y=0, mpg_file_name=item.image_name))
            else:
                media_list.append(Bmp(x=0, y=0, bmp_file_name=item.image_name))
        if not media_list:
            # 兜底：无文本也无图片时构造空文本项，避免 media_list 为空
            media_list.append(
                Text(
                    x=0,
                    y=0,
                    font=Font.HEI_TI,
                    font_size=FontSize._32,
                    font_color=Color.BLACK,
                    background_color=Color.BLACK,
                    text="",
                )
            )
        return media_list

    @classmethod
    def _items_to_content(cls, items: list[CmsPlayItem]) -> str:
        """将 CmsPlayItem 列表转换为协议字符串。

        - CmsPlayItem.duration 单位为秒，SanSi Item.duration 单位为百分之一秒（×100）
        - 缺失字段使用默认值：x=0, y=0, screen_in=1, play_speed=0
        """
        if not items:
            raise ValueError("播放列表不能为空")
        item_list = []
        for cms_item in items:
            duration_sec = cms_item.duration if cms_item.duration is not None else 10
            duration_cent = max(2, min(30000, duration_sec * 100))
            item = Item(
                media_list=cls._item_to_media_list(cms_item),
                duration=duration_cent,
                screen_in=1,
                play_speed=0,
            )
            item_list.append(item)
        return str(Play(item_list=item_list))
