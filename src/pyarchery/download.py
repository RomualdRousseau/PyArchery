import hashlib
import logging
import os
import platform
import sys
import tempfile
from functools import cache
from typing import Any, Optional

import requests
from requests.adapters import HTTPAdapter
from tqdm import tqdm
from urllib3.util.retry import Retry

from .config import FETCH_ALL_NATIVE, MAVEN_SNAPSHOT_URL, MAVEN_URL, REQUIRE_CHECKSUMS

logger = logging.getLogger(__name__)


def _build_http_session() -> requests.Session:
    """Return a session configured with retries/backoff and proxy support."""
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET", "HEAD"),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retries, pool_maxsize=4)
    session = requests.Session()
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


_SESSION = _build_http_session()


def _load_checksums(checksum_path: str | os.PathLike[str]) -> dict[str, str]:
    """Load checksums from a file if present."""
    checksum_path = os.fspath(checksum_path)
    checksums: dict[str, str] = {}
    if not os.path.exists(checksum_path):
        if REQUIRE_CHECKSUMS:
            raise FileNotFoundError("Checksum file is required but missing")
        logger.info("No checksum file found at %s; downloads will not be verified.", checksum_path)
        return checksums

    with open(checksum_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                checksum, filename = line.split(None, 1)
                checksums[filename] = checksum
            except ValueError:
                logger.warning("Ignoring malformed checksum line: %s", line)
    logger.info("Loaded %d checksums from %s", len(checksums), checksum_path)
    return checksums


@cache
def _get_checksums(checksum_path: str) -> dict[str, str]:
    """Memoized checksum loader."""
    return _load_checksums(checksum_path)


def _sha256_file(path: str | os.PathLike[str]) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _download_with_verification(url: str, target_path: str | os.PathLike[str], checksum: str | None = None) -> None:
    """Download a file atomically with checksum verification and cleanup on failure."""
    tmp_fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(target_path), suffix=".part")
    os.close(tmp_fd)
    try:
        logger.info("Downloading %s -> %s", url, target_path)
        with _SESSION.get(url, stream=True, timeout=(10, 60)) as response:
            if response.status_code != 200:
                raise RuntimeError(f"Failed to download {url} (status {response.status_code} {response.reason})")

            with open(tmp_path, "wb") as out:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        out.write(chunk)

        if checksum:
            actual = _sha256_file(tmp_path)
            if actual.lower() != checksum.lower():
                raise RuntimeError(f"Checksum mismatch for {url}: expected {checksum}, got {actual}")
            logger.info("Checksum verified for %s", target_path)

        os.replace(tmp_path, target_path)
        logger.info("Saved %s", target_path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def _arch_matches_platform(arch: str) -> bool:
    """Return True if the native classifier appears compatible with the current platform."""
    if FETCH_ALL_NATIVE:
        return True

    system = sys.platform
    machine = platform.machine().lower()
    arch = arch.lower()

    candidates = []
    if system.startswith("linux"):
        candidates.extend(["linux", f"linux-{machine}"])
    elif system == "darwin":
        candidates.extend(["osx", "macos", f"osx-{machine}", f"macos-{machine}"])
    elif system.startswith("win"):
        candidates.extend(["windows", f"windows-{machine}", "win", f"win-{machine}"])

    return any(arch.startswith(c) for c in candidates)


def _install_one_dependency(
    jars_path: str | os.PathLike[str],
    dep: str,
    checksum_map: dict[str, str],
    pbar: Optional[Any] = None,
) -> None:
    """Download and place a single dependency if not already present (with checksum validation)."""
    parts = dep.split(":")
    if len(parts) == 4:
        package, name, extension, version = parts
        file_name = f"{name}-{version}.{extension}"
        file_name_disk = file_name
        base_url = MAVEN_URL
    else:
        package, name, extension, arch, version = parts
        if arch and not _arch_matches_platform(arch):
            logger.info("Skipping %s because architecture %s is not for this platform.", name, arch)
            return
        if "SNAPSHOT" in version:
            v = version.replace("-SNAPSHOT", "")
            file_name = f"{name}-{v}-{arch}.{extension}"
            file_name_disk = f"{name}-{version}.{extension}"
            base_url = MAVEN_SNAPSHOT_URL
        else:
            file_name = f"{name}-{version}-{arch}.{extension}"
            file_name_disk = file_name
            base_url = MAVEN_URL

    expected_checksum = checksum_map.get(file_name_disk) or checksum_map.get(file_name)
    if expected_checksum is None and REQUIRE_CHECKSUMS:
        raise RuntimeError(f"Checksum required but missing for {file_name_disk}")

    target_path = os.path.join(jars_path, file_name_disk)
    if os.path.exists(target_path):
        if expected_checksum:
            if _sha256_file(target_path).lower() == expected_checksum.lower():
                logger.debug("Reusing cached dependency %s (checksum ok)", target_path)
                return
            logger.warning("Existing file %s failed checksum; re-downloading.", target_path)
            os.remove(target_path)
        else:
            logger.debug("Reusing cached dependency %s (no checksum provided)", target_path)
            return

    url = "/".join([base_url, package.replace(".", "/"), name, version, file_name])
    if pbar:
        pbar.set_description(f"Downloading {file_name}")

    _download_with_verification(url, target_path, expected_checksum)


def install_all_dependencies(
    jars_path: str | os.PathLike[str],
    deps_path: str | os.PathLike[str],
    checksum_path: str | os.PathLike[str],
) -> None:
    """Install all dependencies listed in the deps file into jars_path."""
    os.makedirs(jars_path, exist_ok=True)
    checksum_map = _get_checksums(os.fspath(checksum_path))
    with open(deps_path, "r") as file:
        dependencies = file.readlines()
        pbar = tqdm(dependencies, desc="Loading dependencies")
        for dep in pbar:
            _install_one_dependency(jars_path, dep.rstrip(), checksum_map, pbar)
