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
:Time: 2024/8/20 13:58
"""
from dataclasses import dataclass
from .escape import DmEscape
from .crc import CrcUtils
from highway_sdk.core.exceptions import CrcError


@dataclass
class DmPacket:
    """
    帧格式：【起始符1B】【目的地址2B】【源地址2B】【控制码2B】【数据nB】【校验码2B】【结束符1B】
    注：
    1. 校验码校验范围：目的地址，源地址，控制码，数据；发送时先校验后转义，接受时先转义后校验
    """

    what: bytes
    data: bytes
    crc: bytes
    start: bytes = b'\x02'
    dst_addr: bytes = b'\x30\x30'
    src_addr: bytes = b'\x30\x31'
    end: bytes = b'\x03'

    @classmethod
    def pack(cls, what: bytes, data: bytes, **kwargs) -> bytes:
        """
        打包
        :param what: 控制码
        :param data: 数据
        :param kwargs:
        :return:
        """
        if 'dst_addr' in kwargs:
            cls.dst_addr = kwargs['dst_addr']
        if 'src_addr' in kwargs:
            cls.src_addr = kwargs['src_addr']

        to_check = cls.dst_addr
        to_check += cls.src_addr
        to_check += what
        to_check += data

        crc_16 = CrcUtils.DianMing_crc_16_table(to_check)

        out_buffer = cls.start
        out_buffer += DmEscape.byte_to_short(to_check + crc_16.get_bytes())
        out_buffer += cls.end

        return out_buffer

    @classmethod
    def unpack(cls, message: bytes) -> 'DmPacket':
        """
        解包
        :param message:
        :return:
        """
        dst_src_what_data_and_crc = DmEscape.short_to_byte(message[1:-1])
        start = message[:1]
        end = message[-1:]
        crc = dst_src_what_data_and_crc[-2:]
        dst_src_what_and_data = dst_src_what_data_and_crc[:-2]

        crc_16 = CrcUtils.DianMing_crc_16_table(dst_src_what_and_data)
        if crc_16.get_bytes() != crc:
            raise CrcError('crc check failed')
        elif start != cls.start:
            raise CrcError('start error')
        elif end != cls.end:
            raise CrcError('end error')
        else:
            dst_addr = dst_src_what_and_data[:2]
            src_addr = dst_src_what_and_data[2:4]
            what = dst_src_what_and_data[4:6]
            data = dst_src_what_and_data[6:]

        return cls(start=start,
                   dst_addr=dst_addr,
                   src_addr=src_addr,
                   what=what,
                   data=data,
                   crc=crc,
                   end=end)
