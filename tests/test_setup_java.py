import hashlib
import sys
from pathlib import Path

import pytest

import pyarchery.setup_java as setup_java


def test_load_checksums_parses_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(setup_java, "REQUIRE_CHECKSUMS", False)
    content = """
    # comment
    deadbeef file1.jar
    cafebabe file2.jar
    """
    checksum_file = tmp_path / "checksums.txt"
    checksum_file.write_text(content)

    result = setup_java._load_checksums(checksum_file)

    assert result == {"file1.jar": "deadbeef", "file2.jar": "cafebabe"}


def test_load_checksums_requires_file_when_flag_set(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(setup_java, "REQUIRE_CHECKSUMS", True)
    with pytest.raises(FileNotFoundError):
        setup_java._load_checksums(tmp_path / "missing.txt")


def test_get_checksums_is_memoized(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(setup_java, "REQUIRE_CHECKSUMS", False)
    checksum_file = tmp_path / "checksums.txt"
    checksum_file.write_text("aaa file1.jar\n")
    setup_java._get_checksums.cache_clear()

    first = setup_java._get_checksums(str(checksum_file))
    # Modify file to prove cached value is reused
    checksum_file.write_text("bbb file1.jar\n")
    second = setup_java._get_checksums(str(checksum_file))
    assert first == second == {"file1.jar": "aaa"}

    # Clearing cache should pick up new contents
    setup_java._get_checksums.cache_clear()
    third = setup_java._get_checksums(str(checksum_file))
    assert third == {"file1.jar": "bbb"}


def test_sha256_file(tmp_path: Path):
    path = tmp_path / "data.bin"
    data = b"pyarchery"
    path.write_bytes(data)
    expected = hashlib.sha256(data).hexdigest()
    assert setup_java._sha256_file(path) == expected


def test_arch_matches_platform(monkeypatch: pytest.MonkeyPatch):
    # Force platform-aware behavior
    monkeypatch.setattr(setup_java, "FETCH_ALL_NATIVE", False)
    system = sys.platform
    machine = "x86_64" if sys.maxsize > 2**32 else "x86"

    if system.startswith("linux"):
        matching = f"linux-{machine}"
        non_matching = "windows-x86_64"
    elif system == "darwin":
        matching = f"osx-{machine}"
        non_matching = "windows-x86_64"
    else:  # windows and others
        matching = f"windows-{machine}"
        non_matching = "linux-x86_64"

    assert setup_java._arch_matches_platform(matching) is True
    assert setup_java._arch_matches_platform(non_matching) is False

    # FETCH_ALL_NATIVE overrides platform filtering
    monkeypatch.setattr(setup_java, "FETCH_ALL_NATIVE", True)
    assert setup_java._arch_matches_platform(non_matching) is True
