"""Consolidated pytest-html report: the group of each test and the summary per group.

The pytest hooks stay in conftest.py and only call this module, so the report
logic is unit tested like any other code.
"""

from collections import Counter
from html import escape
import re

TEST_CASE_GROUPS = {
    "Integrante A": (1, 5),
    "Integrante B": (6, 10),
    "Integrante C": (11, 15),
    "Integrante D": (16, 20),
}
UNIT_GROUP = "Testes unitários"
UNCLASSIFIED_GROUP = "Não classificado"

# pytest node IDs always use forward slashes, on Windows too.
UNIT_TESTS_FOLDER = "tests/unit/"
TEST_CASE_PATTERN = re.compile(r"tc[-_]?(\d{3})", flags=re.IGNORECASE)

GROUP_HEADER_CELL = "<th>Grupo</th>"


def report_group(nodeid: str) -> str:
    """Return the group of the test in ``nodeid``: its integrante or the unit tests."""
    if nodeid.startswith(UNIT_TESTS_FOLDER):
        return UNIT_GROUP

    match = TEST_CASE_PATTERN.search(nodeid)
    if match:
        test_case = int(match.group(1))
        for integrante, (first_case, last_case) in TEST_CASE_GROUPS.items():
            if first_case <= test_case <= last_case:
                return integrante
    return UNCLASSIFIED_GROUP


def report_title() -> str:
    """Return a title that covers the 20 test cases and the unit tests."""
    first_case = min(first for first, _ in TEST_CASE_GROUPS.values())
    last_case = max(last for _, last in TEST_CASE_GROUPS.values())
    return (
        f"Relatório consolidado — TC-{first_case:03d} a TC-{last_case:03d} "
        "e testes unitários"
    )


def group_cell(nodeid: str) -> str:
    """Return the results table cell that shows the group of ``nodeid``."""
    return f'<td class="col-group">{escape(report_group(nodeid))}</td>'


def _group_scope(group: str) -> str:
    """Return what ``group`` covers, as shown in the summary."""
    if group == UNIT_GROUP:
        return UNIT_TESTS_FOLDER.rstrip("/")
    first_case, last_case = TEST_CASE_GROUPS[group]
    return f"TC-{first_case:03d} a TC-{last_case:03d}"


class ReportSummary:
    """Count the outcomes of each group and render them for the report summary."""

    def __init__(self) -> None:
        self._counts: dict[str, Counter[str]] = {}

    def record(self, nodeid: str, outcome: str) -> None:
        """Count one ``outcome`` (passed, failed or skipped) for the group of ``nodeid``."""
        self._counts.setdefault(report_group(nodeid), Counter())[outcome] += 1

    def html_lines(self) -> list[str]:
        """Return the summary lines, one per group that ran, in report order."""
        lines = ["<h3>Resultados por grupo</h3>", "<ul>"]
        for group in [*TEST_CASE_GROUPS, UNIT_GROUP]:
            counts = self._counts.get(group)
            if not counts:
                continue
            total = sum(counts.values())
            status = ", ".join(
                f"{amount} {outcome}" for outcome, amount in sorted(counts.items())
            )
            lines.append(
                f"<li><strong>{group}</strong> — {_group_scope(group)}: "
                f"{total} execuções ({escape(status)}).</li>"
            )
        lines.append("</ul>")
        return lines
