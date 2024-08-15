#!/usr/bin/env python
# -*- coding: utf-8 -*-


from dataclasses import dataclass

from .crc import CrcUtils
from .escape import NovaEscape
from highway_sdk.core.exceptions import CrcError


@dataclass
class NovaPacket:
    """
    Nova数据帧格式：【起始符 1B】-【设备地址 2B】-【指令码 1B】-【数据域 nB】-【结束符 1B】-【校验码 2B】
    注：
    1. 校验码为校验前面全部，包括起始符和结束符
    2. 设备地址默认为0xFFFF
    """
    what: bytes
    data: bytes
    crc: bytes
    address: bytes = b'\xFF\xFF'
    start: bytes = b'\xAA'
    end: bytes = b'\xCC'

    @classmethod
    def pack(cls, what: bytes, data: bytes, **kwargs) -> bytes:
        """
        打包函数
        :param what:
        :param data:
        :param kwargs:
        :return: bytes
        """
        if 'address' in kwargs:
            cls.address = kwargs['address']

        to_check = cls.start
        to_check += cls.address
        to_check += what
        to_check += NovaEscape.byte_to_short(data)
        to_check += cls.end

        crc_16 = CrcUtils.nova_crc_16_table(to_check)

        out_buffer = to_check
        out_buffer += crc_16.l
        out_buffer += crc_16.h

        return out_buffer

    @classmethod
    def unpack(cls, message: bytes) -> 'NovaPacket':
        """
        解包函数
        :raise CrcError
        :param message:
        :return: NovaPacket
        """
        address_what_and_data = message[1:-3]

        start = message[:1]
        end = message[-3:-2]
        crc = message[-2:]

        to_check = start
        to_check += address_what_and_data
        to_check += end

        crc_16 = CrcUtils.nova_crc_16_table(to_check)
        if crc_16.get_reverse_bytes() != crc:
            raise CrcError('crc error')
        else:
            address_what_and_data = NovaEscape.short_to_byte(address_what_and_data)
            address = address_what_and_data[:2]
            what = address_what_and_data[2:3]
            data = address_what_and_data[3:]

        return NovaPacket(start=start,
                          address=address,
                          what=what,
                          data=data,
                          end=end,
                          crc=crc)
