import logging
import os
import shutil
import threading
from importlib import resources
from pathlib import Path

import jpype
import jpype.imports

from .config import JARS_HOME, SKIP_JVM_START
from .download import install_all_dependencies
from .version import __version__

logger = logging.getLogger(__name__)
_jvm_lock: threading.Lock = threading.Lock()
_jvm_started: bool = False


def start_java_archery_framework(force: bool = False) -> None:
    """Start the JVM if needed, downloading dependencies lazily."""
    if SKIP_JVM_START and not force:
        logger.info("PYARCHERY_SKIP_JVM_START is set; skipping JVM startup")
        return

    with _jvm_lock:
        global _jvm_started
        if _jvm_started and jpype.isJVMStarted():
            logger.debug("JVM already started; nothing to do")
            return

        if jpype.isJVMStarted():
            _jvm_started = True
            logger.debug("JVM already running outside PyArchery; marking as started")
            return

        package_path = resources.files(str(__package__.rsplit(".", 1)[0]))
        jars_root_env = JARS_HOME
        if jars_root_env:
            jars_root = Path(os.path.expandvars(os.path.expanduser(jars_root_env))).resolve()
            jars_path = jars_root / f"{__package__.rsplit('.', 1)[0]}.jars"
            logger.info("Using custom JAR cache at %s", jars_path)
        else:
            jars_path = Path(package_path.parent / f"{__package__.rsplit('.', 1)[0]}.jars")

        libs_path = Path(package_path.parent / f"{__package__.rsplit('.', 1)[0]}.libs")
        deps_path = Path(package_path / "dependencies")
        checksum_path = Path(package_path / "dependencies.sha256")

        options = [
            "-ea",
            "--add-opens=java.base/java.nio=ALL-UNNAMED",
            "--enable-native-access=ALL-UNNAMED",
        ]

        classpath = [f"{jars_path}/*", f"{libs_path}/*"]

        logger.info("Preparing to start JVM")
        logger.debug("JVM options: %s", options)
        logger.debug("JVM classpath: %s", classpath)

        expected_jar = jars_path / f"archery-{__version__}.jar"
        if os.path.exists(jars_path) and not os.path.exists(expected_jar):
            logger.warning(
                f"Version mismatch or missing jar. Expected archery-{__version__}.jar. Reinstalling dependencies."
            )
            shutil.rmtree(jars_path)

        if not os.path.exists(jars_path):
            install_all_dependencies(jars_path, deps_path, checksum_path)

        jpype.startJVM(*options, classpath=classpath)
        _jvm_started = True
        logger.warning("JAVA ARCHERY FRAMEWORK %s LOADED", __version__)


def is_jvm_started() -> bool:
    """Return True if the JVM is running."""
    return jpype.isJVMStarted()
