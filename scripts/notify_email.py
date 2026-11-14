"""Send the build notification e-mail.

Uses only the standard library, so it runs with the system ``python3`` even
when the pipeline fails before the virtual environment exists.
"""

import argparse
import os
import smtplib
import sys
import xml.etree.ElementTree as ET
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path

TRUE_VALUES = {"1", "true", "yes", "on"}
DEFAULT_JOB_NAME = "projeto-qualidade"
SMTP_TIMEOUT_SECONDS = 30
# Gmail accepts 25 MB per message; the report is usually a few hundred KB.
MAX_ATTACHMENT_BYTES = 10 * 1024 * 1024
# The HTML report that pytest writes in the reports folder.
REPORT_FILENAME = "report.html"
# Docker creates this file in every container, so it marks the tests container.
CONTAINER_MARKER = Path("/.dockerenv")
# The pipeline and the tests container write their reports here, next to scripts/.
REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"


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


def detect_origin(
    env: Mapping[str, str] = os.environ, container_marker: Path = CONTAINER_MARKER
) -> str:
    """Return where the script runs: the Jenkins pipeline, the tests container or a laptop."""
    # Jenkins sets JENKINS_URL in every build; the Jenkins container alone does not.
    if env.get("JENKINS_URL"):
        return "Jenkins"
    if container_marker.exists():
        return "tests container"
    return "local machine"


def build_subject(status: str, env: Mapping[str, str] = os.environ, origin: str = "") -> str:
    """Return the subject line with the build status and, when known, its number and origin."""
    job = env.get("JOB_NAME") or DEFAULT_JOB_NAME
    subject = f"[{status.strip().upper()}] {job}"

    build_number = env.get("BUILD_NUMBER")
    if build_number:
        subject += f" #{build_number}"

    if origin:
        subject += f" ({origin})"

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


def _test_totals(junit_path: Path) -> str:
    """Return the totals of the JUnit report that pytest writes."""
    suites = list(ET.parse(junit_path).getroot().iter("testsuite"))
    if not suites:
        raise ValueError("the JUnit report has no testsuite element")

    # pytest writes a single <testsuite>; adding them up also covers a report with several.
    totals = {
        name: sum(int(suite.get(name, 0)) for suite in suites)
        for name in ("tests", "failures", "errors", "skipped")
    }
    passed = totals["tests"] - totals["failures"] - totals["errors"] - totals["skipped"]
    return (
        f"{totals['tests']} (passed: {passed}, failed: {totals['failures']}, "
        f"errors: {totals['errors']}, skipped: {totals['skipped']})"
    )


def _coverage_percent(coverage_path: Path) -> str:
    """Return the line coverage of the coverage.py XML report, as a percentage."""
    # line-rate is the fraction of covered lines, e.g. 0.9899.
    line_rate = float(ET.parse(coverage_path).getroot().attrib["line-rate"])
    return f"{line_rate * 100:.2f}%"


def build_report_summary(reports_dir: Path = REPORTS_DIR) -> str:
    """Return the test and coverage lines for the body, read from ``reports_dir``."""
    reports = [
        ("Tests", "junit.xml", _test_totals),
        ("Coverage", "coverage.xml", _coverage_percent),
    ]
    lines = []
    for label, filename, summarize in reports:
        # A missing or broken report becomes a notice, so the e-mail still goes out.
        try:
            value = summarize(reports_dir / filename)
        except FileNotFoundError:
            value = f"report not generated (reports/{filename})"
        except (OSError, ET.ParseError, KeyError, ValueError):
            value = f"report could not be read (reports/{filename})"
        lines.append(f"{label}: {value}")
    return "\n".join(lines) + "\n"


def build_message(config: EmailConfig, subject: str, body: str) -> EmailMessage:
    """Assemble the e-mail with the sender, recipients, subject and body."""
    message = EmailMessage()
    message["From"] = config.sender
    message["To"] = ", ".join(config.recipients)
    message["Subject"] = subject
    message.set_content(body)
    # REPORTS_DIR is read on every call, never frozen in a default argument,
    # so the tests can replace it with a temporary folder.
    attach_report(message, REPORTS_DIR / REPORT_FILENAME)
    return message


def attach_report(
    message: EmailMessage,
    report_path: Path,
    max_bytes: int = MAX_ATTACHMENT_BYTES,
) -> bool:
    """Attach the HTML test report when it exists and fits in an e-mail."""
    # A build that fails before the tests has no report, and its e-mail still goes out.
    if not report_path.is_file():
        return False

    size = report_path.stat().st_size
    if size > max_bytes:
        print(
            f"notify_email: report not attached: {size} bytes exceeds the {max_bytes} limit",
            file=sys.stderr,
        )
        return False

    try:
        content = report_path.read_bytes()
    except OSError as error:
        # An unreadable report must not stop the notification.
        print(f"notify_email: report not attached: {error}", file=sys.stderr)
        return False

    message.add_attachment(
        content,
        maintype="text",
        subtype="html",
        filename=REPORT_FILENAME,
        # pytest-html writes the report in UTF-8.
        params={"charset": "utf-8"},
    )
    return True


def send_message(config: EmailConfig, message: EmailMessage) -> None:
    """Deliver ``message`` through the configured SMTP server."""
    with smtplib.SMTP(config.host, config.port, timeout=SMTP_TIMEOUT_SECONDS) as smtp:
        if config.starttls:
            smtp.starttls()
        # Mailpit accepts mail without login; Gmail requires it.
        if config.user and config.password:
            smtp.login(config.user, config.password)
        smtp.send_message(message)


def main(argv: Sequence[str] | None = None, env: Mapping[str, str] = os.environ) -> int:
    """Send the notification for the build status given on the command line."""
    parser = argparse.ArgumentParser(description="Send the build notification e-mail.")
    parser.add_argument(
        "--status", required=True, help="build result, e.g. SUCCESS or FAILURE"
    )
    args = parser.parse_args(argv)

    try:
        config = load_config(env)
    except ConfigError as error:
        print(f"notify_email: configuration error: {error}", file=sys.stderr)
        return 2

    subject = build_subject(args.status, env, detect_origin(env))
    body = build_body(args.status, env) + "\n" + build_report_summary(REPORTS_DIR)
    message = build_message(config, subject, body)

    try:
        send_message(config, message)
    except (OSError, smtplib.SMTPException) as error:
        print(
            f"notify_email: could not send through {config.host}:{config.port}: {error}",
            file=sys.stderr,
        )
        return 1

    print(f"notify_email: sent {message['Subject']!r} to {len(config.recipients)} recipient(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
