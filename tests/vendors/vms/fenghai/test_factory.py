from highway_sdk.vendors.vms.fenghai.factory import FrameFactory


def test_frame_builder():
    frame = FrameFactory.set_brightness(brightness=15)
    expected_hex = "02 00 00 30 35 31 35 31 35 31 35 07 39 03"
    assert bytes(frame) == bytes.fromhex(expected_hex)

    frame = FrameFactory.download_file()
    expected_hex = "02 00 00 30 39 70 6C 61 79 2E 6C 73 74 2B 00 00 00 00 A3 44 03"
    assert bytes(frame) == bytes.fromhex(expected_hex)

    frame = FrameFactory.get_play_item()
    expected_hex = "02 00 00 39 37 F9 B9 03"
    assert bytes(frame) == bytes.fromhex(expected_hex)