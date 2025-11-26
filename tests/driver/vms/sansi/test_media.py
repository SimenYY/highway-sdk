import textwrap
from highway_sdk.driver.vms.sansi.media import PlayFactory


def test_play_facotry():
    pf = PlayFactory("multiple")
    with pf.get_play_builder() as pb:
        with pb.new_window(w=512, h=300) as wb:
            with wb.new_item(300, 1) as ib:
                ib.add_image_media("bmp", file_name="008")
            with wb.new_item(300, 1) as ib:
                ib.add_image_media("bmp", file_name="009")
        with pb.new_window(y=0, w=512, h=84) as wb:
            with wb.new_item(500, 1) as ib:
                ib.add_text_media("文本测试")
    actual = pf.get_play()

    expected = (
        textwrap.dedent(r"""
        [playlist]
        nwindows=2
        windows0_x=0
        windows0_y=0
        windows0_w=512
        windows0_h=300
        item_no=2
        item0=300,1,0,\C000000\B008
        item1=300,1,0,\C000000\B009
        windows1_x=0
        windows1_y=0
        windows1_w=512
        windows1_h=84
        windows1_item_no=1
        windows1_item0=500,1,0,\C000000\fh1616\c255255000000\b000000000000文本测试
    """)
        .lstrip()
        .replace("\n", "\r\n")
    )
    assert str(actual) == expected
