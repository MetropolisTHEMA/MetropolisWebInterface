# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
#sys.path.insert(0, os.path.abspath('/Users/ndiayeabass/Desktop/Metropolis/metroweb/metro/'))
sys.path.append(os.path.abspath('../../'))
#os.environ['DJANGO_SETTINGS_MODULE'] = 'metro_project.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'metro_project.settings')
import django
django.setup()

intersphinx_mapping = {
    'http://docs.python.org/': None,
    'https://docs.djangoproject.com/en/stable': 'https://docs.djangoproject.com/en/stable/_objects',
}

# -- Project information -----------------------------------------------------

project = 'Metroplis Docs'
copyright = '2021, Abass NDIAYE'
author = 'Abass NDIAYE'

# The full version, including alpha/beta/rc tags
release = '1.1.0'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
# pip install sphinxcontrib-apidoc
#pip install apidoc
extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.viewcode',
              'sphinx.ext.coverage',
              'sphinx.ext.napoleon',
              'sphinxcontrib_django',
              #'sphinxcontrib.apidoc',
              ]

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

apidoc_module_dir = "/Users/ndiayeabass/Desktop/Metropolis/metroweb/metro/metro_app/"
apidoc_output_dir = "/Users/ndiayeabass/Desktop/Metropolis/metroweb/metro/docs/source"
apidoc_excluded_paths = "/Users/ndiayeabass/Desktop/Metropolis/metroweb/metro/metro_app/migrations"

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [] #["**/*.migrations.rst"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
import sphinx_rtd_theme
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
