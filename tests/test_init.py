import pytest

import pyarchery
from pyarchery.setup_java import is_jvm_started, start_java_archery_framework


def test_jvm_initialization():
    """Test that the JVM starts correctly and is idempotent."""
    # Explicitly start to ensure lazy startup is exercised
    start_java_archery_framework()
    assert is_jvm_started()


def test_jvm_idempotency():
    """Test that calling start_java_archery_framework multiple times doesn't crash."""
    # This should be safe to call even if already started
    try:
        start_java_archery_framework()
        start_java_archery_framework()
    except Exception as e:
        pytest.fail(f"start_java_archery_framework raised exception on repeated call: {e}")
    assert is_jvm_started()


def test_dunder_dir_contains_expected_entries():
    names = pyarchery.__dir__()
    assert "DocumentWrapper" in names
    assert "load" in names
    assert "model_from_url" in names


def test_dunder_getattr_delegates_to_archery(monkeypatch):
    sentinel = object()

    class FakeArchery:
        def __init__(self):
            self.value = sentinel

    monkeypatch.setattr(pyarchery, "_ARCHERY_MODULE", FakeArchery(), raising=False)
    monkeypatch.setattr(pyarchery, "_archery", lambda: pyarchery._ARCHERY_MODULE)

    assert pyarchery.__getattr__("value") is sentinel
    with pytest.raises(AttributeError):
        pyarchery.__getattr__("does_not_exist")
