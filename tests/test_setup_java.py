import hashlib
import sys
from pathlib import Path

import pytest

from pyarchery import config as config_mod
from pyarchery import download


def test_load_checksums_parses_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(download, "REQUIRE_CHECKSUMS", False)
    content = """
    # comment
    deadbeef file1.jar
    cafebabe file2.jar
    """
    checksum_file = tmp_path / "checksums.txt"
    checksum_file.write_text(content)

    result = download._load_checksums(checksum_file)

    assert result == {"file1.jar": "deadbeef", "file2.jar": "cafebabe"}


def test_load_checksums_requires_file_when_flag_set(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(download, "REQUIRE_CHECKSUMS", True)
    with pytest.raises(FileNotFoundError):
        download._load_checksums(tmp_path / "missing.txt")


def test_get_checksums_is_memoized(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(download, "REQUIRE_CHECKSUMS", False)
    checksum_file = tmp_path / "checksums.txt"
    checksum_file.write_text("aaa file1.jar\n")
    download._get_checksums.cache_clear()

    first = download._get_checksums(str(checksum_file))
    checksum_file.write_text("bbb file1.jar\n")
    second = download._get_checksums(str(checksum_file))
    assert first == second == {"file1.jar": "aaa"}

    download._get_checksums.cache_clear()
    third = download._get_checksums(str(checksum_file))
    assert third == {"file1.jar": "bbb"}


def test_sha256_file(tmp_path: Path):
    path = tmp_path / "data.bin"
    data = b"pyarchery"
    path.write_bytes(data)
    expected = hashlib.sha256(data).hexdigest()
    assert download._sha256_file(path) == expected


def test_arch_matches_platform(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(download, "FETCH_ALL_NATIVE", False)
    system = sys.platform
    machine = "x86_64" if sys.maxsize > 2**32 else "x86"

    if system.startswith("linux"):
        matching = f"linux-{machine}"
        non_matching = "windows-x86_64"
    elif system == "darwin":
        matching = f"osx-{machine}"
        non_matching = "windows-x86_64"
    else:
        matching = f"windows-{machine}"
        non_matching = "linux-x86_64"

    assert download._arch_matches_platform(matching) is True
    assert download._arch_matches_platform(non_matching) is False

    monkeypatch.setattr(download, "FETCH_ALL_NATIVE", True)
    assert download._arch_matches_platform(non_matching) is True


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
