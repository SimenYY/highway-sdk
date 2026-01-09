from highway_sdk.vendors.vms.sansi.factory import FrameFactory


def test_frame_factory():
    frame = FrameFactory.get_play_item()
    expected_hex = "02 30 30 39 37 10 F5 03"
    assert bytes.fromhex(expected_hex) == bytes(frame)

    frame = FrameFactory.download_file()
    expected_hex = "02 30 30 30 39 70 6C 61 79 2E 6C 73 74 00 00 00 00 57 2A 03"
    assert bytes.fromhex(expected_hex) == bytes(frame)
