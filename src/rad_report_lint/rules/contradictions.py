from __future__ import annotations

from rad_report_lint.models import Laterality, LintIssue, ParsedReport, Severity
from rad_report_lint.rules.base import Rule


class ContradictoryLaterality(Rule):
    name = "contradictory-laterality"
    description = "Same body part mentioned with conflicting laterality"

    def check(self, report: ParsedReport) -> list[LintIssue]:
        issues: list[LintIssue] = []
        body_lats: dict[str, set[Laterality]] = {}

        for f in report.findings:
            key = f.body_part
            if key not in body_lats:
                body_lats[key] = set()
            body_lats[key].add(f.laterality)

        for body, lats in body_lats.items():
            if Laterality.right in lats and Laterality.left in lats and Laterality.bilateral not in lats:
                issues.append(
                    LintIssue(
                        rule_name=self.name,
                        severity=Severity.error,
                        message=f"Contradictory laterality for '{body}': "
                                f"described as both right and left",
                    )
                )
        return issues


class NormalAbnormalConflict(Rule):
    name = "normal-abnormal-conflict"
    description = "Same body part described as both normal and abnormal"

    def check(self, report: ParsedReport) -> list[LintIssue]:
        issues: list[LintIssue] = []
        body_states: dict[str, set[bool]] = {}

        for f in report.findings:
            key = f"{f.body_part}:{f.laterality.value}"
            if key not in body_states:
                body_states[key] = set()
            body_states[key].add(f.is_normal)

        for key, states in body_states.items():
            if True in states and False in states:
                body_part, lat = key.split(":")
                issues.append(
                    LintIssue(
                        rule_name=self.name,
                        severity=Severity.error,
                        message=f"'{body_part}' ({lat}) described as both "
                                f"normal and abnormal",
                    )
                )
        return issues


class FindingsImpressionContradiction(Rule):
    name = "findings-impression-contradiction"
    description = "A finding in the body contradicts the impression"

    def check(self, report: ParsedReport) -> list[LintIssue]:
        issues: list[LintIssue] = []

        findings_text = report.sections.get("findings") or ""
        impression_text = report.sections.get("impression") or ""

        if not findings_text or not impression_text:
            return issues

        from rad_report_lint.report_parser import extract_findings

        impression_findings = extract_findings(impression_text)

        imp_normal_body_parts: set[str] = set()
        imp_abnormal_body_parts: set[str] = set()

        for f in impression_findings:
            key = f"{f.body_part}:{f.laterality.value}"
            if f.is_normal:
                imp_normal_body_parts.add(key)
            else:
                imp_abnormal_body_parts.add(key)

        findings_findings = extract_findings(findings_text)
        for f in findings_findings:
            key = f"{f.body_part}:{f.laterality.value}"
            if not f.is_normal and key in imp_normal_body_parts:
                issues.append(
                    LintIssue(
                        rule_name=self.name,
                        severity=Severity.error,
                        message=f"Findings mention abnormal '{f.body_part}' "
                                f"({f.laterality.value}) but impression "
                                f"describes it as normal",
                    )
                )
            elif f.is_normal and key in imp_abnormal_body_parts:
                issues.append(
                    LintIssue(
                        rule_name=self.name,
                        severity=Severity.error,
                        message=f"Findings describe '{f.body_part}' "
                                f"({f.laterality.value}) as normal but "
                                f"impression mentions it as abnormal",
                    )
                )

        return issues
