import json

from rad_report_lint.exporter import export_json
from rad_report_lint.models import LintIssue, Severity


def test_export_json_empty():
    result = export_json([])
    data = json.loads(result)
    assert data == []


def test_export_json_with_issues():
    issues = [
        LintIssue(
            rule_name="test-rule",
            severity=Severity.error,
            message="Test error",
            line=5,
            snippet="test snippet",
        ),
        LintIssue(
            rule_name="test-rule-2",
            severity=Severity.warning,
            message="Test warning",
        ),
    ]
    result = export_json(issues)
    data = json.loads(result)
    assert len(data) == 2
    assert data[0]["rule"] == "test-rule"
    assert data[0]["severity"] == "error"
    assert data[0]["line"] == 5
    assert data[1]["rule"] == "test-rule-2"
    assert data[1]["severity"] == "warning"
    assert data[1]["line"] is None
