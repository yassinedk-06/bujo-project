"""Configuration de Sphinx pour la documentation Bullet Journal."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "Bullet Journal (BuJo)"
author = "Yassine Dhahak"
release = "1.0.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

language = "fr"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "sphinx_rtd_theme"

autodoc_member_order = "bysource"
autodoc_typehints = "description"
suppress_warnings = ["ref.python"]
