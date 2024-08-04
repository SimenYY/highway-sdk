#!/usr/bin/env python
# -*- coding: utf-8 -*-
import setuptools
from pkg_resources import parse_requirements

with open("README.md", 'r', encoding='utf-8') as f:
    long_description = f.read()

with open("requirements.txt", 'r', encoding='utf-8') as f:
    install_requires = [str(requirement) for requirement in parse_requirements(f.read())]

# 所有支持的分类列表 https://pypi.org/pypi?%3Aaction=list_classifiers
setuptools.setup(
    name="highway_sdk",
    version="0.1.1",
    auther="AdzLovelace",
    description="Python SDK for Highway commonly used mechanical and electrical device and intelligent device.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license=' GPL-3.0',
    python_requires='>=3.6',  # 没有验证
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        "License :: OSI Approved :: GNU Free Documentation License (FDL)",
        "Operating System :: OS Independent",
    ],
)
