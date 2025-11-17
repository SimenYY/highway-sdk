import textwrap
from highway_sdk.driver.vms.xianke.spec import XianKeMsgBuilder


class TestXiankeMsg:
    def test_make_upload_file(self):
        content = (
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
        actual = XianKeMsgBuilder.build_upload_file(content, file_name="list\\000.xkl")
        expected = "02 32 30 30 30 31 30 30 31 32 6C 69 73 74 5C 30 30 30 2E 78 6B 6C 30 30 30 30 5B 4C 49 53 54 5D 0D 0A 49 74 65 6D 43 6F 75 6E 74 3D 30 30 32 0D 0A 49 74 65 6D 30 30 3D 32 2C 31 2C 30 2C 31 2C 31 2C 5C 43 30 30 30 30 30 30 5C 46 73 33 32 5C 54 32 35 35 30 30 30 30 30 30 30 30 30 5C 42 30 30 30 30 30 30 30 30 30 30 30 30 5C 55 C9 EE DB DA CF D4 BF C6 BF C6 BC BC D3 D0 CF DE B9 AB CB BE 0D 0A 49 74 65 6D 30 31 3D 32 2C 31 2C 30 2C 31 2C 31 2C 5C 43 30 30 30 30 30 30 5C 46 73 33 32 5C 54 30 30 30 32 35 35 30 30 30 30 30 30 5C 42 30 30 30 30 30 30 30 30 30 30 30 30 5C 55 C9 EE DB DA CF D4 BF C6 BF C6 BC BC D3 D0 CF DE B9 AB CB BE 0D 0A 4D EF 03"
        # print(bytes.fromhex(expected).decode("gbk", "ignore"))
        # print(f"actual: {actual.hex(' ').upper()}")
        # print(f"expected: {expected}")
        assert actual.hex(" ").upper() == expected

    def test_make_download_file(self):
        actual = XianKeMsgBuilder.build_download_file(file_name="list\\000.xkl")

        expected = "02 32 31 30 30 30 31 32 6C 69 73 74 5C 30 30 30 2E 78 6B 6C 30 30 30 30 3A 87 03"

        assert actual.hex(" ").upper() == expected

    def test_play_playlist(self):
        actual = XianKeMsgBuilder.build_play_list(file_name="000.xkl")

        excepted = "02 32 32 30 30 30 30 30 2E 78 6B 6C 7A 93 03"

        assert actual.hex(" ").upper() == excepted

    def test_make_get_item(self):
        actual = XianKeMsgBuilder.build_get_item()

        expected = "02 32 34 30 30 EB 22 03"

        assert actual.hex(" ").upper() == expected

    def test_get_play(self):
        actual = XianKeMsgBuilder.build_get_play()

        expected = "02 32 33 30 30 6E B2 03"

        assert actual.hex(" ").upper() == expected

    def test_get_now_brightness(self):
        actual = XianKeMsgBuilder.build_get_brightness()
        expected = "02 30 35 30 30 31 7A 03"
        assert actual.hex(" ").upper() == expected
