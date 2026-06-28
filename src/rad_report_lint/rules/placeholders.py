from __future__ import annotations

import re
from typing import ClassVar

from rad_report_lint.models import LintIssue, ParsedReport, Severity
from rad_report_lint.rules.base import Rule


class TemplatePlaceholders(Rule):
    name = "template-placeholders"
    description = "Unfilled template placeholders left in report"

    _PLACEHOLDER_PATTERNS: ClassVar[list[re.Pattern]] = [
        re.compile(r"\[.*?\]"),
        re.compile(r"\{.*?\}"),
        re.compile(r"<.*?>"),
        re.compile(r"_{2,}(\s*_{2,})?"),
        re.compile(r"\bTBD\b"),
        re.compile(r"\bTODO\b"),
        re.compile(r"\bFILL\s+(?:IN|ME)\b"),
    ]

    def check(self, report: ParsedReport) -> list[LintIssue]:
        issues: list[LintIssue] = []
        all_text = " ".join(report.sections.values()) if report.sections else report.text

        for pattern in self._PLACEHOLDER_PATTERNS:
            for m in pattern.finditer(all_text):
                placeholder = m.group(0)
                if len(placeholder) >= 3:
                    issues.append(
                        LintIssue(
                            rule_name=self.name,
                            severity=Severity.error,
                            message=f"Unfilled template placeholder: "
                                    f"'{placeholder[:50]}'",
                            snippet=placeholder[:50],
                        )
                    )

        return issues
