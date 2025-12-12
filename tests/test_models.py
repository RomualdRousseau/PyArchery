import pyarchery


class _FakeBuilder:
    def __init__(self):
        self.args = {}

    def fromPath(self, path):  # noqa: N802
        self.args["path"] = path
        return self

    def fromURL(self, url):  # noqa: N802
        self.args["url"] = url
        return self

    def fromJSON(self, data):  # noqa: N802
        self.args["json"] = data
        return self


class _FakeArchery:
    def __init__(self, builder):
        self._builder = builder

    def ModelBuilder(self):  # noqa: N802
        return self._builder


def _patch_archery(monkeypatch, builder):
    fake = _FakeArchery(builder)
    monkeypatch.setattr(pyarchery, "_ARCHERY_MODULE", fake, raising=False)
    monkeypatch.setattr(pyarchery, "_archery", lambda: fake)
    return fake


def test_model_from_url(monkeypatch):
    builder = _FakeBuilder()
    _patch_archery(monkeypatch, builder)

    result = pyarchery.model_from_url("http://example.com/model.json")

    assert result is builder
    assert builder.args["url"] == "http://example.com/model.json"


def test_model_from_path(monkeypatch):
    builder = _FakeBuilder()
    _patch_archery(monkeypatch, builder)

    result = pyarchery.model_from_path("/tmp/model.json")

    assert result is builder
    assert builder.args["path"] == "/tmp/model.json"


def test_model_from_json(monkeypatch):
    builder = _FakeBuilder()
    _patch_archery(monkeypatch, builder)

    payload = '{"hello": "world"}'
    result = pyarchery.model_from_json(payload)

    assert result is builder
    assert builder.args["json"] == payload
