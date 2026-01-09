from highway_sdk.vendors.vms.dianming.factory import FrameFactory


def test_frame_factory():
    frame = FrameFactory.get_play_item()
    frame.dst_addr = b"\x30\x31"
    expected_hex = "02 30 31 30 31 37 33 CD 7D 03"
    assert bytes(frame) == bytes.fromhex(expected_hex)

    frame = FrameFactory.get_play_list()
    expected_hex = "02 30 30 30 31 35 37 30 30 30 30 30 30 30 30 70 6C 61 79 30 30 2E 6C 73 74 BC 91 03"
    assert bytes(frame) == bytes.fromhex(expected_hex)

    frame = FrameFactory.upload_file(file_name="badpoint.png")
    expected_hex = "02 30 30 30 31 30 37 62 61 64 70 6F 69 6E 74 2E 70 6E 67 2B 30 30 30 30 30 30 30 30 43 C2 03"
    assert bytes(frame) == bytes.fromhex(expected_hex)  