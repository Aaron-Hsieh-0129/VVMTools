import os
import sys
sys.path.insert(0, os.path.abspath('../../vvmtools'))


# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'vvmtools'
copyright = '2024, Aaron Hsieh'
author = 'Aaron Hsieh'
release = 'v0.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',  # For Google-style or NumPy-style docstrings
    'sphinx.ext.viewcode',   # For including links to source code
    'sphinx.ext.autosummary',  # Generates summary tables for modules/classes
    'numpydoc'
]

templates_path = ['_templates']
exclude_patterns = []

autosummary_generate = True  # Enable autosummary to generate files automatically

# To customize how types are presented in the documentation
autodoc_mock_imports = ['vvmtools']
autodoc_typehints = 'description'
autodoc_default_options = {
    'members': True,  # Include all members
    'member-order': 'bysource',
    'undoc-members': True,  # Include members without docstrings
    'show-inheritance': True,
    'inherited-members': True,
}

napoleon_google_docstring = False
napoleon_numpy_docstring = True


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_book_theme'
html_theme_options = {
    "repository_url": "https://github.com/Aaron-Hsieh-0129/VVMTools",
    "use_repository_button": True,
}
html_static_path = ['_static']
