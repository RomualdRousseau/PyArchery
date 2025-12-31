# ruff: noqa: F401, E402
"""PyArchery: Python binding to the Archery document parsing library."""

from __future__ import annotations

import importlib
import os
from typing import TYPE_CHECKING

from .jvm import is_jvm_started, start_java_archery_framework

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
        SheetEvent,
        TableGraph,
    )
    from .wrappers import DocumentWrapper, SheetWrapper  # pragma: no cover


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
    """Lazily import DocumentWrapper without exposing wrappers via __getattr__."""
    global _WRAPPERS_MODULE
    if _WRAPPERS_MODULE is None:
        _WRAPPERS_MODULE = importlib.import_module(".wrappers", __name__)
    return _WRAPPERS_MODULE


def model_from_path(path: str | os.PathLike[str]) -> ModelBuilder:
    """Create a ModelBuilder from a file path (starts JVM on first use)."""
    return _archery().ModelBuilder().fromPath(os.fspath(path))


def model_from_url(url: str) -> ModelBuilder:
    """Create a ModelBuilder from a URL (starts JVM and fetches remote model)."""
    return _archery().ModelBuilder().fromURL(url)


def model_from_json(data: str) -> ModelBuilder:
    """Create a ModelBuilder from a JSON string (starts JVM on first use)."""
    return _archery().ModelBuilder().fromJSON(data)


def load(
    file_path: str | os.PathLike[str],
    encoding: str = "UTF-8",
    model=None,
    hints=None,
    recipe=None,
    tag_case: str | None = None,
) -> DocumentWrapper:
    """Load a document and create a DocumentWrapper (starts JVM on first use)."""
    archery = _archery()
    file_path_str = os.fspath(file_path)
    if not os.path.isfile(file_path_str):
        raise FileNotFoundError(f"Document not found: {file_path_str}")
    if not os.access(file_path_str, os.R_OK):
        raise PermissionError(f"Document is not readable: {file_path_str}")
    doc = archery.DocumentFactory.createInstance(file_path_str, encoding)
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
    return _wrappers().DocumentWrapper(doc)


def __getattr__(name: str):
    archery = _archery()
    if hasattr(archery, name):
        return getattr(archery, name)
    wrappers = _wrappers()
    if hasattr(wrappers, name):
        return getattr(wrappers, name)
    raise AttributeError(name)


def __dir__():
    archery = _archery()
    return sorted(set(list(globals().keys()) + dir(archery) + ["DocumentWrapper"]))
