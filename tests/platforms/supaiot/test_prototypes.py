from highway_sdk.platform.supaiot.prototypes import Vms, Csls


class TestPrototype:
    def test_csls_serialize(self):
        content = {"KZCT": "80"}
        csls = Csls(**content)

        expected = {
            "CT": "",
        }
        assert csls.model_dump(by_alias=True, exclude_none=True) == expected

    def test_vms_serialize(self):
        content = {
            "KFC1": "2",
            "KFO1": "107",
            "KSH1": "1",
            "KTI1": "10",
            "KZCT1": "车道关闭",
            "KFC2": "2",
            "KFO2": "107",
            "KSH2": "1",
            "KTI2": "10",
            "KZCT2": "车道关闭",
        }
        vms = Vms.create_from_tags(content)

        expected = {
            "realtime_content": "",
            "items": [
                {
                    "font_color": "2",
                    "font": "107",
                    "play_mode": 1,
                    "duration": 10,
                    "play_content": "车道关闭",
                },
                {
                    "font_color": "2",
                    "font": "107",
                    "play_mode": 1,
                    "duration": 10,
                    "play_content": "车道关闭",
                },
            ],
        }
        assert vms.model_dump() == expected

        expected_json = '{"CT":"","FC1":"2","FO1":"107","SH1":1,"TI1":10,"ZCT1":"车道关闭","FC2":"2","FO2":"107","SH2":1,"TI2":10,"ZCT2":"车道关闭"}'

        assert vms.model_dump_json() == expected_json
