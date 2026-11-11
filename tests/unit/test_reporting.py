"""Unit tests for ``reporting.py``, the logic behind the consolidated HTML report."""

import pytest

from reporting import (
    UNCLASSIFIED_GROUP,
    UNIT_GROUP,
    ReportSummary,
    group_cell,
    report_group,
    report_title,
)

pytestmark = pytest.mark.unit

VALID_TESTS = "tests/test_valid_data.py"
INVALID_TESTS = "tests/test_invalid_data.py"


# report_group


@pytest.mark.parametrize(
    ("nodeid", "group"),
    [
        (f"{VALID_TESTS}::test_tc001_list_all_posts", "Integrante A"),
        (f"{VALID_TESTS}::test_tc005_get_user_with_nested_objects", "Integrante A"),
        (f"{VALID_TESTS}::test_tc006_filter_completed_todos", "Integrante B"),
        (f"{VALID_TESTS}::test_tc010_delete_post", "Integrante B"),
        (f"{INVALID_TESTS}::test_tc011_get_post_outside_valid_id_range[0]", "Integrante C"),
        (f"{INVALID_TESTS}::test_tc015_filter_comments_by_negative_post_id", "Integrante C"),
        (f"{INVALID_TESTS}::test_tc016_create_empty_post", "Integrante D"),
        (f"{INVALID_TESTS}::test_tc020_get_post_after_delete", "Integrante D"),
    ],
)
def test_report_group_maps_each_test_case_to_its_integrante(nodeid, group):
    assert report_group(nodeid) == group


@pytest.mark.parametrize("test_case", ["TC-012", "tc_012", "Tc012"])
def test_report_group_accepts_any_test_case_spelling(test_case):
    assert report_group(f"{INVALID_TESTS}::test_{test_case}_check") == "Integrante C"


def test_report_group_puts_every_unit_test_in_its_own_group():
    assert report_group("tests/unit/test_helpers.py::test_load_payloads") == UNIT_GROUP
    # The folder wins over a test case number in the name.
    assert report_group("tests/unit/test_example.py::test_tc001_like") == UNIT_GROUP


@pytest.mark.parametrize(
    "nodeid",
    [
        f"{VALID_TESTS}::test_tc021_outside_the_plan",
        f"{VALID_TESTS}::test_without_a_test_case_number",
    ],
)
def test_report_group_leaves_unknown_tests_unclassified(nodeid):
    assert report_group(nodeid) == UNCLASSIFIED_GROUP


# report_title and group_cell


def test_report_title_covers_the_test_cases_and_the_unit_tests():
    assert report_title() == "Relatório consolidado — TC-001 a TC-020 e testes unitários"


def test_group_cell_shows_the_group_of_the_test():
    cell = group_cell(f"{INVALID_TESTS}::test_tc013_get_nonexistent_route")

    assert cell == '<td class="col-group">Integrante C</td>'


# ReportSummary


def test_report_summary_without_results_has_only_the_heading():
    assert ReportSummary().html_lines() == ["<h3>Resultados por grupo</h3>", "<ul>", "</ul>"]


def test_report_summary_counts_each_outcome_per_group():
    summary = ReportSummary()
    summary.record(f"{VALID_TESTS}::test_tc001_list_all_posts", "passed")
    summary.record(f"{VALID_TESTS}::test_tc002_get_post_at_valid_boundaries[1]", "passed")
    summary.record(f"{VALID_TESTS}::test_tc003_filter_posts_by_user_id", "failed")

    assert summary.html_lines()[2] == (
        "<li><strong>Integrante A</strong> — TC-001 a TC-005: "
        "3 execuções (1 failed, 2 passed).</li>"
    )


def test_report_summary_lists_the_groups_in_report_order():
    summary = ReportSummary()
    summary.record("tests/unit/test_helpers.py::test_load_payloads", "passed")
    summary.record(f"{INVALID_TESTS}::test_tc016_create_empty_post", "passed")
    summary.record(f"{VALID_TESTS}::test_tc006_filter_completed_todos", "skipped")

    lines = summary.html_lines()

    assert lines[2].startswith("<li><strong>Integrante B</strong> — TC-006 a TC-010")
    assert lines[3].startswith("<li><strong>Integrante D</strong> — TC-016 a TC-020")
    assert lines[4] == (
        "<li><strong>Testes unitários</strong> — tests/unit: 1 execuções (1 passed).</li>"
    )
    assert lines[-1] == "</ul>"


def test_report_summary_leaves_out_unclassified_tests():
    summary = ReportSummary()
    summary.record(f"{VALID_TESTS}::test_without_a_test_case_number", "passed")

    assert UNCLASSIFIED_GROUP not in "".join(summary.html_lines())
