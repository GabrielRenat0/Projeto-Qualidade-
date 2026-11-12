"""Check the Jenkins configuration kept in ``jenkins/``.

These tests only read the files; they never start Jenkins.
"""

import re
from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[2]
PLUGINS_FILE = ROOT / "jenkins" / "plugins.txt"
CASC_DIR = ROOT / "jenkins" / "casc"

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


# Words that mark a key of the configuration as code as a secret.
SECRET_WORDS = ("password", "secret", "token", "passphrase", "privatekey", "apikey")
# The only value accepted for a secret: one variable, with no default written in the file.
VARIABLE = re.compile(r"\$\{[A-Za-z_][A-Za-z0-9_]*\}")


def is_secret_key(key: str) -> bool:
    """Return True when the name of ``key`` says that it holds a secret."""
    name = key.lower().replace("_", "").replace("-", "")
    return any(word in name for word in SECRET_WORDS)


def is_variable(value: object) -> bool:
    """Return True when ``value`` is exactly one ``${VARIABLE}`` reference."""
    return isinstance(value, str) and VARIABLE.fullmatch(value) is not None


def find_secrets(node: object, path: str = "") -> list[tuple[str, object]]:
    """Return ``(path, value)`` for every secret key in a parsed YAML document."""
    found = []
    if isinstance(node, dict):
        for key, value in node.items():
            child = f"{path}.{key}" if path else str(key)
            if is_secret_key(str(key)) and not isinstance(value, (dict, list)):
                found.append((child, value))
            found += find_secrets(value, child)
    elif isinstance(node, list):
        for index, item in enumerate(node):
            found += find_secrets(item, f"{path}[{index}]")
    return found


def casc_files() -> list[Path]:
    """Return the YAML files that JCasC reads from ``jenkins/casc``."""
    return sorted(path for path in CASC_DIR.rglob("*") if path.suffix in {".yaml", ".yml"})


def casc_secrets() -> list[tuple[str, object]]:
    """Return ``(file: path, value)`` for every secret key in the configuration as code."""
    return [
        (f"{path.name}: {key}", value)
        for path in casc_files()
        for key, value in find_secrets(yaml.safe_load(path.read_text(encoding="utf-8")))
    ]


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


# The secret detector itself


@pytest.mark.parametrize("value", ["${JENKINS_ADMIN_PASSWORD}", "${token}"])
def test_detector_accepts_a_secret_that_comes_from_a_variable(value):
    assert is_variable(value)


@pytest.mark.parametrize(
    "value",
    [
        "admin123",
        "",
        "${JENKINS_ADMIN_PASSWORD:-admin123}",
        "x${JENKINS_ADMIN_PASSWORD}",
        None,
        1234,
    ],
)
def test_detector_rejects_a_secret_written_in_the_file(value):
    assert not is_variable(value)


def test_detector_finds_the_secret_keys_at_any_depth():
    document = {
        "jenkins": {"users": [{"id": "admin", "password": "admin123"}]},
        "unclassified": {"mailer": {"smtpPassword": "${SMTP_PASSWORD}", "api_token": "abc"}},
        "credentials": {"secrets": {"url": "http://localhost:8080/"}},
    }

    assert find_secrets(document) == [
        ("jenkins.users[0].password", "admin123"),
        ("unclassified.mailer.smtpPassword", "${SMTP_PASSWORD}"),
        ("unclassified.mailer.api_token", "abc"),
    ]


# jenkins/casc


def test_every_configuration_file_is_valid_yaml():
    files = casc_files()

    assert files, "no configuration file found in jenkins/casc"
    for path in files:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(document, dict), f"{path.name} is not a YAML mapping"


def test_secrets_of_the_configuration_come_only_from_variables():
    # Only the keys go to the message: the value of a secret must never be printed.
    fixed = sorted(key for key, value in casc_secrets() if not is_variable(value))

    assert not fixed, f"use a ${{VARIABLE}} from the .env instead of a fixed value in: {fixed}"


def test_the_admin_password_comes_from_the_contract_variable():
    # A plain boolean, so a failure never prints the values found.
    from_the_contract = any(value == "${JENKINS_ADMIN_PASSWORD}" for _, value in casc_secrets())

    assert from_the_contract, "the admin password must be ${JENKINS_ADMIN_PASSWORD}"
