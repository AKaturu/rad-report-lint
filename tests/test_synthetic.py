from rad_report_lint.synthetic import (
    generate_all_demo_reports,
    generate_demo_report,
)


def test_generate_demo_report_returns_string():
    text = generate_demo_report("normal")
    assert isinstance(text, str)
    assert len(text) > 50


def test_generate_demo_report_known_scenario():
    text = generate_demo_report("empty-impression")
    assert "IMPRESSION" in text


def test_generate_demo_report_unknown_scenario():
    text = generate_demo_report("nonexistent-scenario")
    assert text is None


def test_generate_demo_report_random():
    text = generate_demo_report(None)
    assert isinstance(text, str)
    assert len(text) > 50


def test_generate_all_demo_reports():
    reports = generate_all_demo_reports()
    assert len(reports) == 11
    for name, text in reports.items():
        assert len(text) > 20, f"Report {name} is too short"
