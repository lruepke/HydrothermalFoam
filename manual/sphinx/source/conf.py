# -*- coding: utf-8 -*-
#
# Configuration file for the Sphinx documentation builder.
#
# This file does only contain a selection of the most common options. For a
# full list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))
import sys, os
sys.path.append(os.path.abspath('_extensions'))

# -- Project information -----------------------------------------------------

project = 'HydrothermalFoam'
copyright = '2020, Zhikui Guo'
author = 'Zhikui Guo'

# The short X.Y version
version = '1.1'
# The full version, including alpha/beta/rc tags
release = '1.1'


# -- General configuration ---------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.mathjax', 
              'jinja','sphinxcontrib.bibtex',
              'sphinx.ext.graphviz',
              'sphinx.ext.ifconfig',
              'sphinx.ext.todo',
              'sphinx_sitemap',
            #   'sphinx_tabs.tabs', #tab view extension
              'sphinx_inline_tabs',
              ]
sphinx_tabs_nowarn=True
graphviz_output_format='svg'
source_encoding = 'utf-8-sig'
source_suffix = '.rst'
master_doc = 'index'
templates_path = ['_templates']
bibtex_bibfiles = ['manual.bib']
# todo list
# 仅在开发期间使用，发表时将其关闭就不会再文档中出现todo内容了
todo_include_todos=True

# internationalization
language = 'en'
locale_dirs = ['locale/']
gettext_compact = True
gettext_auto_build=True
# Set smartquotes_action to 'qe' to disable Smart Quotes transform of -- and ---
smartquotes_action = 'qe'
# customize OpenFOAM syntax highlight
from sphinx.highlighting import lexers
from _pygments.foam import OpenFOAMLexer
from _pygments.gmsh import GmshLexer
lexers['foam'] = OpenFOAMLexer(startinline=True)
lexers['gmsh'] = GmshLexer(startinline=True)
# default language to highlight source code
highlight_language = 'foam'
pygments_style = 'emacs' # xcode,monokai,emacs,autumn,vs,solarized-dark


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'rtd'
html_theme_path = ["_themes"]
html_theme_options = {
    'sticky_navigation': False,
    'includehidden': False,
    'logo_only' : True,
    'sticky_navigation': True,
    'titles_only': True,
    'display_version': False,
    'prev_next_buttons_location': 'both',
    'style_nav_header_background': 'purple',
    # 'gitlab_url': 'https://gitlab.com/gmdpapers/hydrothermalfoam'
}
html_context = {
    "menu_links": [
        (
            '<i class="fa fa-envelope fa-fw"></i> Contact',
            "mailto:zguo@geomar.de",
            
        ),
        (
            '<img src="https://zenodo.org/static/img/orcid.png" height=14px> Zhikui Guo',
            'https://orcid.org/0000-0002-0604-0455'
        ),
        (
            '<i class="fa fa-book fa-fw"></i> LICENCE',
            "https://gitlab.com/gmdpapers/hydrothermalfoam/-/blob/master/LICENSE",
        ),
        (
            '<i class="fa fa-gitlab fa-fw"></i> Source Code',
            "https://gitlab.com/gmdpapers/hydrothermalfoam",
        ),
        (
            '<img src="https://zenodo.org/badge/DOI/10.5281/zenodo.3755648.svg" alt="DOI">',
            'https://doi.org/10.5281/zenodo.3755648'
        ),
    ],
}

# favicon of the docs
html_favicon = "_static/favicon.png"
html_logo="_static/logo.png"
html_static_path = ['_static']
html_last_updated_fmt = '%b %d, %Y'
# If true, links to the reST sources are added to the pages.
html_show_sourcelink = False
# List of custom CSS files (needs sphinx>=1.8)
html_css_files = ["style.css"]

# Redefine supported_image_types for the HTML builder
from sphinx.builders.html import StandaloneHTMLBuilder
StandaloneHTMLBuilder.supported_image_types = [
  'image/svg+xml', 'image/png', 'image/jpeg', 'image/gif'
]


