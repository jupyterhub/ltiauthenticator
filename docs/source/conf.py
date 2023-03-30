# Configuration file for Sphinx to build our documentation to HTML.
#
# Configuration reference: https://www.sphinx-doc.org/en/master/usage/configuration.html
#
# -- Path setup --------------------------------------------------------------
# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))
# -- Project specific imports ------------------------------------------------
import datetime

# -- Sphinx setup function ---------------------------------------------------
# ref: http://www.sphinx-doc.org/en/latest/extdev/tutorial.html#the-setup-function


def setup(app):
    app.add_css_file("custom.css")


# -- General MyST configuration -----------------------------------------------------

# myst_enable_extensions ref: https://myst-parser.readthedocs.io/en/latest/using/syntax-optional.html
myst_enable_extensions = []


# -- Project information -----------------------------------------------------
# ref: https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "LTI Autenticator for JupyterHub"
copyright = f"{datetime.date.today().year}, Project Jupyter Contributors"
author = "Project Jupyter Contributors"


# -- General Sphinx configuration ---------------------------------------------------
# ref: https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.mathjax",
    "sphinx_copybutton",
    "myst_parser",
    "sphinxext.rediraffe",
]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# The master toctree document.
master_doc = "index"

# The suffix(es) of source filenames.
source_suffix = [".md", ".rst"]

# Rediraffe redirects to ensure proper redirection
rediraffe_redirects = {}

myst_heading_anchors = 3

# -- Options for linkcheck builder -------------------------------------------
# ref: http://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-the-linkcheck-builder
linkcheck_ignore = [
    r"(.*)github\.com(.*)#",  # javascript based anchors
    r"(.*)/#%21(.*)/(.*)",  # /#!forum/jupyter - encoded anchor edge case
]
linkcheck_anchors_ignore = [
    "/#!",
    "/#%21",
]


# -- Options for HTML output -------------------------------------------------
# ref: http://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#

html_theme = "pydata_sphinx_theme"
html_theme_options = {
    "github_url": "https://github.com/jupyterhub/ltiauthenticator/",
    "use_edit_page_button": True,
    "icon_links": [],
}
html_context = {
    "github_user": "jupyterhub",
    "github_repo": "ltiauthenticator",
    "github_version": "main",
    "doc_path": "docs/source",
}

html_favicon = "_static/images/logo/favicon.ico"
html_logo = "_static/images/logo/logo.png"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
