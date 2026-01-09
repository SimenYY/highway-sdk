from highway_sdk.vendors.vms.xianke.factory import FrameFactory


def test_frame_factory():
    # 测试获取播放项 - 对应协议文档中的例子
    frame = FrameFactory.get_play_item()
    expected_hex = "02 32 34 30 30 EB 22 03"
    assert bytes(frame) == bytes.fromhex(expected_hex)

    # 测试下载播放表 - 对应协议文档中的例子
    frame = FrameFactory.download_file(file_name="list\\000.xkl")
    expected_hex = "02 32 31 30 30 30 31 32 6C 69 73 74 5C 30 30 30 2E 78 6B 6C 30 30 30 30 3A 87 03"
    assert bytes(frame) == bytes.fromhex(expected_hex)