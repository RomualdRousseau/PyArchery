# ruff: noqa: F401, E402
"""PyArchery: Python binding to the Archery document parsing library."""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

from .setup_java import is_jvm_started, start_java_archery_framework

if TYPE_CHECKING:
    from .archery import (  # pragma: no cover
        CAMEL,
        INTELLI_EXTRACT,
        INTELLI_LAYOUT,
        INTELLI_TAG,
        INTELLI_TIME,
        SNAKE,
        DataTable,
        DocumentFactory,
        LayexTableParser,
        Model,
        ModelBuilder,
        TableGraph,
    )
    from .wrappers import DocumentWrapper  # pragma: no cover


_ARCHERY_MODULE = None
_WRAPPERS_MODULE = None


def _archery():
    """Lazily import the archery module after ensuring JVM is started."""
    global _ARCHERY_MODULE
    if _ARCHERY_MODULE is None:
        start_java_archery_framework()
        _ARCHERY_MODULE = importlib.import_module(".archery", __name__)
    return _ARCHERY_MODULE


def _wrappers():
    """Lazily import wrappers (depends on archery being loaded)."""
    global _WRAPPERS_MODULE
    if _WRAPPERS_MODULE is None:
        _archery()
        _WRAPPERS_MODULE = importlib.import_module(".wrappers", __name__)
    return _WRAPPERS_MODULE


def model_from_path(path: str) -> Model:
    """Create a ModelBuilder from a file path."""
    return _archery().ModelBuilder().fromPath(path)


def model_from_url(url: str) -> Model:
    """Create a ModelBuilder from a URL."""
    return _archery().ModelBuilder().fromURL(url)


def model_from_json(data: str) -> Model:
    """Create a ModelBuilder from a JSON string."""
    return _archery().ModelBuilder().fromJSON(data)


def load(
    file_path: str,
    encoding: str = "UTF-8",
    model=None,
    hints=None,
    recipe=None,
    tag_case: str | None = None,
) -> DocumentWrapper:
    """Load a document and create a DocumentWrapper."""
    archery = _archery()
    wrappers = _wrappers()

    doc = archery.DocumentFactory.createInstance(file_path, encoding)
    if model:
        doc.setModel(model)
    if hints:
        doc.setHints(hints)
    if recipe:
        doc.setRecipe("\n".join(recipe))
    if tag_case:
        if tag_case == "SNAKE":
            doc.getTagClassifier().setTagStyle(archery.SNAKE)
        elif tag_case == "CAMEL":
            doc.getTagClassifier().setTagStyle(archery.CAMEL)
    return wrappers.DocumentWrapper(doc)


def __getattr__(name: str):
    archery = _archery()
    if hasattr(archery, name):
        return getattr(archery, name)
    if name == "DocumentWrapper":
        _archery()
        return _wrappers().DocumentWrapper
    raise AttributeError(name)


def __dir__():
    archery = _archery()
    return sorted(set(list(globals().keys()) + dir(archery) + ["DocumentWrapper"]))
