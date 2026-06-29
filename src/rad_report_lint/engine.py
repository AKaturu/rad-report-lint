from __future__ import annotations

from rad_report_lint.models import LintIssue, ParsedReport
from rad_report_lint.report_parser import parse_report
from rad_report_lint.rules import RuleRegistry, default_registry


class LintEngine:
    def __init__(self, registry: RuleRegistry | None = None):
        self.registry = registry or default_registry()

    @staticmethod
    def _sort_issues(issues: list[LintIssue]) -> None:
        issues.sort(
            key=lambda x: (
                {"error": 0, "warning": 1, "info": 2}[x.severity.value],
                x.rule_name,
            )
        )

    def lint(self, text: str) -> list[LintIssue]:
        report = parse_report(text)
        issues = self.registry.run_all(report)
        self._sort_issues(issues)
        return issues

    def lint_with_report(self, text: str) -> tuple[ParsedReport, list[LintIssue]]:
        report = parse_report(text)
        issues = self.registry.run_all(report)
        self._sort_issues(issues)
        return report, issues
