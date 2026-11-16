"""Check ``docker-compose.yml`` against the names the group agreed on.

Reads the YAML as written, without resolving ``${...}`` from ``.env``: what
matters is what each service declares, so the test needs no secret and no Docker.
"""

from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit

COMPOSE_FILE = Path(__file__).resolve().parents[2] / "docker-compose.yml"

SERVICES = {"jenkins", "tests", "reports", "mailpit", "k6"}
VOLUMES = {"jenkins_home", "reports", "mailpit_data"}
# Host ports of each service; an empty set means the service publishes none.
PUBLISHED_PORTS = {
    "jenkins": {8080},
    "mailpit": {8025},
    "reports": {8081},
    "tests": set(),
    "k6": set(),
}
JENKINS_IMAGE_NAME = "projeto-qualidade-jenkins"


@pytest.fixture(scope="module")
def compose() -> dict:
    """Return ``docker-compose.yml`` as plain data, with every ``${...}`` left as text."""
    return yaml.safe_load(COMPOSE_FILE.read_text(encoding="utf-8"))


def dependencies(service: dict) -> set[str]:
    """Return the services that ``service`` waits for, from either ``depends_on`` form."""
    # A list of names or a map of name to condition: iterating both yields the names.
    return set(service.get("depends_on") or [])


def published_ports(service: dict) -> set[int]:
    """Return the host ports that ``service`` publishes, from either ``ports`` form."""
    ports = set()
    for entry in service.get("ports") or []:
        if isinstance(entry, dict):
            # Long form: {target: 80, published: "8081"}.
            published = entry.get("published")
        else:
            # Short form: "[host_ip:]host:container[/protocol]". A lone container port
            # gets a random host port, so it publishes no fixed one.
            parts = str(entry).split("/")[0].split(":")
            published = parts[-2] if len(parts) > 1 else None
        if published is not None:
            ports.add(int(published))
    return ports


# The helpers themselves


@pytest.mark.parametrize(
    "depends_on",
    [["mailpit"], {"mailpit": {"condition": "service_healthy"}}],
    ids=["list", "map"],
)
def test_dependencies_reads_both_compose_forms(depends_on):
    assert dependencies({"depends_on": depends_on}) == {"mailpit"}


def test_dependencies_of_a_service_that_waits_for_nothing():
    assert dependencies({"image": "nginx:1.30.6-alpine"}) == set()


@pytest.mark.parametrize(
    ("entry", "expected"),
    [
        ("8081:80", {8081}),
        ("127.0.0.1:8080:8080", {8080}),
        ("8025:8025/tcp", {8025}),
        ({"target": 80, "published": "8081"}, {8081}),
        ({"target": 80, "published": 8081, "host_ip": "127.0.0.1"}, {8081}),
        ("80", set()),
        ({"target": 80}, set()),
    ],
)
def test_published_ports_reads_both_compose_forms(entry, expected):
    assert published_ports({"ports": [entry]}) == expected


# The repository


def test_services_are_the_contract_ones(compose):
    services = set(compose["services"])

    assert services == SERVICES, f"services in the file: {sorted(services)}"


@pytest.mark.parametrize("name", ["jenkins", "mailpit", "reports", "tests"])
def test_service_starts_with_a_plain_up(compose, name):
    # A profile keeps a service out of `docker compose up`; the skeleton used "placeholder".
    profiles = compose["services"][name].get("profiles")

    assert not profiles, f"{name} is still under a profile: {profiles}"


def test_k6_runs_only_under_the_perf_profile(compose):
    profiles = compose["services"]["k6"].get("profiles")

    assert profiles == ["perf"], f"k6 profiles: {profiles}"


def test_tests_is_built_from_the_local_dockerfile(compose):
    build = compose["services"]["tests"].get("build")

    assert build, "tests has no build: it must come from the local Dockerfile"


def test_jenkins_is_pulled_as_our_published_image(compose):
    jenkins = compose["services"]["jenkins"]
    image = jenkins.get("image", "")
    # Drops the tag or the digest: "user/name:1.0.0" becomes "user/name".
    namespace, _, name = image.replace("@", ":").split(":")[0].partition("/")

    assert "build" not in jenkins, "jenkins must be pulled from Docker Hub, not built locally"
    assert namespace and name == JENKINS_IMAGE_NAME, f"jenkins image: {image!r}"


def test_volumes_are_the_contract_ones(compose):
    volumes = set(compose["volumes"])

    assert volumes == VOLUMES, f"volumes in the file: {sorted(volumes)}"


@pytest.mark.parametrize("name", sorted(PUBLISHED_PORTS))
def test_service_publishes_only_its_contract_ports(compose, name):
    ports = published_ports(compose["services"][name])

    assert ports == PUBLISHED_PORTS[name], f"{name} publishes {sorted(ports)}"


@pytest.mark.parametrize("name", ["jenkins", "tests"])
def test_service_waits_for_mailpit(compose, name):
    # Both send the e-mail through mailpit, so it has to be up before they run.
    waits_for = dependencies(compose["services"][name])

    assert "mailpit" in waits_for, f"{name} depends on {sorted(waits_for)}"
