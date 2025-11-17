import textwrap
from highway_sdk.driver.vms.xianke.media import (
    MediaBuilder,
    PlayBuilder,
    ItemBuilder,
    FontEnum,
    TextSizeEnum,
    ColorEnum,
    ScreenInOutEnum,
    PlayParser
)


class TestPlayBuiler:
    def test_media_display(self):
        play_builder = PlayBuilder()
        item_builder1 = ItemBuilder()
        media_builder = MediaBuilder()
        media_builder.x = 0
        media_builder.y = 0
        media_builder.font = FontEnum.SONG_TI.value
        media_builder.text_size = TextSizeEnum.SIZE_32.value
        media_builder.text_color = ColorEnum.RED.value
        media_builder.background_color = ColorEnum.BLACK.value
        media_builder.text = "深圳显科科技有限公司"
        item_builder1._media = media_builder.build()
        item_builder1.duration = 2
        item_builder1.screen_in = ScreenInOutEnum.NORMAL.value
        item_builder1.screen_out = ScreenInOutEnum.NORMAL.value
        item_builder1.play_effect = 0
        item_builder1.play_speed = 1
        play_builder.add_item_builder(item_builder1)

        item_builder2 = ItemBuilder()
        media_builder = MediaBuilder()
        media_builder.x = 0
        media_builder.y = 0
        media_builder.font = FontEnum.SONG_TI.value
        media_builder.text_size = TextSizeEnum.SIZE_32.value
        media_builder.text_color = ColorEnum.GREEN.value
        media_builder.background_color = ColorEnum.BLACK.value
        media_builder.text = "深圳显科科技有限公司"
        item_builder2._media = media_builder.build()
        item_builder2.duration = 2
        item_builder2.screen_in = ScreenInOutEnum.NORMAL.value
        item_builder2.screen_out = ScreenInOutEnum.NORMAL.value
        item_builder2.play_effect = 0
        item_builder2.play_speed = 1
        play_builder.add_item_builder(item_builder2)

        actual = play_builder.build()
        expected = (
            textwrap.dedent(r"""
            [LIST]
            ItemCount=002
            Item00=2,1,0,1,1,\C000000\Fs32\T255000000000\B000000000000\U深圳显科科技有限公司 
            Item01=2,1,0,1,1,\C000000\Fs32\T000255000000\B000000000000\U深圳显科科技有限公司
        """)
            .lstrip()
            .replace("\n", "\r\n")
            .replace(" ", "")
        )

        assert str(actual) == expected


class TestPlayParser:
    def test_play_parse(self):
        parsed = (
            textwrap.dedent(r"""
            [LIST]
            ItemCount=002
            Item00=2,1,0,1,1,\C000000\Fs32\T255000000000\B000000000000\U深圳显科科技有限公司 
            Item01=2,1,0,1,1,\C000000\Fs32\T000255000000\B000000000000\U深圳显科科技有限公司
            """)
            .lstrip()
            .replace("\n", "\r\n")
            .replace(" ", "")
        )
        
        play_builder = PlayParser.parse(parsed)
        
        assert str(play_builder.build()) == parsed
        
        
        
