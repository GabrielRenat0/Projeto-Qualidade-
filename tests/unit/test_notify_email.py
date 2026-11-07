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
