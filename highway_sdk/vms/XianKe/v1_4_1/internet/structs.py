#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: structs.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2025/2/17 10:28
"""
from dataclasses import dataclass

from highway_sdk.core.exceptions import CrcError
from highway_sdk.vms.crc import CrcUtils


@dataclass
class XianKePacket:
    """
    显科数据帧格式：【帧头 1B】-【类型 2B】-【地址 2B】-【数据 nB】-【校验 2B】-【帧尾 1B】

    注：
    1. 校验范围：类型+地址+数据
    2. 校验完，发送再转义
    """
    what: bytes
    data: bytes
    address: bytes = b'\x30\x30'
    crc: bytes | None = None
    start: bytes = b'\x02'
    end: bytes = b'\x03'

    def pack(self) -> bytes:
        """
        换成实例函数，提高使用的逻辑性

        :return:
        """
        if self.crc is None:
            self.crc = self._calc_crc()

        escaped = XianKePacket.byte_to_short(self.data + self.crc)

        out_buffer = self.start + self.what + self.address + escaped + self.end

        return out_buffer

    @classmethod
    def unpack(cls, message: bytes) -> 'XianKePacket':
        """
        :raise CrcError
        :param message:
        :return:
        """
        start = message[:1]
        end = message[-1:]
        what = message[1:3]
        address = message[3:5]
        escaped = XianKePacket.short_to_byte(message[5:-1])
        crc = escaped[-2:]
        data = escaped[:-2]

        packet = cls(what=what, address=address, data=data, crc=crc)

        calc_crc = packet._calc_crc()
        if packet.crc != calc_crc:
            raise CrcError(f'crc error: {message.hex()}')
        elif packet.start != start or packet.end != end:
            raise CrcError(f'start or end error: {message.hex()}')
        else:
            return packet

    def _calc_crc(self) -> bytes:
        to_check = self.what + self.address + self.data

        crc_16 = CrcUtils.YingSha_crc_16_table(to_check)

        return crc_16.get_bytes()

    @staticmethod
    def byte_to_short(data: bytes) -> bytes:
        """
        转义作为包的相关功能函数，不在单独分一个转义类

        :param data:
        :return:
        """
        data = data.replace(b'\x1B', b'\x1B\x00')
        data = data.replace(b'\x02', b'\x1B\xE7')
        data = data.replace(b'\x03', b'\x1B\xE8')

        return data

    @staticmethod
    def short_to_byte(data: bytes) -> bytes:
        data = data.replace(b'\x1B\xE7', b'\x02')
        data = data.replace(b'\x1B\xE8', b'\x03')
        data = data.replace(b'\x1B\x00', b'\x1B')

        return data
