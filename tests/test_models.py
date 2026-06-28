from rad_report_lint.models import (
    Finding,
    Laterality,
    LintIssue,
    Measurement,
    ParsedReport,
    ReportSection,
    Severity,
    SyntheticReport,
)


def test_finding_defaults():
    f = Finding(body_part="liver")
    assert f.body_part == "liver"
    assert f.laterality == Laterality.unspecified
    assert f.is_normal is False


def test_measurement():
    m = Measurement(body_part="nodule", laterality=Laterality.right, value_mm=8.0)
    assert m.body_part == "nodule"
    assert m.value_mm == 8.0


def test_lint_issue():
    issue = LintIssue(
        rule_name="test-rule",
        severity=Severity.error,
        message="Something is wrong",
    )
    assert issue.rule_name == "test-rule"
    assert issue.severity == Severity.error


def test_parsed_report():
    r = ParsedReport(text="test", sections={ReportSection.findings: "normal"})
    assert r.text == "test"
    assert r.sections[ReportSection.findings.value] == "normal"


def test_synthetic_report():
    sr = SyntheticReport(text="test", expected_issues=[])
    assert sr.text == "test"


def test_severity_enum():
    assert Severity.error == "error"
    assert Severity.warning == "warning"
    assert Severity.info == "info"


def test_laterality_enum():
    assert Laterality.right == "right"
    assert Laterality.left == "left"
    assert Laterality.bilateral == "bilateral"
