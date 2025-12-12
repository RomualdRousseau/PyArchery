import pytest

from pyarchery.setup_java import start_java_archery_framework

start_java_archery_framework()

from pyarchery.archery import java_types  # noqa: E402


def test_jpath_convert(monkeypatch: pytest.MonkeyPatch):
    calls = {}

    class FakePaths:
        @staticmethod
        def get(arg):
            calls["arg"] = arg
            return f"path:{arg}"

    monkeypatch.setattr(java_types, "Paths_", FakePaths)
    result = java_types._JPathConvert(None, "/tmp/example")
    assert result == "path:/tmp/example"
    assert calls["arg"] == "/tmp/example"


def test_jlist_convert(monkeypatch: pytest.MonkeyPatch):
    class FakeList:
        @staticmethod
        def of(arg):
            return list(arg)

    monkeypatch.setattr(java_types, "List_", FakeList)
    data = [1, 2, 3]
    result = java_types._JListConvert(None, data)
    assert result == data


def test_jdsf_object_convert(monkeypatch: pytest.MonkeyPatch):
    calls = {}

    class FakeJSON:
        @staticmethod
        def objectOf(arg):  # noqa: N802
            calls["arg"] = arg
            return {"json": arg}

    monkeypatch.setattr(java_types, "JSON_", FakeJSON)
    result = java_types._JDSFObjectConvert(None, '{"a": 1}')
    assert result == {"json": '{"a": 1}'}
    assert calls["arg"] == '{"a": 1}'


def test_jenum_set_convert(monkeypatch: pytest.MonkeyPatch):
    calls = []

    class FakeEnumSet:
        @staticmethod
        def of(*args):
            calls.append(args)
            return tuple(args)

    monkeypatch.setattr(java_types, "EnumSet_", FakeEnumSet)

    # len <= 2 path
    result_short = java_types._JEnumSetConvert(None, ["A"])
    assert result_short == ("A",)
    assert calls[-1] == ("A",)

    # len > 2 path
    result_long = java_types._JEnumSetConvert(None, ["A", "B", "C"])
    assert result_long == ("A", ["B", "C"])
    assert calls[-1] == ("A", ["B", "C"])
