from highway_sdk.vendors.vms.nova.factory import FrameFactory


def test_frame_factory():
    frame = FrameFactory.get_play_item()
    expected_hex = "AA FF FF 2D CC EE 0A"
    assert bytes(frame) == bytes.fromhex(expected_hex)

    frame = FrameFactory.get_play_list()
    expected_hex = "AA FF FF 3A CC 77 D2"
    assert bytes(frame) == bytes.fromhex(expected_hex)
