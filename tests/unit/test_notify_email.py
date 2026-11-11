"""Unit tests for ``scripts/notify_email.py``, with a fake SMTP server."""

import smtplib
from unittest import mock

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
    "JENKINS_URL": "http://localhost:8080/",
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


@pytest.fixture
def smtp():
    """Replace ``smtplib.SMTP`` and yield the fake SMTP class."""
    with mock.patch.object(notify_email.smtplib, "SMTP") as smtp_class:
        yield smtp_class


def session_of(smtp_class: mock.MagicMock) -> mock.MagicMock:
    """Return the fake connection that the ``with`` block of the script receives."""
    return smtp_class.return_value.__enter__.return_value


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


def test_build_subject_ends_with_the_origin():
    subject = notify_email.build_subject("SUCCESS", JENKINS_ENV, "Jenkins")

    assert subject == "[SUCCESS] projeto-qualidade #42 (Jenkins)"


# detect_origin


def test_detect_origin_in_a_jenkins_build(tmp_path):
    # The Jenkins container is also a container, but the build variables win.
    marker = tmp_path / ".dockerenv"
    marker.touch()

    assert notify_email.detect_origin(JENKINS_ENV, marker) == "Jenkins"


def test_detect_origin_in_the_tests_container(tmp_path):
    marker = tmp_path / ".dockerenv"
    marker.touch()

    assert notify_email.detect_origin({}, marker) == "tests container"


def test_detect_origin_on_a_local_machine(tmp_path):
    assert notify_email.detect_origin({}, tmp_path / ".dockerenv") == "local machine"


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


# send_message


def test_send_message_to_mailpit_skips_tls_and_login(smtp):
    config = make_config()
    message = notify_email.build_message(config, "subject", "body")

    notify_email.send_message(config, message)

    smtp.assert_called_once_with("mailpit", 1025, timeout=notify_email.SMTP_TIMEOUT_SECONDS)
    session = session_of(smtp)
    session.starttls.assert_not_called()
    session.login.assert_not_called()
    session.send_message.assert_called_once_with(message)


def test_send_message_to_gmail_uses_tls_and_login(smtp):
    config = notify_email.load_config(GMAIL_ENV)
    message = notify_email.build_message(config, "subject", "body")

    notify_email.send_message(config, message)

    session = session_of(smtp)
    assert session.method_calls == [
        mock.call.starttls(),
        mock.call.login("bot@example.com", "app-password"),
        mock.call.send_message(message),
    ]


# main


def test_main_sends_the_success_email(smtp, capsys):
    exit_code = notify_email.main(["--status", "SUCCESS"], {**GMAIL_ENV, **JENKINS_ENV})

    assert exit_code == 0
    message = session_of(smtp).send_message.call_args.args[0]
    assert message["Subject"] == "[SUCCESS] projeto-qualidade #42 (Jenkins)"
    assert "Build status: SUCCESS" in message.get_content()
    assert (
        "sent '[SUCCESS] projeto-qualidade #42 (Jenkins)' to 2 recipient(s)"
        in capsys.readouterr().out
    )


def test_main_sends_the_failure_email(smtp):
    exit_code = notify_email.main(["--status", "FAILURE"], {**GMAIL_ENV, **JENKINS_ENV})

    assert exit_code == 0
    message = session_of(smtp).send_message.call_args.args[0]
    assert message["Subject"] == "[FAILURE] projeto-qualidade #42 (Jenkins)"
    assert "Build status: FAILURE" in message.get_content()


def test_main_without_recipients_fails_without_connecting(smtp, capsys):
    env = {key: val for key, val in GMAIL_ENV.items() if key != "NOTIFY_EMAIL_TO"}

    exit_code = notify_email.main(["--status", "SUCCESS"], env)

    assert exit_code == 2
    smtp.assert_not_called()
    assert "configuration error: NOTIFY_EMAIL_TO is not set" in capsys.readouterr().err


def test_main_with_the_server_down_reports_the_error(smtp, capsys):
    smtp.side_effect = ConnectionRefusedError("connection refused")

    exit_code = notify_email.main(["--status", "SUCCESS"], GMAIL_ENV)

    assert exit_code == 1
    assert "could not send through smtp.example.com:587" in capsys.readouterr().err


def test_main_with_rejected_login_reports_the_error(smtp, capsys):
    session_of(smtp).login.side_effect = smtplib.SMTPAuthenticationError(535, b"bad password")

    exit_code = notify_email.main(["--status", "SUCCESS"], GMAIL_ENV)

    assert exit_code == 1
    session_of(smtp).send_message.assert_not_called()
    assert "could not send through smtp.example.com:587" in capsys.readouterr().err


def test_main_requires_the_status(smtp):
    with pytest.raises(SystemExit) as exit_info:
        notify_email.main([], GMAIL_ENV)

    assert exit_info.value.code == 2
    smtp.assert_not_called()
