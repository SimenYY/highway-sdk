import textwrap
from highway_sdk.driver.vms.nova.v3_11_5.spec import NovaMsg


class TestNovaMsg:
    """验证请求报文是否正确"""

    def test_make_send_file_name(self):
        actual = NovaMsg.make_send_file_name(file_name="play001.lst", block_size=65535)
        expected = "AA FF FF 11 FF FF 70 6C 61 79 30 30 31 2E 6C 73 74 CC 5A 9B"

        assert actual.hex(" ").upper() == expected

    def test_make_send_file_content(self):
        content = (
            textwrap.dedent("""
                [all]
                items=1
                [item1]
                param=100,1,1,1,0,5,1
                txtext1=0,0,0,280,3,4848,0,0,0,1,0,1,8,0,2,100,1,马尔康欢迎您。,1,1,0,5,5,5""")
            .lstrip()
            .replace("\n", "\r\n")
        )
        actual = NovaMsg.make_send_file_content(
            content=content,
            block_num=1,
        )
        expected = "AA FF FF 13 01 00 5B 61 6C 6C 5D 0D 0A 69 74 65 6D 73 3D 31 0D 0A 5B 69 74 65 6D 31 5D 0D 0A 70 61 72 61 6D 3D 31 30 30 2C 31 2C 31 2C 31 2C 30 2C 35 2C 31 0D 0A 74 78 74 65 78 74 31 3D 30 2C 30 2C 30 2C 32 38 30 2C 33 2C 34 38 34 38 2C 30 2C 30 2C 30 2C 31 2C 30 2C 31 2C 38 2C 30 2C 32 2C 31 30 30 2C 31 2C E9 A9 AC E5 B0 94 E5 BA B7 E6 AC A2 E8 BF 8E E6 82 A8 E3 80 82 2C 31 2C 31 2C 30 2C 35 2C 35 2C 35 CC 83 84"

        assert actual.hex(" ").upper() == expected

    def test_make_play_playlist(self):
        actual = NovaMsg.make_play_playlist(1)
        expected = "AA FF FF 1B 01 CC BF 28"

        assert actual.hex(" ").upper() == expected
        
    def test_make_get_item(self):
        actual = NovaMsg.make_get_item()
        expected = "AA FF FF 2D CC EE 0A"
        
        assert actual.hex(" ").upper() == expected
    def test_make_get_play(self):
        actual = NovaMsg.make_get_play()
        expected = "AA FF FF 3A CC 77 D2"

        assert actual.hex(" ").upper() == expected
        
    def test_get_screen_size(self):
        actual = NovaMsg.make_get_screen_size()
        expected = "AA FF FF 82 CC D9 26"
        
        assert actual.hex(" ").upper() == expected
        
    def test_get_now_brightness(self):
        actual = NovaMsg.make_get_now_brightness()
        expected = "AA FF FF C3 CC 67 79"
        
        assert actual.hex(" ").upper() == expected
    