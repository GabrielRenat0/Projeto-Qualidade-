"""Guard the security rules of ``docker-compose.yml``.

Every image is pinned to a version, only mailpit reaches the Gmail credentials
and no service mounts the Docker socket. Reads the YAML as written, without
resolving ``${...}`` from ``.env``: the test checks which variable each service
references, never its value, so it needs no secret.
"""

import re
from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit

COMPOSE_FILE = Path(__file__).resolve().parents[2] / "docker-compose.yml"

SERVICES = ["jenkins", "k6", "mailpit", "reports", "tests"]
# The tests service has no image: it is built from the local Dockerfile.
PULLED_SERVICES = ["jenkins", "k6", "mailpit", "reports"]
GMAIL_VARIABLES = {"GMAIL_USER", "GMAIL_APP_PASSWORD"}
SERVICES_WITHOUT_GMAIL = ["jenkins", "k6", "reports", "tests"]
DOCKER_SOCKET = "docker.sock"

# $NAME or ${NAME...}, the two ways Compose interpolates a variable.
VARIABLE_PATTERN = re.compile(r"\$\{?([A-Za-z_][A-Za-z0-9_]*)")


@pytest.fixture(scope="module")
def compose() -> dict:
    """Return ``docker-compose.yml`` as plain data, with every ``${...}`` left as text."""
    return yaml.safe_load(COMPOSE_FILE.read_text(encoding="utf-8"))


def is_pinned(image: str) -> bool:
    """Return True when ``image`` names one exact version: a digest or a tag other than latest."""
    if "$" in image:
        # A variable hides the version from the file.
        return False
    if "@sha256:" in image:
        return True
    # Only the last path segment has the tag; "localhost:5000/name" has a port, not a tag.
    _, colon, tag = image.rsplit("/", 1)[-1].partition(":")
    return bool(colon) and tag not in ("", "latest")


def env_names(service: dict) -> set[str]:
    """Return every variable that ``service`` receives or interpolates, from either form."""
    environment = service.get("environment") or {}
    if isinstance(environment, list):
        # List form: "NAME=value", or just "NAME" to pass the host value through.
        names = {str(entry).split("=", 1)[0] for entry in environment}
    else:
        names = set(environment)

    # Interpolations anywhere in the service, such as in a value or in the command.
    # "$$" is the Compose escape for a literal "$", so it references nothing.
    text = yaml.safe_dump(service).replace("$$", "")
    return names | set(VARIABLE_PATTERN.findall(text))


def mount_sources(service: dict) -> list[str]:
    """Return the host paths and volume names ``service`` mounts, from either ``volumes`` form."""
    sources = []
    for entry in service.get("volumes") or []:
        if isinstance(entry, dict):
            # Long form: {type: bind, source: ./perf, target: /perf}.
            source = entry.get("source")
        else:
            # Short form: "source:target[:mode]"; a lone path is an anonymous volume.
            source, colon, _ = str(entry).partition(":")
            source = source if colon else None
        if source:
            sources.append(str(source))
    return sources


# The helpers themselves


@pytest.mark.parametrize(
    "image",
    [
        "axllent/mailpit:v1.32.0",
        "nginx:1.30.6-alpine",
        "grafana/k6@sha256:a070982921f37e1b891f8ed9fb2b507520c83228614c14640f7e28f635f4281b",
        "localhost:5000/team/image:1.0.0",
    ],
)
def test_is_pinned_accepts_a_version_or_a_digest(image):
    assert is_pinned(image)


@pytest.mark.parametrize(
    "image",
    [
        "nginx",
        "nginx:latest",
        "nginx:",
        "localhost:5000/team/image",
        "${JENKINS_IMAGE}",
        "nginx:${NGINX_TAG}",
    ],
)
def test_is_pinned_rejects_a_floating_image(image):
    assert not is_pinned(image)


@pytest.mark.parametrize(
    "environment",
    [
        {"MP_SMTP_RELAY_PASSWORD": "${GMAIL_APP_PASSWORD}"},
        ["MP_SMTP_RELAY_PASSWORD=${GMAIL_APP_PASSWORD}"],
    ],
    ids=["map", "list"],
)
def test_env_names_reads_both_compose_forms(environment):
    names = env_names({"environment": environment})

    assert names == {"MP_SMTP_RELAY_PASSWORD", "GMAIL_APP_PASSWORD"}


def test_env_names_sees_a_variable_passed_through_from_the_host():
    assert env_names({"environment": ["GMAIL_APP_PASSWORD"]}) == {"GMAIL_APP_PASSWORD"}


def test_env_names_sees_a_variable_with_a_default_value():
    service = {"environment": {"BASE_URL": "${API_BASE_URL:-https://api.example.com}"}}

    assert env_names(service) == {"BASE_URL", "API_BASE_URL"}


def test_env_names_sees_a_variable_used_in_the_command():
    service = {"command": ["sh", "-c", "send --password $GMAIL_APP_PASSWORD"]}

    assert env_names(service) == {"GMAIL_APP_PASSWORD"}


def test_env_names_ignores_an_escaped_dollar():
    assert env_names({"command": 'sh -c "exit $$code"'}) == set()


@pytest.mark.parametrize(
    ("entry", "expected"),
    [
        ("reports:/app/reports", ["reports"]),
        ("./perf:/perf:ro", ["./perf"]),
        ("/var/run/docker.sock:/var/run/docker.sock", ["/var/run/docker.sock"]),
        ({"type": "volume", "source": "reports", "target": "/usr/share/nginx/html"}, ["reports"]),
        ("/data", []),
        ({"type": "tmpfs", "target": "/tmp"}, []),
    ],
)
def test_mount_sources_reads_both_compose_forms(entry, expected):
    assert mount_sources({"volumes": [entry]}) == expected


# The repository


@pytest.mark.parametrize("name", PULLED_SERVICES)
def test_image_is_pinned_to_a_version(compose, name):
    image = compose["services"][name].get("image", "")

    assert is_pinned(image), f"{name} uses {image!r}: pin a version, never latest"


def test_no_other_service_pulls_an_image(compose):
    # A new service with an image must join PULLED_SERVICES to be checked above.
    pulled = sorted(name for name, service in compose["services"].items() if "image" in service)

    assert pulled == PULLED_SERVICES, f"services with an image: {pulled}"


def test_mailpit_reads_the_gmail_credentials(compose):
    missing = GMAIL_VARIABLES - env_names(compose["services"]["mailpit"])

    assert not missing, f"mailpit does not reference {sorted(missing)}"


@pytest.mark.parametrize("name", SERVICES_WITHOUT_GMAIL)
def test_service_never_reaches_the_gmail_credentials(compose, name):
    leaked = GMAIL_VARIABLES & env_names(compose["services"][name])

    assert not leaked, f"{name} references {sorted(leaked)}; only mailpit may"


@pytest.mark.parametrize("name", SERVICES)
def test_service_does_not_load_an_env_file(compose, name):
    # env_file hands every variable of the file to the container, the Gmail password
    # included; each service lists only the variables it needs under environment.
    env_file = compose["services"][name].get("env_file")

    assert not env_file, f"{name} loads {env_file!r}"


@pytest.mark.parametrize("name", SERVICES)
def test_service_does_not_mount_the_docker_socket(compose, name):
    # The socket would give the container full control of the host's Docker.
    sockets = [
        source for source in mount_sources(compose["services"][name]) if DOCKER_SOCKET in source
    ]

    assert not sockets, f"{name} mounts {sockets}"
