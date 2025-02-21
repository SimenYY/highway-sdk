# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'highway_sdk'
copyright = '2025, Adv Lovelace'
author = 'Adv Lovelace'
release = '1.20.3'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',  # 自动生成文档
    'sphinx.ext.viewcode',  # 显示源代码链接
    'sphinx.ext.napoleon',  # 支持 Google 和 NumPy 风格的 docstring
    'sphinx.ext.doctest',  # 包含测试片段
    'sphinx.ext.todo',  # 包含todo项
    'sphinx.ext.coverage',  # 文档覆盖率统计
    'sphinx.ext.mathjax',  # 通过javascript呈现数学
    'sphinx_copybutton',  # 为代码块添加复制按钮
    'sphinx_tabs.tabs',  # 添加选项卡内容
    'sphinx.ext.doctest',  # 启用doctest扩展
]
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'zh_CN'

todo_include_todos = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
