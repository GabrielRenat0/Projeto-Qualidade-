"""Unit tests for the HTML report attachment of ``scripts/notify_email.py``."""

from email.message import EmailMessage
from pathlib import Path
from unittest import mock

import pytest

from scripts import notify_email
from scripts.notify_email import EmailConfig

pytestmark = pytest.mark.unit

# Non-ASCII on purpose: the attachment must keep the UTF-8 text of the report.
REPORT_HTML = "<!DOCTYPE html><html><body><h1>Relatório: 20 passed</h1></body></html>\n"


@pytest.fixture(autouse=True)
def reports_dir(tmp_path, monkeypatch) -> Path:
    """Point the script at an empty temporary reports folder, never the real one."""
    folder = tmp_path / "reports"
    folder.mkdir()
    monkeypatch.setattr(notify_email, "REPORTS_DIR", folder)
    return folder


def make_message() -> EmailMessage:
    """Return a plain-text message, as the script has it before attaching anything."""
    message = EmailMessage()
    message.set_content("Body\n")
    return message


def write_report(folder: Path, content: str = REPORT_HTML) -> Path:
    """Write ``content`` as a report file in ``folder`` and return its path."""
    path = folder / "report.html"
    path.write_bytes(content.encode("utf-8"))
    return path


def attachments_of(message: EmailMessage) -> list[EmailMessage]:
    """Return the attachment parts of ``message``."""
    return list(message.iter_attachments())


# attach_report


def test_attach_report_adds_the_html_file(tmp_path):
    message = make_message()

    attached = notify_email.attach_report(message, write_report(tmp_path))

    assert attached is True
    [attachment] = attachments_of(message)
    assert attachment.get_filename() == "report.html"
    assert attachment.get_content_type() == "text/html"
    assert attachment.get_content_disposition() == "attachment"
    assert attachment.get_content() == REPORT_HTML


def test_attach_report_keeps_the_text_body(tmp_path):
    message = make_message()

    notify_email.attach_report(message, write_report(tmp_path))

    assert message.get_body().get_content() == "Body\n"


def test_attach_report_always_names_the_attachment_report_html(tmp_path):
    source = tmp_path / "another-name.html"
    source.write_bytes(REPORT_HTML.encode("utf-8"))
    message = make_message()

    notify_email.attach_report(message, source)

    [attachment] = attachments_of(message)
    assert attachment.get_filename() == "report.html"


def test_attach_report_without_a_report_leaves_the_message_alone(tmp_path, capsys):
    message = make_message()

    attached = notify_email.attach_report(message, tmp_path / "report.html")

    assert attached is False
    assert attachments_of(message) == []
    assert message.get_content() == "Body\n"
    assert capsys.readouterr().err == ""


def test_attach_report_ignores_a_directory_with_the_report_name(tmp_path):
    folder = tmp_path / "report.html"
    folder.mkdir()
    message = make_message()

    assert notify_email.attach_report(message, folder) is False
    assert attachments_of(message) == []


def test_attach_report_skips_a_report_over_the_limit(tmp_path, capsys):
    report = write_report(tmp_path)
    size = report.stat().st_size
    message = make_message()

    attached = notify_email.attach_report(message, report, max_bytes=size - 1)

    assert attached is False
    assert attachments_of(message) == []
    assert f"report not attached: {size} bytes exceeds the {size - 1} limit" in (
        capsys.readouterr().err
    )


def test_attach_report_accepts_a_report_exactly_at_the_limit(tmp_path):
    report = write_report(tmp_path)
    message = make_message()

    attached = notify_email.attach_report(message, report, max_bytes=report.stat().st_size)

    assert attached is True
    assert len(attachments_of(message)) == 1


def test_attach_report_skips_a_report_that_cannot_be_read(tmp_path, capsys):
    report = write_report(tmp_path)
    message = make_message()

    with mock.patch.object(Path, "read_bytes", side_effect=PermissionError("access denied")):
        attached = notify_email.attach_report(message, report)

    assert attached is False
    assert attachments_of(message) == []
    assert "report not attached: access denied" in capsys.readouterr().err


# build_message


def make_config() -> EmailConfig:
    """Return a Mailpit-like configuration."""
    return EmailConfig(
        recipients=("ana@example.com",),
        sender="bot@example.com",
        host="mailpit",
        port=1025,
        user="",
        password="",
        starttls=False,
    )


def test_build_message_attaches_the_report_of_the_reports_folder(reports_dir):
    write_report(reports_dir)

    message = notify_email.build_message(make_config(), "[SUCCESS] job #1", "Body\n")

    [attachment] = attachments_of(message)
    assert attachment.get_filename() == "report.html"
    assert attachment.get_content() == REPORT_HTML
    assert message["Subject"] == "[SUCCESS] job #1"
    assert message.get_body().get_content() == "Body\n"


def test_build_message_without_a_report_stays_plain_text():
    message = notify_email.build_message(make_config(), "[FAILURE] job #1", "Body\n")

    assert attachments_of(message) == []
    assert message.get_content_type() == "text/plain"
    assert message.get_content() == "Body\n"


def test_build_message_reads_the_reports_folder_on_every_call(
    reports_dir, tmp_path, monkeypatch
):
    write_report(reports_dir)
    with_report = notify_email.build_message(make_config(), "subject", "Body\n")

    # A path frozen when the script was imported would still find the first folder.
    monkeypatch.setattr(notify_email, "REPORTS_DIR", tmp_path / "another-folder")
    without_report = notify_email.build_message(make_config(), "subject", "Body\n")

    assert len(attachments_of(with_report)) == 1
    assert attachments_of(without_report) == []
