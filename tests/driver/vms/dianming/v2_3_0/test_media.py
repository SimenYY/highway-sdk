import textwrap
from highway_sdk.vendors.vms.dianming.media import (
    TextBuilder,
    ItemBuilder,
    PlayBuilder,
    BmpBuilder,
    Font,
    Color,
    FontSize,
    PlayParser,
)


class TestMedia:
    def test_play_build(self):
        play_builder = PlayBuilder()
        item_builder1 = ItemBuilder()
        text_builder = TextBuilder("Hello World!")
        text_builder.x = 32
        text_builder.font = Font.SONG_TI.value
        text_builder.text_color = Color.RED.value
        text_builder.background_color = Color.GREEN.value
        text_builder.text_size = FontSize._32.value
        bmp_builder = BmpBuilder("000")
        item_builder1.add_media_builder(bmp_builder).add_media_builder(text_builder)
        item_builder1.duration = 30
        play_builder.add_item_builder(item_builder1)

        item_builder2 = ItemBuilder()
        text_builder = TextBuilder("SLOW DOWN")
        text_builder.text_size = FontSize._32.value
        text_builder.font = Font.SONG_TI.value
        text_builder.text_color = Color.RED.value
        text_builder.background_color = Color.GREEN.value
        item_builder2.duration = 30
        item_builder2.add_media_builder(text_builder)
        play_builder.add_item_builder(item_builder2)

        actual = play_builder.build()

        expected = (
            textwrap.dedent(r"""
            [PLAYLIST]
            ITEM_NO=002
            ITEM000=30,0,0,0,0,\C000000\B000\C032000\Fs3232\T255000000000\K000255000000\WHello World!
            ITEM001=30,0,0,0,0,\C000000\Fs3232\T255000000000\K000255000000\WSLOW DOWN
        """)
            .lstrip()
            .replace("\n", "\r\n")
        )

        assert str(actual) == expected

    def test_play_parse(self):
        parsed = (
            textwrap.dedent(r"""
            [PLAYLIST]
            ITEM_NO=002
            ITEM000=30,0,0,0,0,\C000000\B000\C032000\Fs3232\T255000000000\K000255000000\WHello World!
            ITEM001=30,0,0,0,0,\C000000\Fs3232\T255000000000\K000255000000\WSLOW DOWN
        """)
            .lstrip()
            .replace("\n", "\r\n")
        )

        play_builder = PlayParser.parse(parsed)

        print(play_builder.build())
        
        assert str(play_builder.build()) == parsed
