from __future__ import annotations

import re

from rad_report_lint.models import LintIssue, ParsedReport, Severity
from rad_report_lint.rules.base import Rule

_AMBIGUOUS_PRONOUNS = re.compile(
    r"\b(this|that|these|those|it|such)\s+(finding|structure|"
    r"lesion|mass|nodule|area|region|abnormality|process)\b",
    re.IGNORECASE,
)

_HEDGE_WORDS = [
    "may", "might", "could", "possibly", "probably",
    "likely", "unlikely", "suggestive", "suggests",
    "cannot be excluded", "cannot exclude", "may represent",
    "could represent", "raises the possibility",
    "is suspected", "is considered", "appears to",
    "seems to", "rather than", "or",
]


class AmbiguousPronouns(Rule):
    name = "ambiguous-pronouns"
    description = "Pronoun without clear antecedent"

    def check(self, report: ParsedReport) -> list[LintIssue]:
        issues: list[LintIssue] = []
        all_text = " ".join(report.sections.values()) if report.sections else report.text

        for m in _AMBIGUOUS_PRONOUNS.finditer(all_text):
            issues.append(
                LintIssue(
                    rule_name=self.name,
                    severity=Severity.info,
                    message=f"Ambiguous pronoun: '{m.group(0)}' may lack "
                            f"a clear antecedent",
                    snippet=m.group(0),
                )
            )

        return issues


class ExcessiveHedging(Rule):
    name = "excessive-hedging"
    description = "Excessive use of hedging language"

    def check(self, report: ParsedReport) -> list[LintIssue]:
        issues: list[LintIssue] = []
        all_text = " ".join(report.sections.values()) if report.sections else report.text
        text_lower = all_text.lower()

        hedge_count = 0
        for word in _HEDGE_WORDS:
            count = len(re.findall(r"\b" + re.escape(word) + r"\b", text_lower))
            hedge_count += count

        if hedge_count >= 5:
            issues.append(
                LintIssue(
                    rule_name=self.name,
                    severity=Severity.warning,
                    message=f"Excessive hedging ({hedge_count} instances); "
                            f"consider more definitive language",
                )
            )

        return issues


class UnexpandedAbbreviations(Rule):
    name = "unexpanded-abbreviations"
    description = "Abbreviations not defined at first use"

    _ABBREVIATION_PATTERN = re.compile(r"\b([A-Z]{2,})(?:s\b|\b)")

    def check(self, report: ParsedReport) -> list[LintIssue]:
        issues: list[LintIssue] = []
        all_text = " ".join(report.sections.values()) if report.sections else report.text

        defined: set[str] = set()
        expanded_forms: list[str] = []

        for m in re.finditer(r"\(([A-Z]{2,})\)", all_text):
            abbr = m.group(1)
            defined.add(abbr)

        for m in re.finditer(r"([A-Z]{2,})\s*\(", all_text):
            potential = m.group(1)
            expanded_forms.append(potential)

        defined.update(expanded_forms)

        for m in self._ABBREVIATION_PATTERN.finditer(all_text):
            abbr = m.group(1)
            if len(abbr) >= 2 and abbr not in defined:
                issues.append(
                    LintIssue(
                        rule_name=self.name,
                        severity=Severity.info,
                        message=f"Unexpanded abbreviation: '{abbr}'",
                        snippet=abbr,
                    )
                )

        return issues
