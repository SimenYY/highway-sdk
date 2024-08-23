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
:Time: 2024/8/22 9:20
"""
from dataclasses import dataclass
from .crc import CrcUtils
from .escape import SanSiEscape
from highway_sdk.core.exceptions import CrcError


@dataclass
class SanSiPacketRsp:
    """
    帧格式：【帧头1B】【地址2B】【帧数据nB】【帧校验2B】【帧尾1B】
    注
    1. 先转义，后校验
    """
    data: bytes
    crc: bytes
    start: bytes = b'\x02'
    address: bytes = b'\x30\x30'
    end: bytes = b'\x03'

    @classmethod
    def unpack(cls, message: bytes) -> 'SanSiPacketRsp':
        """
        解包
        :param message:
        :return:
        """
        data_crc = message[3:-1]
        escaped_data_crc = SanSiEscape.short_to_byte(data_crc)
        start = message[:1]
        end = message[-1:]
        address = message[1:3]
        crc = escaped_data_crc[-2:]
        data = escaped_data_crc[:-2]

        crc_16 = CrcUtils.SanSi_crc_16_table(address + data)
        if crc_16.get_bytes() != crc:
            raise CrcError('crc check failed')
        elif start != cls.start:
            raise CrcError('start error')
        elif end != cls.end:
            raise CrcError('end error')
        else:
            return cls(start=start,
                       address=address,
                       data=data,
                       crc=crc,
                       end=end)


@dataclass
class SanSiPacketReq:
    """
    帧格式：【帧头1B】【地址2B】【帧类型2B】【帧数据nB】【帧校验2B】【帧尾1B】
    注
    1. 对地址，类型，数据进行校验
    2.先校验，后转义
    """
    what: bytes
    data: bytes
    crc: bytes
    start: bytes = b'\x02'
    address: bytes = b'\x30\x30'
    end: bytes = b'\x03'

    @classmethod
    def pack(cls, what: bytes, data: bytes, **kwargs) -> bytes:
        """
        打包
        :param what:
        :param data:
        :param kwargs:
        :return:
        """
        if 'address' in kwargs:
            cls.address = kwargs['address']

        to_check = cls.address
        to_check += what
        to_check += data

        crc_16 = CrcUtils.SanSi_crc_16_table(to_check)

        escaped_data_crc = SanSiEscape.byte_to_short(data + crc_16.get_bytes())

        out_buffer = cls.start
        out_buffer += cls.address
        out_buffer += what
        out_buffer += escaped_data_crc
        out_buffer += cls.end

        return out_buffer
