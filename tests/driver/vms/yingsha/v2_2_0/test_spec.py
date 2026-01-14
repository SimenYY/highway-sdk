import pytest

from highway_sdk.vendors.vms.yingsha.media import (
    ColorEnum,
    FontEnum,
    FontSizeEnum,
    ItemBuilder,
    PlayBuilder,
    ScreenInOutEnum,
    TextMediaBuilder,
)
from highway_sdk.vendors.vms.yingsha.spec import YingShaMsg


class TestYingShaMsg:
    def test_make_get_item(self):
        actual = YingShaMsg.make_get_item()

        expected = "02 30 30 39 37 00 00 BC C9 03"

        assert actual.hex(" ").upper() == expected

    def test_make_download_file(self):
        actual = YingShaMsg.make_download_file()

        expected = "02 30 30 32 30 00 0C 30 30 30 2E 4C 53 54 00 00 00 00 00 A1 DD 03"

        assert actual.hex(" ").upper() == expected

    def test_make_upload_file(self):
        pb = PlayBuilder()
        ib_1 = ItemBuilder()
        mb = TextMediaBuilder()
        mb.font_size = FontSizeEnum.SIZE_16.value
        mb.text_color = ColorEnum.RED.value
        mb.font = FontEnum.FANG_SONG.value
        mb.x = 4
        mb.y = 16
        mb.text = "前方匝道事故 靠\\n右行驶"
        ib_1.add_media_builder(mb)
        ib_1.duration = 1000
        ib_1.screen_in = ScreenInOutEnum.NORMAL
        ib_1.play_speed = 0
        pb.add_item_builder(ib_1)

        actual = YingShaMsg.make_upload_file(content=f"{pb.build()}")

        expected = "02 30 30 31 30 00 6D 30 30 30 2E 4C 53 54 00 00 00 00 00 5B 50 4C 41 59 4C 49 53 54 5D 0D 0A 49 54 45 4D 5F 4E 4F 3D 31 0D 0A 49 54 45 4D 30 3D 31 30 30 30 2C 31 2C 30 2C 5C 43 30 30 34 30 31 36 5C 66 66 31 36 31 36 5C 63 32 35 35 30 30 30 30 30 30 30 30 30 C7 B0 B7 BD D4 D1 B5 C0 CA C2 B9 CA 20 BF BF 5C 6E D3 D2 D0 D0 CA BB 0D 0A 5B 45 4E 44 5D 10 C9 03"
        # print(bytes.fromhex(expected).decode("gbk", "ignore"))
        assert actual.hex(" ").upper() == expected

    @pytest.mark.skip(reason="TODO")
    def test_make_get_brightness(self):
        pass

    @pytest.mark.skip(reason="TODO")
    def test_make_set_brightness(self):
        pass
