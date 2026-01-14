# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Highway SDK"
copyright = "2026, AdzLovelace"
author = "AdzLovelace"
release = "2.0.0"

# -- General configuration ---------------------------------------------------# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

import os
import sys

sys.path.insert(0, os.path.abspath("../../"))

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
html_static_path = ["_static"]

# 主题配置
html_theme_options = {
    "sidebar_hide_name": True,
    "light_logo": "logo.png",
    "dark_logo": "logo.png",
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
    "inherited-members": True,
}

autodoc_member_order = "bysource"
autoclass_content = "both"
