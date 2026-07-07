# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

sys.path.insert(0, os.path.abspath("../../"))

# -- Project information -----------------------------------------------------# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Highway SDK"
copyright = "2026, AdzLovelace"
author = "AdzLovelace"
release = "3.1.0"

# -- General configuration ---------------------------------------------------# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "sphinx_tabs.tabs",
]

templates_path = ["_templates"]
exclude_patterns = []

language = "zh_CN"

# -- Options for HTML output -------------------------------------------------# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
# 暂无静态资源；如后续添加 logo/图标，请创建 docs/source/_static/ 目录并恢复 html_static_path。

# 主题配置
html_theme_options = {
    "sidebar_hide_name": True,
    "light_css_variables": {
        "color-brand-primary": "#336791",
        "color-brand-content": "#336791",
    },
    "dark_css_variables": {
        "color-brand-primary": "#336791",
        "color-brand-content": "#336791",
    },
}

# 自动文档配置
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "private-members": False,
    "show-inheritance": True,
    # 不渲染继承成员：避免 Pydantic BaseModel 的 model_dump/model_dump_json 等
    # 方法因 RST 不兼容的 docstring 产生数百条警告。
    # 单个类如需展示继承成员，在 autoclass 指令上显式加 :inherited-members:。
    "inherited-members": False,
}

autodoc_member_order = "bysource"
autoclass_content = "both"

# 抑制已知非阻塞警告类型（不阻塞构建，但减少噪音）
suppress_warnings = [
    # pydantic 部分魔法方法即使在 inherited-members=False 时也会触发微格式警告
    "docutils",
]
