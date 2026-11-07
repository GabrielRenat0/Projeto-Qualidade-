"""Unit tests for ``scripts/notify_email.py``, with a fake SMTP server."""

import pytest

from scripts import notify_email
from scripts.notify_email import ConfigError, EmailConfig

pytestmark = pytest.mark.unit

GMAIL_ENV = {
    "NOTIFY_EMAIL_TO": "ana@example.com, bruno@example.com",
    "SMTP_HOST": "smtp.example.com",
    "SMTP_PORT": "587",
    "SMTP_USER": "bot@example.com",
    "SMTP_PASSWORD": "app-password",
    "SMTP_STARTTLS": "true",
}

JENKINS_ENV = {
    "JOB_NAME": "projeto-qualidade",
    "BUILD_NUMBER": "42",
    "GIT_BRANCH": "origin/main",
    "GIT_COMMIT": "a321775",
    "BUILD_DURATION": "1 min 5 sec",
    "BUILD_URL": "http://localhost:8080/job/projeto-qualidade/42/",
}


def make_config(**overrides) -> EmailConfig:
    """Return a Mailpit-like configuration, changed by ``overrides``."""
    values = {
        "recipients": ("ana@example.com",),
        "sender": "bot@example.com",
        "host": "mailpit",
        "port": 1025,
        "user": "",
        "password": "",
        "starttls": False,
    }
    values.update(overrides)
    return EmailConfig(**values)


# load_config


def test_load_config_reads_every_setting():
    config = notify_email.load_config(GMAIL_ENV)

    assert config == EmailConfig(
        recipients=("ana@example.com", "bruno@example.com"),
        sender="bot@example.com",
        host="smtp.example.com",
        port=587,
        user="bot@example.com",
        password="app-password",
        starttls=True,
    )


def test_load_config_defaults_to_mailpit():
    config = notify_email.load_config(
        {"NOTIFY_EMAIL_TO": "ana@example.com", "SMTP_FROM": "bot@example.com"}
    )

    assert (config.host, config.port, config.starttls) == ("mailpit", 1025, False)
    assert (config.user, config.password) == ("", "")


def test_load_config_ignores_blank_recipients():
    config = notify_email.load_config({**GMAIL_ENV, "NOTIFY_EMAIL_TO": " ana@example.com, ,"})

    assert config.recipients == ("ana@example.com",)


@pytest.mark.parametrize("value", [None, "", " , "])
def test_load_config_requires_a_recipient(value):
    env = {key: val for key, val in GMAIL_ENV.items() if key != "NOTIFY_EMAIL_TO"}
    if value is not None:
        env["NOTIFY_EMAIL_TO"] = value

    with pytest.raises(ConfigError, match="NOTIFY_EMAIL_TO"):
        notify_email.load_config(env)


def test_load_config_rejects_a_port_that_is_not_a_number():
    with pytest.raises(ConfigError, match="SMTP_PORT"):
        notify_email.load_config({**GMAIL_ENV, "SMTP_PORT": "abc"})


def test_load_config_prefers_smtp_from_over_the_user():
    config = notify_email.load_config({**GMAIL_ENV, "SMTP_FROM": "builds@example.com"})

    assert config.sender == "builds@example.com"


def test_load_config_requires_a_sender():
    with pytest.raises(ConfigError, match="SMTP_FROM"):
        notify_email.load_config({"NOTIFY_EMAIL_TO": "ana@example.com"})


@pytest.mark.parametrize(
    ("value", "expected"),
    [("true", True), (" YES ", True), ("1", True), ("on", True), ("false", False), ("", False)],
)
def test_load_config_reads_starttls_as_a_flag(value, expected):
    config = notify_email.load_config({**GMAIL_ENV, "SMTP_STARTTLS": value})

    assert config.starttls is expected


# build_subject and build_body


def test_build_subject_has_the_status_and_the_build_number():
    assert notify_email.build_subject("success", JENKINS_ENV) == "[SUCCESS] projeto-qualidade #42"


def test_build_subject_outside_jenkins_uses_the_default_job():
    assert notify_email.build_subject(" failure ", {}) == "[FAILURE] projeto-qualidade"


def test_build_body_lists_the_jenkins_details():
    body = notify_email.build_body("FAILURE", JENKINS_ENV)

    assert body == (
        "Build status: FAILURE\n"
        "\n"
        "Job: projeto-qualidade\n"
        "Build: #42\n"
        "Branch: origin/main\n"
        "Commit: a321775\n"
        "Duration: 1 min 5 sec\n"
        "Link: http://localhost:8080/job/projeto-qualidade/42/\n"
    )


def test_build_body_outside_jenkins_skips_the_missing_details():
    assert notify_email.build_body("SUCCESS", {}) == (
        "Build status: SUCCESS\n\nJob: projeto-qualidade\n"
    )


def test_build_body_falls_back_to_the_branch_parameter():
    body = notify_email.build_body("SUCCESS", {"BRANCH": "feat/notify-email"})

    assert "Branch: feat/notify-email\n" in body


# build_message


def test_build_message_sets_the_headers_and_the_body():
    config = make_config(recipients=("ana@example.com", "bruno@example.com"))

    message = notify_email.build_message(config, "[SUCCESS] job #1", "Body\n")

    assert message["From"] == "bot@example.com"
    assert message["To"] == "ana@example.com, bruno@example.com"
    assert message["Subject"] == "[SUCCESS] job #1"
    assert message.get_content() == "Body\n"
