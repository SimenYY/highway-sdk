"""显科厂商设备模块。"""

from datetime import datetime

from highway_sdk.core.device import BaseDevice

from ..tags import CmsPlayItem, CmsTags
from .codec import XianKeCodec
from .spec import (
    ENCODING,
    BaseMedia,
    Color,
    Esc,
    Font,
    FontSize,
    Frame,
    Gif,
    Image,
    Item,
    Play,
    ScreenInOut,
    Text,
    Video,
    What,
)

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


class XianKeCms(BaseDevice[XianKeCodec]):
    """显科CMS设备客户端。

    所有方法成功返回业务数据（CmsTags）或 None，失败抛 ``DeviceOperationError`` 等
    ``HighwaySDKError`` 子类异常，由调用方捕获处理。
    """

    codec = XianKeCodec

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
        frame = Frame(what=What.GET_BRIGHTNESS_AND_MODE)
        response = await self._request(frame)
        data = self.codec.decode(response)
        cms_tags = CmsTags(
            brightness=data["brightness"],
            brightness_mode="manual" if data["mode"] == 1 else "auto",
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
        frame = Frame(what=What.GET_PLAY_ITEM)
        response = await self._request(frame)
        data = self.codec.decode(response)

        orig_play_item = data.get("text") or ""
        play_item = CmsPlayItem(
            index=0,
            text=data.get("text"),
            font=None,
            font_color=None,
            font_size=None,
            image_name=None,
            duration=None,
        )

        cms_tags = CmsTags(
            orig_play_item=orig_play_item,
            play_item=play_item,
            timestamp=datetime.now(),
        )
        return cms_tags

    async def get_play_list(self, play_id: int = 0) -> CmsTags:
        """获取当前播放列表（结构化 + 原始格式）。

        Args:
            play_id: 播放列表 ID，默认为 0。

        Returns:
            CmsTags: 填充 play_list、orig_play_list、timestamp。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。
        """
        frame = Frame(what=What.DOWNLOAD_FILE)
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

    async def upload_file(self, content: str, file_name: str = "list\\000.xkl") -> None:
        """上传文件。

        Args:
            content: 文件内容。
            file_name: 文件名，默认为 "list\\000.xkl"。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。
        """
        data = b"10"
        data += str(len(file_name)).encode("ascii").rjust(3, b"0")
        data += file_name.encode(ENCODING)
        data += b"0000"
        data += content.encode(ENCODING)
        frame = Frame(what=What.UPLOAD_FILE, data=data)
        response = await self._request(frame)
        self.codec.decode(response)

    async def select_play_list(self, file_name: str = "000.xkl") -> None:
        """选择播放列表进行播放。

        Args:
            file_name: 播放列表文件名，默认为 "000.xkl"。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。
        """
        data = file_name.encode(ENCODING)
        frame = Frame(what=What.SELECT_PLAY_LIST, data=data)
        response = await self._request(frame)
        self.codec.decode(response)

    async def set_play_list(self, items: list[CmsPlayItem], file_name: str = "list\\000.xkl") -> None:
        """下发播放列表并立即播放。

        XianKe 需要两步：upload_file 上传文件 → select_play_list 触发播放。
        任一步失败抛异常，后续步骤不执行。

        Args:
            items: 播放项列表。
            file_name: 文件名，默认为 ``list\\000.xkl``（XianKe 协议规定的特殊命名，
                含 ``\\`` 路径分隔符；select 时取 basename ``000.xkl``）。

        Raises:
            DeviceOperationError: 设备返回错误响应。
            ResponseTimeoutError: 响应超时。
            DeviceConnectionError: 连接异常。
        """
        content = self._items_to_content(items)
        await self.upload_file(content, file_name)
        play_name = file_name.split("\\")[-1] if "\\" in file_name else file_name
        await self.select_play_list(play_name)

    # ------------------------------------------------------------------
    # 内部工具方法
    # ------------------------------------------------------------------

    @staticmethod
    def _dict_to_cms_play_item(item: dict) -> CmsPlayItem:
        """将厂商解析结果转换为统一 CmsPlayItem。"""
        text = item.get("text")
        font = item.get("font")
        font_color = item.get("font_color")
        font_size = item.get("font_size")

        image_name = None
        for key in ("bmp", "gif", "mpg"):
            if item.get(key):
                image_name = item[key]
                break

        duration = None
        if item.get("duration") is not None:
            duration = item["duration"]  # 显科 duration 单位已经是秒

        return CmsPlayItem(
            index=None,
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
        文本中的 ``\\n`` 自动转为协议换行转义码 ``\\N``。
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
                font_size=cls._font_size_to_enum(item.font_size),
                font_color=cls._hex_color_to_vendor(item.font_color),
                background_color=Color.BLACK,
                text=item.text.replace("\n", Esc.LF.value),
            )
            media_list.append(text)
        if item.image_name:
            ext = item.image_name.lower().rsplit(".", 1)[-1] if "." in item.image_name else ""
            if ext == "gif":
                media_list.append(Gif(x=x, y=y, gif_file_name=item.image_name))
            elif ext in ("mpg", "mpeg", "mp4"):
                media_list.append(Video(x=x, y=y, video_file_name=item.image_name))
            else:
                media_list.append(Image(x=x, y=y, image_file_name=item.image_name))
        if not media_list:
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

        - CmsPlayItem.duration 单位为秒，XianKe Item.duration 单位也是秒（无需转换）
        - 缺失字段使用默认值：x=0, y=0, screen_in=NORMAL, play_effect=0, screen_out=NORMAL, play_speed=1
        """
        if not items:
            raise ValueError("播放列表不能为空")
        item_list = []
        for cms_item in items:
            duration_sec = cms_item.duration if cms_item.duration is not None else 10
            duration_sec = max(1, min(65535, duration_sec))
            item = Item(
                media_list=cls._item_to_media_list(cms_item),
                duration=duration_sec,
                screen_in=ScreenInOut.NORMAL,
                play_effect=0,
                screen_out=ScreenInOut.NORMAL,
                play_speed=1,
            )
            item_list.append(item)
        return str(Play(item_list=item_list))
