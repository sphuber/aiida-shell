"""Configuration file for the Sphinx documentation builder.

This file only contains a selection of the most common options. For a full list see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""
import aiida_shell

project = 'aiida-shell'
copyright = 'Sebastiaan P. Huber 2022 - 2023'
release = aiida_shell.__version__

extensions = [
    'myst_parser',
    'sphinx_copybutton',
    'sphinx_click',
    'sphinx_design',
    'sphinx.ext.intersphinx',
    'sphinx_favicon',
]

html_theme = 'pydata_sphinx_theme'
html_theme_options = {
    'pygment_light_style': 'abap',
    'pygment_dark_style': 'nord',
    'use_edit_page_button': True,
    'navbar_align': 'left',
    'github_url': 'https://github.com/sphuber/aiida-shell',
    'logo': {
        'image_light': '_static/logo-text.svg',
        'image_dark': '_static/logo-text-light.svg',
    },
    'favicons': [
        {
            'rel': 'icon',
            'href': 'logo-shell.svg',
        },
    ],
}
html_context = {
    'github_user': 'sphuber',
    'github_repo': 'aiida-shell',
    'github_version': 'master',
}
html_static_path = ['_static']
html_css_files = [
    'custom.css',
]
html_domain_indices = True
html_sidebars = {
    'examples': [],
    'examples/*': [],
}

myst_enable_extensions = [
    'attrs_inline',
    'colon_fence',
    'deflist',
    'substitution',
]

myst_substitutions = {
    'logo_shell': '<img src="_static/logo-shell.svg" alt="aiida-shell" class="logo-shell">',
}


# Settings for the `sphinx_copybutton` extension
copybutton_selector = 'div:not(.no-copy)>div.highlight pre'
copybutton_prompt_text = r'>>> |\.\.\. |(?:\(.*\) )?\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: '
copybutton_prompt_is_regexp = True

# Settings for the `sphinx.ext.intersphinx` extension
intersphinx_mapping = {
    'aiida': ('http://aiida.readthedocs.io/en/latest/', None),
}