# -- Options for LaTeX output ---------------------------------------------
latex_engine = 'xelatex'
latex_elements = {
    'papersize': 'a4paper',
    'utf8extra': '',
    'inputenc': '',
    'babel': r'''\usepackage[english]{babel}''',
    'preamble': r'''\usepackage{ctex}
\definecolor{FOAM_green}{rgb}{0.27,0.49,0.36}
\setCJKsansfont{Source Han Sans CN} %为中文和英文设置特定字体
\setsansfont{Source Han Sans CN}
\setmainfont{Arial}
\geometry{
	a4paper, 
	nomarginpar,
	left=1cm,
	right=1cm,
	% top=2cm,
	% bottom=1cm,
	% headsep=0.5cm, %正文到页眉的距离
}
    ''',
}
latex_logo='_static/logo.pdf'
# 设置公式和图片编号依赖于章节
numfig = True 
math_numfig = True
math_eqref_format = '({number})'
# 只对make latex有效
# numfig_format = 'Figure. %s'
numfig_secnum_depth = 1
imgmath_latex = 'dvilualatex'
imgmath_image_format = 'svg'
imgmath_dvipng_args = ['-gamma', '1.5', '-bg', 'Transparent']
# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'HydrothermalFoam.tex', 'HydrothermalFoam Manual',
     'Zhikui Guo, Lars Rüpke, Chunhui Tao', 'manual'),
]


# -- Options for manual page output ------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'hydrothermalfoam', 'HydrothermalFoam Manual',
     [author], 1)
]


# -- Options for Texinfo output ----------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'HydrothermalFoam', 'HydrothermalFoam Documentation',
     author, 'HydrothermalFoam', 'One line description of project.',
     'Miscellaneous'),
]

# def setup(app):
#     # app.add_stylesheet("style.css")
#     # app.add_javascript("js/custom.js")
#     app.add_javascript(
#         "https://cdn.jsdelivr.net/npm/clipboard@1/dist/clipboard.min.js")
    
# new defined cite style
from pybtex.style.formatting.unsrt import Style as UnsrtStyle
from pybtex.plugin import register_plugin
from collections import Counter
import re
import unicodedata

from pybtex.style.labels import BaseLabelStyle

_nonalnum_pattern = re.compile('[^A-Za-z0-9 \-]+', re.UNICODE)

def _strip_accents(s):
    return "".join(
        (c for c in unicodedata.normalize('NFD', s)
            if not unicodedata.combining(c)))

def _strip_nonalnum(parts):
    """Strip all non-alphanumerical characters from a list of strings.

    >>> print(_strip_nonalnum([u"ÅA. B. Testing 12+}[.@~_", u" 3%"]))
    AABTesting123
    """
    s = "".join(parts)
    return _nonalnum_pattern.sub("", _strip_accents(s))

class APALabelStyle(BaseLabelStyle):
    def format_labels(self, sorted_entries):
        labels = [self.format_label(entry) for entry in sorted_entries]
        count = Counter(labels)
        counted = Counter()
        for label in labels:
            if count[label] == 1:
                yield label
            else:
                yield label + chr(ord('a') + counted[label])
                counted.update([label])

    def format_label(self, entry):
        label = "Anonymous"
        if 'author' in entry.persons:
            label = self.format_author_or_editor_names(entry.persons['author'])
        elif 'editor' in entry.persons:
            label = self.format_author_or_editor_names(entry.persons['editor'])
        elif 'organization' in entry.fields:
            label = entry.fields['organization']
            if label.startswith("The "):
                label = label[4:]

        if 'year' in entry.fields:
            return "{}, {}".format(label, entry.fields['year'])
        else:
            return "{}, n.d.".format(label)

    def format_author_or_editor_names(self, persons):
        if len(persons) is 1:
            return _strip_nonalnum(persons[0].last_names)
        elif len(persons) is 2:
            return "{} & {}".format(
                _strip_nonalnum(persons[0].last_names),
                _strip_nonalnum(persons[1].last_names))
        else:
            return "{} et al.".format(
                _strip_nonalnum(persons[0].last_names))

class APAStyle(UnsrtStyle):

    default_label_style = APALabelStyle

register_plugin('pybtex.style.formatting', 'apa', APAStyle)
# # ====================================================================