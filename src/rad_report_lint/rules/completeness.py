from __future__ import annotations

import re

from rad_report_lint.models import LintIssue, ParsedReport, Severity
from rad_report_lint.rules.base import Rule


class MissingComparisonDate(Rule):
    name = "missing-comparison-date"
    description = "Report mentions comparison but no prior exam date"

    def check(self, report: ParsedReport) -> list[LintIssue]:
        issues: list[LintIssue] = []
        all_text = " ".join(report.sections.values()) if report.sections else report.text

        has_comparison_words = bool(
            re.search(
                r"\b(?:compared?|comparison|prior|previous|earlier|follow.up)\b",
                all_text,
                re.IGNORECASE,
            )
        )

        if not has_comparison_words:
            return issues

        has_date = bool(re.search(r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b", all_text))

        has_age = bool(
            re.search(r"\b\d+\s*(?:month|year|week|day)[s]?\s+(?:ago|prior|earlier|old)\b", all_text, re.IGNORECASE)
        )

        if not has_date and not has_age:
            issues.append(
                LintIssue(
                    rule_name=self.name,
                    severity=Severity.warning,
                    message="Report mentions prior/comparison but no comparison date found",
                )
            )

        return issues


class EmptyImpression(Rule):
    name = "empty-impression"
    description = "Impression section is empty or missing"

    def check(self, report: ParsedReport) -> list[LintIssue]:
        issues: list[LintIssue] = []

        impression = report.sections.get("impression") or ""
        if not impression.strip():
            issues.append(
                LintIssue(
                    rule_name=self.name,
                    severity=Severity.error,
                    message="Impression section is empty or missing",
                )
            )

        return issues


class RecommendationWithoutInterval(Rule):
    name = "recommendation-without-interval"
    description = "Recommendation made without specified time interval"

    def check(self, report: ParsedReport) -> list[LintIssue]:
        issues: list[LintIssue] = []
        all_text = " ".join(report.sections.values()) if report.sections else report.text

        recommendation_patterns = re.findall(
            r"\b(?:recommend|follow.up|repeat|rescan|surveillance|monitor|"
            r"reimage|re-evaluate)\b",
            all_text,
            re.IGNORECASE,
        )

        if not recommendation_patterns:
            return issues

        has_interval = bool(
            re.search(
                r"\bin\s+\d+\s*(?:month|year|week|day)[s]?\b",
                all_text,
                re.IGNORECASE,
            )
        )

        has_date = bool(
            re.search(
                r"\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b",
                all_text,
                re.IGNORECASE,
            )
        )

        if not has_interval and not has_date:
            issues.append(
                LintIssue(
                    rule_name=self.name,
                    severity=Severity.warning,
                    message=f"Recommendation made ({recommendation_patterns[0]}) "
                            f"without specified interval or date",
                )
            )

        return issues
