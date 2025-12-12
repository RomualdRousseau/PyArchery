import os
from typing import Optional


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


MAVEN_URL = os.environ.get("PYARCHERY_MAVEN_URL", "https://oss.sonatype.org/content/repositories/releases")
MAVEN_SNAPSHOT_URL = os.environ.get(
    "PYARCHERY_MAVEN_SNAPSHOT_URL",
    "https://oss.sonatype.org/content/repositories/snapshots",
)

JARS_HOME: Optional[str] = os.environ.get("PYARCHERY_JARS_HOME")
SKIP_JVM_START = _env_flag("PYARCHERY_SKIP_JVM_START")
REQUIRE_CHECKSUMS = _env_flag("PYARCHERY_REQUIRE_CHECKSUMS")
FETCH_ALL_NATIVE = _env_flag("PYARCHERY_FETCH_ALL_NATIVE")
