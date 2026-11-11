"""Fail if a real e-mail address is hardcoded in the pipeline configuration.

The recipients must come only from ``NOTIFY_EMAIL_TO`` (and the Gmail account
only from ``GMAIL_USER``), both set in ``.env``. Reserved example domains, such
as ``example.com``, are allowed in comments, docstrings and defaults.
"""

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[2]

# Files and folders that reach the pipeline; the ones not created yet are skipped.
SCANNED_PATHS = ["Jenkinsfile", "jenkins/casc", "docker-compose.yml", "scripts"]
SCANNED_SUFFIXES = {"", ".py", ".sh", ".yml", ".yaml", ".groovy"}

EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+)")

# Domains reserved for documentation and tests (RFC 2606 and RFC 6761).
EXAMPLE_DOMAINS = {"example.com", "example.net", "example.org"}
EXAMPLE_TLDS = {"example", "test", "invalid", "localhost"}


def is_example_domain(domain: str) -> bool:
    """Return True when ``domain`` is reserved for examples and never delivers mail."""
    domain = domain.lower()
    if domain.rsplit(".", 1)[-1] in EXAMPLE_TLDS:
        return True
    return any(domain == base or domain.endswith(f".{base}") for base in EXAMPLE_DOMAINS)


def find_hardcoded_emails(text: str) -> list[str]:
    """Return every e-mail address in ``text`` whose domain is not an example one."""
    return [
        match.group(0)
        for match in EMAIL_PATTERN.finditer(text)
        if not is_example_domain(match.group(1))
    ]


def scanned_files() -> list[Path]:
    """Return the existing files under ``SCANNED_PATHS``, skipping caches."""
    files = []
    for relative in SCANNED_PATHS:
        path = ROOT / relative
        candidates = sorted(path.rglob("*")) if path.is_dir() else [path]
        files += [
            candidate
            for candidate in candidates
            if candidate.is_file()
            and candidate.suffix in SCANNED_SUFFIXES
            and "__pycache__" not in candidate.parts
        ]
    return files


# The detector itself


@pytest.mark.parametrize(
    "text",
    [
        "NOTIFY_EMAIL_TO=team@gmail.com",
        "to: 'someone.else+ci@inatel.br'",
        "recipients = ['a@example.com', 'b@outlook.com']",
        "mail to ana@sub.example.com.br",
    ],
)
def test_detector_flags_real_addresses(text):
    assert find_hardcoded_emails(text)


@pytest.mark.parametrize(
    "text",
    [
        "NOTIFY_EMAIL_TO=member1@example.com,member2@example.org",
        "SMTP_FROM=pipeline@builds.example.net",
        "bot@ci.test and nobody@mail.invalid",
        "NOTIFY_EMAIL_TO=${NOTIFY_EMAIL_TO}",
        "image: axllent/mailpit:v1.32.0",
        "git clone https://github.com/GabrielRenat0/Projeto-Qualidade-.git",
    ],
)
def test_detector_accepts_examples_and_variables(text):
    assert find_hardcoded_emails(text) == []


# The repository


def test_the_scan_covers_the_pipeline_files():
    scanned = {path.relative_to(ROOT).as_posix() for path in scanned_files()}

    assert "docker-compose.yml" in scanned
    assert "scripts/notify_email.py" in scanned


def test_no_real_email_is_hardcoded_in_the_pipeline():
    found = {
        path.relative_to(ROOT).as_posix(): emails
        for path in scanned_files()
        if (emails := find_hardcoded_emails(path.read_text(encoding="utf-8")))
    }

    assert not found, f"use NOTIFY_EMAIL_TO or GMAIL_USER instead of fixed addresses: {found}"
