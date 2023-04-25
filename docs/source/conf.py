# -*- coding: utf-8 -*-
"""Configuration file for the Sphinx documentation builder.

This file only contains a selection of the most common options. For a full list see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""
# pylint: disable=invalid-name
import aiida_shell

project = 'aiida-shell'
copyright = 'Sebastiaan P. Huber 2022 - 2023'  # pylint: disable=redefined-builtin
release = aiida_shell.__version__

extensions = ['sphinx_copybutton', 'sphinx_click', 'sphinx.ext.intersphinx']

html_theme = 'sphinx_book_theme'
html_theme_options = {
    'home_page_in_toc': True,
    'repository_url': 'https://github.com/sphuber/aiida-shell',
    'repository_branch': 'master',
    'use_repository_button': True,
    'use_issues_button': True,
    'use_fullscreen_button': False,
    'path_to_docs': 'docs',
    'use_edit_page_button': True,
}
html_domain_indices = True
html_logo = 'images/logo-column.png'

# Settings for the `sphinx_copybutton` extension
copybutton_selector = 'div:not(.no-copy)>div.highlight pre'
copybutton_prompt_text = r'>>> |\.\.\. |(?:\(.*\) )?\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: '
copybutton_prompt_is_regexp = True

# Settings for the `sphinx.ext.intersphinx` extension
intersphinx_mapping = {
    'aiida': ('http://aiida.readthedocs.io/en/latest/', None),
}
