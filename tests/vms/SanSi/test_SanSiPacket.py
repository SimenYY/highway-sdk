#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: test_SanSiPacket.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/8/23 11:36
"""
import pytest
from highway_sdk.vms.SanSi.v4_21_0.internet.structs import SanSiPacketReq, SanSiPacketRsp
from highway_sdk.core.exceptions import CrcError

class TestSanSiPacket:

    def test_unpack_success(self):
        msg = SanSiPacketRsp.unpack(b'\x02\x30\x31\x30\x31\x43\x34\x79\x07\x03')
        start = b'\x02'
        address = b'\x30\x31'
        data = b'\x30\x31\x43\x34'
        crc = b'\x79\x07'
        end = b'\x03'

        assert msg.start == start
        assert msg.address == address
        assert msg.data == data
        assert msg.crc == crc
        assert msg.end == end

    def test_unpack_crc_error(self):

        with pytest.raises(CrcError):
            SanSiPacketRsp.unpack(b'\x02\x30\x31\x30\x31\x43\x34\x79\x08\x03')

    def test_pack(self):
        msg = SanSiPacketReq.pack(what=b'\x30\x31', data=b'')

        excepted_msg = b'\x02\x30\x30\x30\x31\xCA\xAB\x03'

        assert msg == excepted_msg


if __name__ == '__main__':
    pytest.main([__file__])