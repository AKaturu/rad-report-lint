from __future__ import annotations

import re
from typing import ClassVar

from rad_report_lint.models import LintIssue, ParsedReport, Severity
from rad_report_lint.rules.base import Rule

_MODALITY_MAPPING = {
    "CT": ["ct", "computed tomography", "helical"],
    "MRI": ["mri", "mr", "magnetic resonance"],
    "US": ["ultrasound", "sonogram", "sonography", "echo"],
    "XR": ["x-ray", "radiograph", "plain film"],
    "PET": ["pet", "positron emission"],
    "MAMMO": ["mammogram", "mammography", "tomosynthesis"],
    "FLUORO": ["fluoroscopy", "fluoro", "upper gi", "barium"],
    "ANGIO": ["angiography", "angiogram", "dsa"],
    "NUC_MED": ["nuclear medicine", "nuclear", "spect"],
}


class ModalityMismatch(Rule):
    name = "modality-mismatch"
    description = "Report findings reference a modality inconsistent with the report type"

    def check(self, report: ParsedReport) -> list[LintIssue]:
        issues: list[LintIssue] = []
        all_text = " ".join(report.sections.values()) if report.sections else report.text

        detected_modalities: set[str] = set()
        text_lower = all_text.lower()

        for modality, keywords in _MODALITY_MAPPING.items():
            for kw in keywords:
                if kw in text_lower:
                    detected_modalities.add(modality)
                    break

        if len(detected_modalities) > 1:
            issues.append(
                LintIssue(
                    rule_name=self.name,
                    severity=Severity.warning,
                    message=f"Modality mismatch detected: report references "
                            f"multiple modalities ({', '.join(sorted(detected_modalities))})",
                )
            )

        return issues


class DuplicatedFindings(Rule):
    name = "duplicated-findings"
    description = "Same finding appears verbatim multiple times"

    def check(self, report: ParsedReport) -> list[LintIssue]:
        issues: list[LintIssue] = []
        all_text = " ".join(report.sections.values()) if report.sections else report.text

        sentences = [
            s.strip().rstrip(".!?") for s in re.split(r"[.!?]\s+", all_text) if s.strip()
        ]
        seen: dict[str, int] = {}

        for s in sentences:
            key = s.lower()
            seen[key] = seen.get(key, 0) + 1

        for text, count in seen.items():
            if count > 1 and len(text) > 20:
                issues.append(
                    LintIssue(
                        rule_name=self.name,
                        severity=Severity.warning,
                        message=f"Duplicated finding ({count}x): '{text}'",
                    )
                )

        return issues


class CriticalFindingOmitted(Rule):
    name = "critical-finding-omitted"
    description = "Critical finding in body but not mentioned in impression"

    _CRITICAL_TERMS: ClassVar[list[str]] = [
        "mass", "nodule", "fracture", "hemorrhage", "infarct",
        "abscess", "malignancy", "cancer", "tumor", "dissection",
        "pneumothorax", "perforation", "obstruction", "embolism",
        "aneurysm", "stroke", "ischemia",
    ]

    def check(self, report: ParsedReport) -> list[LintIssue]:
        issues: list[LintIssue] = []

        findings_text = report.sections.get("findings") or ""
        impression_text = report.sections.get("impression") or ""

        if not findings_text or not impression_text:
            return issues

        findings_lower = findings_text.lower()
        impression_lower = impression_text.lower()

        for term in self._CRITICAL_TERMS:
            if term in findings_lower and term not in impression_lower:
                issues.append(
                    LintIssue(
                        rule_name=self.name,
                        severity=Severity.error,
                        message=f"'{term}' mentioned in findings but omitted "
                                f"from impression",
                    )
                )

        return issues


class InconsistentMeasurements(Rule):
    name = "inconsistent-measurements"
    description = "Same structure measured at different sizes"

    def check(self, report: ParsedReport) -> list[LintIssue]:
        issues: list[LintIssue] = []
        body_measurements: dict[str, list[float]] = {}

        for m in report.measurements:
            key = f"{m.body_part}:{m.laterality.value}"
            if m.value_mm is not None:
                if key not in body_measurements:
                    body_measurements[key] = []
                body_measurements[key].append(m.value_mm)

        for key, values in body_measurements.items():
            if len(values) >= 2:
                max_v = max(values)
                min_v = min(values)
                if max_v > min_v * 1.2:
                    body, lat = key.split(":")
                    issues.append(
                        LintIssue(
                            rule_name=self.name,
                            severity=Severity.warning,
                            message=f"Inconsistent measurements for '{body}' "
                                    f"({lat}): {min(values):.1f}mm to "
                                    f"{max(values):.1f}mm (>{20:.0f}% variation)",
                        )
                    )

        return issues
