"""Codec 编解码器测试。"""

import pytest

from highway_sdk.core.codec import BaseCodec
from highway_sdk.core.frame import BaseFrame
from highway_sdk.core.tags import BaseTags


class ItemTags(BaseTags):
    """测试用数据标签。"""

    text: str = ""


class MockFrame(BaseFrame):
    """测试用帧。"""

    @classmethod
    def from_bytes(cls, message: bytes) -> "MockFrame":
        return cls(what=message[:8], data=message[8:])

    def __bytes__(self) -> bytes:
        return self.what + self.data


class TestCodec(BaseCodec):
    """测试用编解码器。"""

    @classmethod
    @BaseCodec.register(b"test_cmd")
    def decode_test(cls, data: bytes) -> ItemTags:
        """解码测试命令。"""
        return ItemTags(text=data.decode("utf-8"))


class TestBaseCodec:
    """BaseCodec 类测试。"""

    def test_register_decorator(self):
        """测试装饰器注册。"""
        assert b"test_cmd" in TestCodec._decoders

    def test_decode_success(self):
        """测试成功解码。"""
        frame = MockFrame(what=b"test_cmd", data=b"hello")
        result = TestCodec.decode(frame)

        assert isinstance(result, ItemTags)
        assert result.text == "hello"

    def test_decode_unsupported_command(self):
        """测试不支持的命令。"""
        frame = MockFrame(what=b"unknown_cmd", data=b"test")

        with pytest.raises(ValueError, match="Unsupported command"):
            TestCodec.decode(frame)

    def test_register_multiple_commands(self):
        """测试注册多个命令。"""

        class MultiCodec(BaseCodec):
            @classmethod
            @BaseCodec.register(b"cmd1")
            def decode_cmd1(cls, data: bytes) -> ItemTags:
                return ItemTags(text="cmd1")

            @classmethod
            @BaseCodec.register(b"cmd2")
            def decode_cmd2(cls, data: bytes) -> ItemTags:
                return ItemTags(text="cmd2")

        assert b"cmd1" in MultiCodec._decoders
        assert b"cmd2" in MultiCodec._decoders

        frame1 = MockFrame(what=b"cmd1", data=b"")
        frame2 = MockFrame(what=b"cmd2", data=b"")

        assert MultiCodec.decode(frame1).text == "cmd1"
        assert MultiCodec.decode(frame2).text == "cmd2"
