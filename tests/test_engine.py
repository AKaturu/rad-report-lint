from rad_report_lint.engine import LintEngine
from rad_report_lint.models import Severity
from rad_report_lint.rules import default_registry


def test_engine_creates_with_default_registry():
    engine = LintEngine()
    assert len(engine.registry.get_all()) == 14


def test_engine_clean_report():
    engine = LintEngine()
    text = """FINDINGS: The liver is normal in size and appearance. The spleen is normal.
IMPRESSION: Normal examination. No significant findings."""
    issues = engine.lint(text)
    # Should have few or no issues for a clean report
    warnings = [i for i in issues if i.severity == Severity.error]
    assert len(warnings) == 0


def test_engine_with_issues():
    engine = LintEngine()
    text = """FINDINGS: There is a 12 mm nodule in the right lung.
IMPRESSION: Normal examination."""
    issues = engine.lint(text)
    assert len(issues) >= 1


def test_engine_lint_with_report():
    engine = LintEngine()
    text = """FINDINGS: Normal liver.
IMPRESSION: Normal examination."""
    report, issues = engine.lint_with_report(text)
    assert report is not None
    assert isinstance(issues, list)


def test_engine_empty_text():
    engine = LintEngine()
    issues = engine.lint("")
    assert isinstance(issues, list)


def test_engine_custom_registry():

    registry = default_registry()
    engine = LintEngine(registry)
    issues = engine.lint("IMPRESSION:\n")
    empty_impression_issues = [
        i for i in issues if i.rule_name == "empty-impression"
    ]
    assert len(empty_impression_issues) >= 1
