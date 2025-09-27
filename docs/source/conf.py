
import os
import sys
sys.path.insert(0, os.path.abspath('../../src'))

# -- Project info --
project = 'Evidence Extractor'
copyright = '2025, Ryen-X'
author = 'Ryen-X'
release = '0.0.1'

# -- General configuration --
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
]
templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output --
html_theme = 'furo'
html_static_path = ['_static']
html_title = "Evidence Extractor Documentation"