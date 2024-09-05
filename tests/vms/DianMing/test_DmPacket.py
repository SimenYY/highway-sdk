#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: test_DmPacket.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/8/20 14:42
"""
import pytest
from highway_sdk.vms.DianMing.v2_3_0.internet.utils.structs import DmPacket


class TestNovaPacket:

    def test_pack_with_empty_data(self):
        what = b'\x37\x33'
        data = b''
        pack = DmPacket.pack(what, data, dst_addr=b'\x30\x31')
        expected_pack = b'\x02\x30\x31\x30\x31\x37\x33\xCD\x7D\x03'
        assert pack == expected_pack

    def test_unpack_with_empty_data(self):
        example_message = b'\x02\x30\x31\x30\x31\x37\x33\xCD\x7D\x03'
        unpack = DmPacket.unpack(example_message)

        assert unpack.start == b'\x02'
        assert unpack.dst_addr == b'\x30\x31'
        assert unpack.src_addr == b'\x30\x31'
        assert unpack.what == b'\x37\x33'
        assert unpack.data == b''
        assert unpack.crc == b'\xCD\x7D'
        assert unpack.end == b'\x03'


if __name__ == '__main__':
    pytest.main([__file__])
