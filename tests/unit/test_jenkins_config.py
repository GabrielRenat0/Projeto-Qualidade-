"""Check the Jenkins configuration kept in ``jenkins/``.

These tests only read the files; they never start Jenkins.
"""

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[2]
PLUGINS_FILE = ROOT / "jenkins" / "plugins.txt"

# The plugins that the pipeline and the configuration as code rely on (the project contract).
CONTRACT_PLUGINS = {
    "configuration-as-code",
    "job-dsl",
    "workflow-aggregator",
    "git",
    "junit",
    "timestamper",
    "pipeline-stage-view",
}

# A pinned plugin is "name:version", with an explicit version that starts with a digit.
PINNED_PLUGIN = re.compile(r"[a-z0-9][a-z0-9._-]*:\d[A-Za-z0-9._-]*")


def is_pinned(line: str) -> bool:
    """Return True when ``line`` names a plugin with an explicit version."""
    return PINNED_PLUGIN.fullmatch(line) is not None


def plugin_lines() -> list[str]:
    """Return the plugin lines of ``plugins.txt``, without blank lines and comments."""
    lines = (line.strip() for line in PLUGINS_FILE.read_text(encoding="utf-8").splitlines())
    return [line for line in lines if line and not line.startswith("#")]


def plugin_names() -> list[str]:
    """Return the name of every plugin listed in ``plugins.txt``."""
    return [line.split(":")[0] for line in plugin_lines()]


# The pin detector itself


@pytest.mark.parametrize(
    "line",
    ["git:5.11.0", "timestamper:1.30", "configuration-as-code:2147.v8a_8d38668c72"],
)
def test_detector_accepts_a_plugin_with_a_fixed_version(line):
    assert is_pinned(line)


@pytest.mark.parametrize("line", ["git", "git:", "git:latest", "git:experimental"])
def test_detector_rejects_a_plugin_without_a_fixed_version(line):
    assert not is_pinned(line)


# jenkins/plugins.txt


def test_every_plugin_of_the_image_is_pinned():
    unpinned = [line for line in plugin_lines() if not is_pinned(line)]

    assert not unpinned, f"pin a version (name:version) for: {unpinned}"


def test_no_plugin_is_listed_twice():
    names = plugin_names()
    repeated = sorted({name for name in names if names.count(name) > 1})

    assert not repeated, f"plugins listed more than once: {repeated}"


def test_the_contract_plugins_are_in_the_image():
    missing = sorted(CONTRACT_PLUGINS - set(plugin_names()))

    assert not missing, f"contract plugins missing from plugins.txt: {missing}"
