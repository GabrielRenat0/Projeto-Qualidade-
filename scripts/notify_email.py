"""Send the build notification e-mail.

Uses only the standard library, so it runs with the system ``python3`` even
when the pipeline fails before the virtual environment exists.
"""

import os
from collections.abc import Mapping
from dataclasses import dataclass

TRUE_VALUES = {"1", "true", "yes", "on"}
DEFAULT_JOB_NAME = "projeto-qualidade"


class ConfigError(Exception):
    """Raised when the e-mail configuration in the environment is invalid."""


@dataclass(frozen=True)
class EmailConfig:
    """SMTP server and recipients, read from environment variables."""

    recipients: tuple[str, ...]
    sender: str
    host: str
    port: int
    user: str
    password: str
    starttls: bool


def load_config(env: Mapping[str, str] = os.environ) -> EmailConfig:
    """Build the e-mail configuration from ``env``, failing with a clear message."""
    recipients = tuple(
        address.strip()
        for address in env.get("NOTIFY_EMAIL_TO", "").split(",")
        if address.strip()
    )
    if not recipients:
        raise ConfigError("NOTIFY_EMAIL_TO is not set; define at least one recipient")

    raw_port = env.get("SMTP_PORT", "1025")
    try:
        port = int(raw_port)
    except ValueError:
        raise ConfigError(f"SMTP_PORT must be a number, got {raw_port!r}") from None

    user = env.get("SMTP_USER", "")
    sender = env.get("SMTP_FROM", "") or user
    if not sender:
        raise ConfigError("SMTP_FROM is not set and there is no SMTP_USER to use instead")

    return EmailConfig(
        recipients=recipients,
        sender=sender,
        host=env.get("SMTP_HOST", "mailpit"),
        port=port,
        user=user,
        password=env.get("SMTP_PASSWORD", ""),
        starttls=env.get("SMTP_STARTTLS", "false").strip().lower() in TRUE_VALUES,
    )


def build_subject(status: str, env: Mapping[str, str] = os.environ) -> str:
    """Return the subject line with the build status and, when known, its number."""
    job = env.get("JOB_NAME") or DEFAULT_JOB_NAME
    subject = f"[{status.strip().upper()}] {job}"

    build_number = env.get("BUILD_NUMBER")
    if build_number:
        subject += f" #{build_number}"

    return subject


def build_body(status: str, env: Mapping[str, str] = os.environ) -> str:
    """Return the plain-text body with the build details that ``env`` provides."""
    build_number = env.get("BUILD_NUMBER")
    details = [
        ("Job", env.get("JOB_NAME") or DEFAULT_JOB_NAME),
        ("Build", f"#{build_number}" if build_number else ""),
        # GIT_BRANCH comes from the git plugin; BRANCH is the job parameter.
        ("Branch", env.get("GIT_BRANCH") or env.get("BRANCH", "")),
        ("Commit", env.get("GIT_COMMIT", "")),
        # Jenkins has no duration variable; the Jenkinsfile exports it.
        ("Duration", env.get("BUILD_DURATION", "")),
        ("Link", env.get("BUILD_URL", "")),
    ]

    lines = [f"Build status: {status.strip().upper()}", ""]
    lines += [f"{label}: {value}" for label, value in details if value]
    return "\n".join(lines) + "\n"
