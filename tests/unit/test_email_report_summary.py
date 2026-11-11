"""Unit tests for the test and coverage summary of ``scripts/notify_email.py``."""

from pathlib import Path
from unittest import mock

import pytest

from scripts import notify_email

pytestmark = pytest.mark.unit

# The same attributes that pytest and coverage.py write in their reports.
JUNIT_XML = (
    '<?xml version="1.0" encoding="utf-8"?>'
    '<testsuites><testsuite name="pytest" errors="1" failures="2" skipped="3" tests="95" '
    'time="3.345" timestamp="2026-11-10T22:32:09.455159-03:00" hostname="ci">'
    '<testcase classname="tests.test_valid_data" name="test_tc001_list_all_posts" time="0.1" />'
    "</testsuite></testsuites>"
)
COVERAGE_XML = (
    '<?xml version="1.0" ?>'
    '<coverage version="7.17.2" timestamp="1794360732730" lines-valid="198" '
    'lines-covered="196" line-rate="0.9899" branches-covered="0" branches-valid="0" '
    'branch-rate="0" complexity="0"><packages /></coverage>'
)

TESTS_LINE = "Tests: 95 (passed: 89, failed: 2, errors: 1, skipped: 3)\n"
COVERAGE_LINE = "Coverage: 98.99%\n"


def write_reports(
    folder: Path, junit: str | None = JUNIT_XML, coverage: str | None = COVERAGE_XML
) -> Path:
    """Write the given reports to ``folder`` (``None`` leaves one out) and return it."""
    if junit is not None:
        (folder / "junit.xml").write_text(junit, encoding="utf-8")
    if coverage is not None:
        (folder / "coverage.xml").write_text(coverage, encoding="utf-8")
    return folder


# Both reports present


def test_summary_lists_the_test_totals_and_the_coverage(tmp_path):
    summary = notify_email.build_report_summary(write_reports(tmp_path))

    assert summary == TESTS_LINE + COVERAGE_LINE


def test_summary_adds_up_several_test_suites(tmp_path):
    junit = (
        "<testsuites>"
        '<testsuite errors="0" failures="1" skipped="0" tests="20" />'
        '<testsuite errors="1" failures="0" skipped="2" tests="5" />'
        "</testsuites>"
    )

    summary = notify_email.build_report_summary(write_reports(tmp_path, junit=junit))

    assert summary == "Tests: 25 (passed: 21, failed: 1, errors: 1, skipped: 2)\n" + COVERAGE_LINE


def test_summary_reads_a_report_whose_root_is_the_test_suite(tmp_path):
    junit = '<testsuite errors="0" failures="0" skipped="1" tests="4" />'

    summary = notify_email.build_report_summary(write_reports(tmp_path, junit=junit))

    assert summary == "Tests: 4 (passed: 3, failed: 0, errors: 0, skipped: 1)\n" + COVERAGE_LINE


@pytest.mark.parametrize(
    ("line_rate", "expected"),
    [("1", "100.00%"), ("0.9086", "90.86%"), ("0", "0.00%")],
)
def test_summary_shows_the_coverage_with_two_decimals(tmp_path, line_rate, expected):
    coverage = f'<coverage line-rate="{line_rate}" />'

    summary = notify_email.build_report_summary(write_reports(tmp_path, coverage=coverage))

    assert summary == TESTS_LINE + f"Coverage: {expected}\n"


# Missing reports


def test_summary_without_the_junit_report_says_it_was_not_generated(tmp_path):
    summary = notify_email.build_report_summary(write_reports(tmp_path, junit=None))

    assert summary == "Tests: report not generated (reports/junit.xml)\n" + COVERAGE_LINE


def test_summary_without_the_coverage_report_says_it_was_not_generated(tmp_path):
    summary = notify_email.build_report_summary(write_reports(tmp_path, coverage=None))

    assert summary == TESTS_LINE + "Coverage: report not generated (reports/coverage.xml)\n"


def test_summary_without_the_reports_folder_says_nothing_was_generated(tmp_path):
    summary = notify_email.build_report_summary(tmp_path / "reports")

    assert summary == (
        "Tests: report not generated (reports/junit.xml)\n"
        "Coverage: report not generated (reports/coverage.xml)\n"
    )


# Broken reports


@pytest.mark.parametrize(
    "junit",
    ["<testsuites><testsuite tests=", "<report />", '<testsuite tests="many" />'],
    ids=["cut short", "no testsuite element", "total that is not a number"],
)
def test_summary_with_a_broken_junit_report_says_it_could_not_be_read(tmp_path, junit):
    summary = notify_email.build_report_summary(write_reports(tmp_path, junit=junit))

    assert summary == "Tests: report could not be read (reports/junit.xml)\n" + COVERAGE_LINE


@pytest.mark.parametrize(
    "coverage",
    ["<coverage line-rate=", "<coverage />", '<coverage line-rate="high" />'],
    ids=["cut short", "no line-rate", "rate that is not a number"],
)
def test_summary_with_a_broken_coverage_report_says_it_could_not_be_read(tmp_path, coverage):
    summary = notify_email.build_report_summary(write_reports(tmp_path, coverage=coverage))

    assert summary == TESTS_LINE + "Coverage: report could not be read (reports/coverage.xml)\n"


def test_summary_with_a_folder_in_place_of_a_report_says_it_could_not_be_read(tmp_path):
    write_reports(tmp_path, junit=None)
    (tmp_path / "junit.xml").mkdir()

    summary = notify_email.build_report_summary(tmp_path)

    assert summary == "Tests: report could not be read (reports/junit.xml)\n" + COVERAGE_LINE


# Default folder


def test_the_default_reports_folder_sits_next_to_the_scripts_folder():
    repository_root = notify_email.REPORTS_DIR.parent

    assert notify_email.REPORTS_DIR.name == "reports"
    assert (repository_root / "scripts" / "notify_email.py").is_file()


# The summary in the e-mail body

EMAIL_ENV = {"NOTIFY_EMAIL_TO": "ana@example.com", "SMTP_FROM": "bot@example.com"}


def send_and_read_body(monkeypatch, reports_dir: Path, status: str) -> str:
    """Run the script with a fake SMTP server and return the body of the e-mail it sends."""
    monkeypatch.setattr(notify_email, "REPORTS_DIR", reports_dir)
    with mock.patch.object(notify_email.smtplib, "SMTP") as smtp_class:
        exit_code = notify_email.main(["--status", status], EMAIL_ENV)

    assert exit_code == 0
    session = smtp_class.return_value.__enter__.return_value
    return session.send_message.call_args.args[0].get_content()


def test_main_adds_the_summary_after_the_build_details(tmp_path, monkeypatch):
    body = send_and_read_body(monkeypatch, write_reports(tmp_path), "SUCCESS")

    assert body == (
        "Build status: SUCCESS\n"
        "\n"
        "Job: projeto-qualidade\n"
        "\n"
        "Tests: 95 (passed: 89, failed: 2, errors: 1, skipped: 3)\n"
        "Coverage: 98.99%\n"
    )


def test_main_still_sends_the_email_when_the_reports_were_not_generated(tmp_path, monkeypatch):
    body = send_and_read_body(monkeypatch, tmp_path / "reports", "FAILURE")

    assert body == (
        "Build status: FAILURE\n"
        "\n"
        "Job: projeto-qualidade\n"
        "\n"
        "Tests: report not generated (reports/junit.xml)\n"
        "Coverage: report not generated (reports/coverage.xml)\n"
    )
