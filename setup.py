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
    name="supcon_highway_sdk",
    version="0.1.0",
    auther="He YinYu",
    description="Python SDK for Highway commonly used mechanical and electrical device and intelligent device.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://gitee.com/AdvLoveLace/supcon_highway_sdk.git',
    license='BSD-2-Clause',
    python_requires='>=3.6',
    packages=setuptools.find_packages(exclude=['tests', 'tests.*', 'dist', 'dist.*']),
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
)
