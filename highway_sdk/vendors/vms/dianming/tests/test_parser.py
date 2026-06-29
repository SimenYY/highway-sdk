from highway_sdk.vendors.vms.dianming.parser import Parser
from highway_sdk.vendors.vms.dianming.spec import Frame


class TestParser:
    """测试解析器"""

    def test_parse_get_brightness_and_mode(self):
        """测试解析获取亮度和控制亮度模式响应"""
        frame = Frame.from_bytes(bytes.fromhex("02 30 31 30 30 32 32 46 46 46 46 46 46 30 31 36 65 03"))

        tags = Parser.parse(frame)
        expect_tags = {
            "mode": 1,
            "brightness": 3,
        }
        assert tags.model_dump(mode="json") == expect_tags

    def test_parse_get_play_item(self):
        frame = Frame.from_bytes(
            bytes.fromhex(
                "02 30 31 30 30 37 34 30 30 30 30 30 31 30 30 30 30 30 30 30 30 30 30 5c 46 6b 34 38 34 38 5c 43 30 31 36 30 31 32 5c 4d 31 30 5c 54 32 35 35 32 35 35 30 30 30 30 30 30 5c 57 b7 a2 c9 fa ca c2 b9 ca 20 b3 b5 bf bf b1 df c8 cb b3 b7 c0 eb bc b4 b1 a8 be af 8b 5d 03"
            )
        )

        tags = Parser.parse(frame)
        print(tags.model_dump(mode="json", exclude_none=True))
        expect_tags = {
            "index": "000",
            "media": "\\Fk4848\\C016012\\M10\\T255255000000\\W发生事故 车靠边人撤离即报警",
            "media_list": [
                {
                    "media": "\\Fk4848\\C016012\\M10\\T255255000000\\W发生事故 车靠边人撤离即报警",
                    "font": "k",
                    "font_size": 4848,
                    "font_color": "255255000000",
                    "word_space": 10,
                    "text": "发生事故 车靠边人撤离即报警",
                }
            ],
            "duration": 100,
            "screen_in_mode": 0,
            "screen_out_mode": 0,
            "play_speed": 0,
            "play_effect": 0,
        }
        assert tags.model_dump(mode="json", exclude_none=True) == expect_tags

        frame = Frame.from_bytes(
            bytes.fromhex(
                "02 30 31 30 31 37 34 30 30 30 30 30 30 35 30 30 30 30 30 30 30 30 30 5C 43 30 30 30 30 30 30 5C 42 30 30 31 5C 43 30 32 34 30 30 30 5C 42 30 30 31 5C 43 30 34 38 30 30 30 5C 42 30 30 31 5C 43 30 37 32 30 30 30 5C 42 30 30 32 5C 43 30 39 36 30 30 30 5C 42 30 30 36 DD 85 03 "
            )
        )
        tags = Parser.parse(frame)
        print(tags.model_dump(mode="json", exclude_none=True))
        expect_tags = {
            "index": "000",
            "media": "\\C000000\\B001\\C024000\\B001\\C048000\\B001\\C072000\\B002\\C096000\\B006",
            "media_list": [
                {"media": "\\C000000\\B001", "bmp": "001"},
                {"media": "\\C024000\\B001", "bmp": "001"},
                {"media": "\\C048000\\B001", "bmp": "001"},
                {"media": "\\C072000\\B002", "bmp": "002"},
                {"media": "\\C096000\\B006", "bmp": "006"},
            ],
            "duration": 50,
            "screen_in_mode": 0,
            "screen_out_mode": 0,
            "play_speed": 0,
            "play_effect": 0,
        }
        assert tags.model_dump(mode="json", exclude_none=True) == expect_tags

    def test_parse_get_play_list(self):
        frame = Frame.from_bytes(
            bytes.fromhex(
                "02 30 31 30 30 35 38 2B 30 30 30 30 30 30 30 30 70 6C 61 79 30 30 2E 6C 73 74 5B 50 4C 41 59 4C 49 53 54 5D 0D 0A 49 54 45 4D 5F 4E 4F 3D 30 30 33 0D 0A 49 54 45 4D 30 30 30 3D 35 30 2C 30 2C 30 2C 30 2C 30 2C 5C 43 30 30 30 30 30 30 5C 46 73 33 32 33 32 5C 54 30 30 30 32 35 35 30 30 30 30 30 30 5C 4B 30 30 30 30 30 30 30 30 30 30 30 30 5C 57 D2 D4 C8 CB CE AA B1 BE 5C 41 B9 D8 B0 AE C9 FA C3 FC 0D 0A 49 54 45 4D 30 30 31 3D 35 30 2C 30 2C 30 2C 30 2C 30 2C 5C 43 30 30 30 30 30 30 5C 46 73 33 32 33 32 5C 54 32 35 35 32 35 35 30 30 30 30 30 30 5C 4B 30 30 30 30 30 30 30 30 30 30 30 30 5C 57 B0 B2 C8 AB B5 DA D2 BB 5C 41 D4 A4 B7 C0 CE AA D6 F7 0D 0A 49 54 45 4D 30 30 32 3D 35 30 2C 30 2C 30 2C 30 2C 30 2C 5C 43 30 30 30 30 30 30 5C 46 73 33 32 33 32 5C 54 32 35 35 30 30 30 30 30 30 30 30 30 5C 4B 30 30 30 30 30 30 30 30 30 30 30 30 5C 57 D7 F1 D5 C2 CA D8 B7 A8 5C 41 B0 B2 C8 AB BC DD CA BB 0D 0A 7F 3C 03"
            )
        )

        tags = Parser.parse(frame)
        print(tags.model_dump(mode="json", exclude_none=True))
        expect_tags = {
            "windows": [
                {
                    "items": [
                        {
                            "media": "\\C000000\\Fs3232\\T000255000000\\K000000000000\\W以人为本\\A关爱生命",
                            "media_list": [
                                {
                                    "media": "\\C000000\\Fs3232\\T000255000000\\K000000000000\\W以人为本\\A关爱生命",
                                    "font": "s",
                                    "font_size": 3232,
                                    "font_color": "000255000000",
                                    "background_color": "000000000000",
                                    "text": "以人为本\\A关爱生命",
                                }
                            ],
                            "duration": 50,
                            "screen_in_mode": 0,
                            "screen_out_mode": 0,
                            "play_speed": 0,
                            "play_effect": 0,
                        },
                        {
                            "media": "\\C000000\\Fs3232\\T255255000000\\K000000000000\\W安全第一\\A预防为主",
                            "media_list": [
                                {
                                    "media": "\\C000000\\Fs3232\\T255255000000\\K000000000000\\W安全第一\\A预防为主",
                                    "font": "s",
                                    "font_size": 3232,
                                    "font_color": "255255000000",
                                    "background_color": "000000000000",
                                    "text": "安全第一\\A预防为主",
                                }
                            ],
                            "duration": 50,
                            "screen_in_mode": 0,
                            "screen_out_mode": 0,
                            "play_speed": 0,
                            "play_effect": 0,
                        },
                        {
                            "media": "\\C000000\\Fs3232\\T255000000000\\K000000000000\\W遵章守法\\A安全驾驶",
                            "media_list": [
                                {
                                    "media": "\\C000000\\Fs3232\\T255000000000\\K000000000000\\W遵章守法\\A安全驾驶",
                                    "font": "s",
                                    "font_size": 3232,
                                    "font_color": "255000000000",
                                    "background_color": "000000000000",
                                    "text": "遵章守法\\A安全驾驶",
                                }
                            ],
                            "duration": 50,
                            "screen_in_mode": 0,
                            "screen_out_mode": 0,
                            "play_speed": 0,
                            "play_effect": 0,
                        },
                    ]
                }
            ]
        }
        assert tags.model_dump(mode="json", exclude_none=True) == expect_tags
