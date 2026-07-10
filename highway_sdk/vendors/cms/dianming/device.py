"""电明厂商设备模块。"""

from datetime import datetime

from highway_sdk.core.device import BaseDevice

from ..tags import CmsPlayItem, CmsTags
from .codec import DianMingCodec
from .spec import ENCODING, BaseMedia, Bmp, Color, Esc, Font, FontSize, Frame, Gif, Item, Jpg, Play, Png, Text, What

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


class DianMingCms(BaseDevice[DianMingCodec]):
    """电明CMS设备客户端。

    所有方法成功返回业务数据（CmsTags）或 None，失败抛 ``DeviceOperationError`` 等
    ``HighwaySDKError`` 子类异常，由调用方捕获处理。
    """

    codec = DianMingCodec

    async def _request(self, frame: Frame, timeout: float | None = None) -> Frame:
        """发送请求帧并返回解析后的响应帧。"""
        response = await self.request(frame, timeout)
        return Frame.from_bytes(response)

    # ------------------------------------------------------------------
    # 数据采集 API（返回 CmsTags，失败抛异常）
    # ------------------------------------------------------------------

    async def get_brightness(self) -> CmsTags:
        """获取亮度百分比和亮度控制模式。

        Returns:
            CmsTags: 仅填充 brightness、brightness_mode、timestamp。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。
        """
        frame = Frame(what=What.GET_BRIGHTNESS_AND_MODE_REQ)
        response = await self._request(frame)
        data = self.codec.decode(response)
        cms_tags = CmsTags(
            brightness=data["brightness"],
            brightness_mode=data["mode"],
            timestamp=datetime.now(),
        )
        return cms_tags

    async def get_play_item(self) -> CmsTags:
        """获取当前播放项（结构化 + 原始格式）。

        Returns:
            CmsTags: 填充 play_item（含 index）、orig_play_item、timestamp。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。
        """
        frame = Frame(what=What.GET_PLAY_ITEM_REQ)
        response = await self._request(frame)
        data = self.codec.decode(response)

        orig_play_item = data.get("media") or ""
        play_item = self._dict_to_cms_play_item(data)

        cms_tags = CmsTags(
            orig_play_item=orig_play_item,
            play_item=play_item,
            timestamp=datetime.now(),
        )
        return cms_tags

    async def get_play_list(self, play_id: int = 0, filename: str = "play00.lst") -> CmsTags:
        """获取当前播放列表（结构化 + 原始格式）。

        Args:
            play_id: 播放列表 ID，默认为 0。
            filename: 播放列表文件名，默认为 "play00.lst"。

        Returns:
            CmsTags: 填充 play_list、orig_play_list、timestamp。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。
        """
        offset = f"{play_id:08d}".encode("ascii")
        data = offset + filename.encode("ascii")
        frame = Frame(what=What.GET_PLAY_LIST_REQ, data=data)
        response = await self._request(frame)
        play_data = self.codec.decode(response)

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
        return cms_tags

    # ------------------------------------------------------------------
    # 控制类 API（成功返回 None，失败抛异常）
    # ------------------------------------------------------------------

    async def set_brightness(self, brightness: int | None = None) -> None:
        """设置亮度或控制亮度模式。

        Args:
            brightness: 亮度值(0-31)，None表示自动调节亮度模式。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。
        """
        if brightness is None:
            data = b"FFFFFF"
        else:
            brightness = max(0, min(31, brightness))
            data = (f"{brightness:02d}" * 3).encode("ascii")
        frame = Frame(what=What.SET_BRIGHTNESS_OR_MODE_REQ, data=data)
        response = await self._request(frame)
        self.codec.decode(response)

    async def set_play_list(self, items: list[CmsPlayItem], file_name: str = "play.lst") -> None:
        """下发播放列表并立即播放。

        DianMing 使用 SET_PLAY_LIST_AND_PLAY_REQ 单指令完成下发并播放。

        Args:
            items: 播放项列表。
            file_name: 文件名，默认为 "play.lst"。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。
        """
        content = self._items_to_content(items)
        data = b"+00000000" + file_name.encode(ENCODING) + content.encode(ENCODING)
        frame = Frame(what=What.SET_PLAY_LIST_AND_PLAY_REQ, data=data)
        response = await self._request(frame)
        self.codec.decode(response)

    # ------------------------------------------------------------------
    # 内部工具方法
    # ------------------------------------------------------------------

    @staticmethod
    def _dict_to_cms_play_item(item: dict) -> CmsPlayItem:
        """将厂商解析结果转换为统一 CmsPlayItem。"""
        index = None
        if item.get("index") and item["index"].isdigit():
            index = int(item["index"])

        text = None
        font = None
        font_color = None
        font_size = None
        image_name = None

        for media in item.get("media_list", []):
            if media.get("text") and text is None:
                text = media["text"]
            if media.get("font") and font is None:
                font = media["font"]
            if media.get("font_color") and font_color is None:
                font_color = media["font_color"]
            if media.get("font_size") and font_size is None:
                font_size = media["font_size"]
            if media.get("bmp") and image_name is None:
                image_name = media["bmp"]
            elif media.get("jpg") and image_name is None:
                image_name = media["jpg"]
            elif media.get("png") and image_name is None:
                image_name = media["png"]
            elif media.get("gif") and image_name is None:
                image_name = media["gif"]

        duration = None
        if item.get("duration") is not None:
            duration = item["duration"] // 10  # 十分之一秒 → 秒

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
        """将单个 CmsPlayItem 转换为媒体对象列表。

        优先使用 ``CmsPlayItem.x`` / ``CmsPlayItem.y`` 作为渲染坐标，缺失时默认 0。
        文本中的 ``\\n`` 自动转为协议换行转义码 ``\\A``。
        配合 ``TextLayout`` 工具可实现文字居中显示。
        """
        media_list: list[BaseMedia] = []
        x = item.x or 0
        y = item.y or 0
        if item.text is not None:
            font_enum = _FONT_NAME_MAP.get(item.font or "黑体", Font.HEI_TI)
            text = Text(
                x=x,
                y=y,
                font=font_enum,
                text_size=cls._font_size_to_enum(item.font_size),
                text_color=cls._hex_color_to_vendor(item.font_color),
                background_color=Color.BLACK,
                word_space=0,
                text=item.text.replace("\n", Esc.LF.value),
            )
            media_list.append(text)
        if item.image_name:
            ext = item.image_name.lower().rsplit(".", 1)[-1] if "." in item.image_name else ""
            if ext == "png":
                media_list.append(Png(x=x, y=y, png_file_name=item.image_name))
            elif ext in ("jpg", "jpeg"):
                media_list.append(Jpg(x=x, y=y, jpg_file_name=item.image_name))
            elif ext == "gif":
                media_list.append(Gif(x=x, y=y, gif_file_name=item.image_name))
            else:
                media_list.append(Bmp(x=x, y=y, bmp_file_name=item.image_name))
        if not media_list:
            media_list.append(
                Text(
                    x=0,
                    y=0,
                    font=Font.HEI_TI,
                    text_size=FontSize._32,
                    text_color=Color.BLACK,
                    background_color=Color.BLACK,
                    word_space=0,
                    text="",
                )
            )
        return media_list

    @classmethod
    def _items_to_content(cls, items: list[CmsPlayItem]) -> str:
        """将 CmsPlayItem 列表转换为协议字符串。

        - CmsPlayItem.duration 单位为秒，DianMing Item.duration 单位为十分之一秒（×10）
        - 缺失字段使用默认值：x=0, y=0, screen_in_mode=0, play_effect=0, screen_out_mode=0, play_speed=0
        """
        if not items:
            raise ValueError("播放列表不能为空")
        item_list = []
        for cms_item in items:
            duration_sec = cms_item.duration if cms_item.duration is not None else 10
            duration_deci = max(2, min(30000, duration_sec * 10))
            item = Item(
                media_list=cls._item_to_media_list(cms_item),
                duration=duration_deci,
                screen_in_mode=0,
                play_effect=0,
                screen_out_mode=0,
                play_speed=0,
            )
            item_list.append(item)
        return str(Play(item_list=item_list))
