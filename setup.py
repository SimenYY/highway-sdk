#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:FileName: setup.py
:Project:
:Brand:
:Version:
:Description: 
:Author: He YinYu
:Link:
:Time: 2024/8/1 19:54
:Department: 公路机电工程技术中心
:Copyright: ©1993-2023 浙江中控信息产业股份有限公司
"""
import setuptools

with open("README.md", 'r', encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name="supcon_highway_sdk",
    version="0.1.0",
    auther="He YinYu",
    description="Python SDK for Highway commonly used mechanical and electrical device and intelligent device.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='',
    python_requires='>=3.10',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU GENERAL PUBLIC LICENSE",
        "Operating System :: OS Independent",
    ],
)
