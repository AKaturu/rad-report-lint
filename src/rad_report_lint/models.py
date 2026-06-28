from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel


class Severity(StrEnum):
    error = "error"
    warning = "warning"
    info = "info"


class ReportSection(StrEnum):
    technique = "technique"
    history = "history"
    comparison = "comparison"
    findings = "findings"
    impression = "impression"


class Laterality(StrEnum):
    right = "right"
    left = "left"
    bilateral = "bilateral"
    midline = "midline"
    unspecified = "unspecified"


class ParsedReport(BaseModel):
    text: str
    sections: dict[str, str] = {}
    findings: list[Finding] = []
    measurements: list[Measurement] = []
    abbreviations: dict[str, str] = {}


class Finding(BaseModel):
    body_part: str
    laterality: Laterality = Laterality.unspecified
    is_normal: bool = False
    text: str = ""
    measurement_refs: list[int] = []


class Measurement(BaseModel):
    body_part: str
    laterality: Laterality = Laterality.unspecified
    value_mm: float | None = None
    text: str = ""


class LintIssue(BaseModel):
    rule_name: str
    severity: Severity
    message: str
    line: int | None = None
    snippet: str | None = None


class SyntheticReport(BaseModel):
    text: str
    expected_issues: list[LintIssue] = []
