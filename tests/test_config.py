import pytest

from pyarchery import config as config_mod


def test_env_flag_truthy_and_falsey(monkeypatch: pytest.MonkeyPatch):
    for val in ["1", "true", "TRUE", "yes", "on"]:
        monkeypatch.setenv("PYARCHERY_TEST_FLAG", val)
        assert config_mod._env_flag("PYARCHERY_TEST_FLAG") is True

    for val in ["0", "false", "False", "no", "off", ""]:
        monkeypatch.setenv("PYARCHERY_TEST_FLAG", val)
        assert config_mod._env_flag("PYARCHERY_TEST_FLAG") is False

    monkeypatch.delenv("PYARCHERY_TEST_FLAG", raising=False)
    assert config_mod._env_flag("PYARCHERY_TEST_FLAG", default=True) is True
    assert config_mod._env_flag("PYARCHERY_TEST_FLAG", default=False) is False
