import textwrap
from highway_sdk.vendors.vms.nova.media import (
    TextMediaBuilder,
    ImageMediaBuilder,
    TextextMediaBuilder,
    WebMediaBuilder,
    PlayParser,
    PlayBuilder,
    ItemBuilder,
)



class TestPlayBuiler:
    def test_textext_media_display(self):
        pb = PlayBuilder()

        ib_1 = ItemBuilder()
        tb_1 = TextextMediaBuilder()
        tb_1.text = "文本测试1"
        ib_1.add_media_builder(tb_1)

        tb_2 = TextextMediaBuilder()
        tb_2.text = "文本测试2"
        ib_1.add_media_builder(tb_2)
        pb.add_item_builder(ib_1)

        ib_2 = ItemBuilder()
        tb_3 = TextextMediaBuilder()
        tb_3.text = "文本测试3"
        ib_2.add_media_builder(tb_1)
        pb.add_item_builder(ib_2)

        actual = str(pb.build())
        expected = textwrap.dedent("""
            [all]
            items=2
            [item1]
            param=100,1,1,1,0,5,1
            txtext1=0,0,0,0,1,1616,0,2,2,1,0,1,8,0,2,100,1,文本测试1,0,0,0,5,5,5
            txtext2=0,0,0,0,1,1616,0,2,2,1,0,1,8,0,2,100,1,文本测试2,0,0,0,5,5,5
            [item2]
            param=100,1,1,1,0,5,1
            txtext1=0,0,0,0,1,1616,0,2,2,1,0,1,8,0,2,100,1,文本测试1,0,0,0,5,5,5
        """).lstrip().replace("\n", "\r\n")
        print(actual)
        assert actual == expected
    
    def test_image_media_display(self):
        pb = PlayBuilder()
        ib_1 = ItemBuilder()
        imb_1 = ImageMediaBuilder()
        imb_1.file_path = "test.png"
        ib_1.add_media_builder(imb_1)
        
        imb_2 = ImageMediaBuilder()
        imb_2.file_path = "test.png"
        ib_1.add_media_builder(imb_2)
        pb.add_item_builder(ib_1)
        
        actual = str(pb.build())
        
        expected = textwrap.dedent("""
            [all]
            items=1
            [item1]
            param=100,1,1,1,0,5,1
            img1=0,0,test.png,0,0,0
            imgparam1=100,0,00,1,1
            img2=0,0,test.png,0,0,0
            imgparam2=100,0,00,1,1
        """).lstrip().replace("\n", "\r\n")
        print(actual)
        assert actual == expected
        
    
    def test_text_media_display(self):
        
        pb = PlayBuilder()
        ib_1 = ItemBuilder()
        tb_1 = TextMediaBuilder()
        tb_1.text = "文本测试1"
        ib_1.add_media_builder(tb_1)
        tb_2 = TextMediaBuilder()
        tb_2.text = "文本测试2"
        ib_1.add_media_builder(tb_2)
        pb.add_item_builder(ib_1)
        
        actual = str(pb.build())
        
        expected = textwrap.dedent("""
            [all]
            items=1
            [item1]
            param=100,1,1,1,0,5,1
            txt1=0,0,1,1616,1,8,0,文本测试1,0,0,0
            txtparam1=0,0
            txt2=0,0,1,1616,1,8,0,文本测试2,0,0,0
            txtparam2=0,0
        """).lstrip().replace("\n", "\r\n")
        print(actual)
        assert actual == expected
        
    def test_web_media_display(self):
        pb = PlayBuilder()
        ib_1 = ItemBuilder()
        wmb_1 = WebMediaBuilder()
        wmb_1.url = "https://www.baidu.com"
        ib_1.add_media_builder(wmb_1)
        pb.add_item_builder(ib_1)
        
        actual = str(pb.build())
        
        expected = textwrap.dedent("""
            [all]
            items=1
            [item1]
            param=100,1,1,1,0,5,1
            webview1=0,0,https://www.baidu.com/,0,0,0
        """).lstrip().replace("\n", "\r\n")
        print(actual)
        
        assert actual == expected
        


class TestPlayParser:
    
    def test_play_parse(self):

        parsed = textwrap.dedent("""
            [all]
            items=5
            [item1]
            param=100,1,1,1,0,5,1
            txtext1=0,0,0,0,1,1616,0,2,2,1,0,1,8,0,2,100,1,文本测试1,0,0,0,5,5,5
            txtext2=0,0,0,0,1,1616,0,2,2,1,0,1,8,0,2,100,1,文本测试2,0,0,0,5,5,5
            [item2]
            param=100,1,1,1,0,5,1
            txtext1=0,0,0,0,1,1616,0,2,2,1,0,1,8,0,2,100,1,文本测试1,0,0,0,5,5,5
            [item3]
            param=100,1,1,1,0,5,1
            txt1=0,0,1,1616,1,8,0,文本测试1,0,0,0
            txtparam1=0,0
            txt2=0,0,1,1616,1,8,0,文本测试2,0,0,0
            txtparam2=0,0
            [item4]
            param=100,1,1,1,0,5,1
            img1=0,0,test.png,0,0,0
            imgparam1=100,0,00,1,1
            img2=0,0,test.png,0,0,0
            imgparam2=100,0,00,1,1
            [item5]
            param=100,1,1,1,0,5,1
            webview1=0,0,https://www.baidu.com/,0,0,0
        """).lstrip().replace("\n", "\r\n")
        
        play_builder = PlayParser.parse(parsed)
        
        assert len(play_builder._item_list) == 5
        
        item1, item2, item3, item4, item5 = play_builder._item_list
    
        expected = textwrap.dedent("""
            [item1]
            param=100,1,1,1,0,5,1
            txtext1=0,0,0,0,1,1616,0,2,2,1,0,1,8,0,2,100,1,文本测试1,0,0,0,5,5,5
            txtext2=0,0,0,0,1,1616,0,2,2,1,0,1,8,0,2,100,1,文本测试2,0,0,0,5,5,5
        """).lstrip().replace("\n", "\r\n")
        # print(str(item1))
        assert str(item1) == expected
        
        expected = textwrap.dedent("""
            [item2]
            param=100,1,1,1,0,5,1
            txtext1=0,0,0,0,1,1616,0,2,2,1,0,1,8,0,2,100,1,文本测试1,0,0,0,5,5,5
        """).lstrip().replace("\n", "\r\n")
        assert str(item2) == expected
        
        # print(str(item3))
        expected = textwrap.dedent("""
            [item3]
            param=100,1,1,1,0,5,1
            txt1=0,0,1,1616,1,8,0,文本测试1,0,0,0
            txtparam1=0,0
            txt2=0,0,1,1616,1,8,0,文本测试2,0,0,0
            txtparam2=0,0
        """).lstrip().replace("\n", "\r\n")
        assert str(item3) == expected   
        
        expected = textwrap.dedent("""
            [item4]
            param=100,1,1,1,0,5,1
            img1=0,0,test.png,0,0,0
            imgparam1=100,0,00,1,1
            img2=0,0,test.png,0,0,0
            imgparam2=100,0,00,1,1
        """).lstrip().replace("\n", "\r\n")
        assert str(item4) == expected

        # TODO 网址媒体测试