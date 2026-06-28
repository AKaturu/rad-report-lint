from rad_report_lint.models import Laterality, ReportSection
from rad_report_lint.report_parser import (
    extract_findings,
    extract_measurements,
    parse_report,
    split_sections,
)


def test_split_sections():
    text = """FINDINGS: The liver is normal.
IMPRESSION: Normal examination."""
    sections = split_sections(text)
    assert ReportSection.findings in sections
    assert ReportSection.impression in sections
    assert "liver" in sections[ReportSection.findings]
    assert "Normal examination" in sections[ReportSection.impression]


def test_split_sections_no_header():
    text = "The liver is normal in appearance."
    sections = split_sections(text)
    assert len(sections) == 0


def test_split_sections_with_colon():
    text = "TECHNIQUE: Standard protocol.\nFINDINGS:\nNormal liver."
    sections = split_sections(text)
    assert ReportSection.technique in sections
    assert ReportSection.findings in sections
    assert "Normal liver" in sections[ReportSection.findings]


def test_extract_findings_normal():
    text = "The liver is normal in size and appearance."
    findings = extract_findings(text)
    assert len(findings) >= 1
    liver_findings = [f for f in findings if f.body_part == "liver"]
    assert len(liver_findings) >= 1
    assert liver_findings[0].is_normal is True


def test_extract_findings_abnormal():
    text = "There is a 12 mm nodule in the right lung."
    findings = extract_findings(text)
    lung_findings = [f for f in findings if f.body_part == "lung"]
    assert len(lung_findings) >= 1
    assert lung_findings[0].laterality == Laterality.right
    assert lung_findings[0].is_normal is False


def test_extract_findings_laterality():
    text = "The left kidney is normal. The right kidney has a cyst."
    findings = extract_findings(text)
    left = [f for f in findings if f.laterality == Laterality.left]
    right = [f for f in findings if f.laterality == Laterality.right]
    assert len(left) >= 1
    assert len(right) >= 1


def test_extract_measurements():
    text = "A 12 mm nodule in the right lung. A 8 mm cyst in the liver."
    measurements = extract_measurements(text)
    assert len(measurements) >= 2
    values = [m.value_mm for m in measurements if m.value_mm is not None]
    assert 12.0 in values
    assert 8.0 in values


def test_parse_report_full():
    text = """FINDINGS: The liver is normal. A 15 mm nodule in the right lung.
IMPRESSION: Normal examination."""
    parsed = parse_report(text)
    assert len(parsed.sections) == 2
    assert len(parsed.findings) >= 1
    assert len(parsed.measurements) >= 1


def test_parse_report_no_sections():
    text = "The liver is normal in appearance."
    parsed = parse_report(text)
    assert len(parsed.sections) == 0
    assert len(parsed.findings) >= 1


def test_extract_findings_empty():
    assert extract_findings("") == []
    assert extract_findings("   ") == []


def test_extract_measurements_empty():
    assert extract_measurements("") == []
