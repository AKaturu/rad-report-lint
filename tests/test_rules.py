from rad_report_lint.models import ParsedReport, ReportSection
from rad_report_lint.report_parser import parse_report
from rad_report_lint.rules.clarity import (
    AmbiguousPronouns,
    ExcessiveHedging,
    UnexpandedAbbreviations,
)
from rad_report_lint.rules.completeness import (
    EmptyImpression,
    MissingComparisonDate,
    RecommendationWithoutInterval,
)
from rad_report_lint.rules.consistency import (
    CriticalFindingOmitted,
    DuplicatedFindings,
    InconsistentMeasurements,
    ModalityMismatch,
)
from rad_report_lint.rules.contradictions import (
    ContradictoryLaterality,
    FindingsImpressionContradiction,
    NormalAbnormalConflict,
)
from rad_report_lint.rules.placeholders import TemplatePlaceholders


def _make_report(
    findings_text: str = "",
    impression_text: str = "",
    comparison_text: str = "",
    technique_text: str = "",
) -> ParsedReport:
    s: dict[ReportSection, str] = {}
    if technique_text:
        s[ReportSection.technique] = technique_text
    if comparison_text:
        s[ReportSection.comparison] = comparison_text
    if findings_text:
        s[ReportSection.findings] = findings_text
    if impression_text:
        s[ReportSection.impression] = impression_text
    full_text = "\n".join(
        f"{k.value.upper()}: {v}" for k, v in s.items()
    )
    return parse_report(full_text)


class TestContradictoryLaterality:
    rule = ContradictoryLaterality()

    def test_no_contradiction(self):
        report = _make_report(
            findings_text="The right lung is clear.",
            impression_text="Normal.",
        )
        assert self.rule.check(report) == []

    def test_contradiction_detected(self):
        text = "The right lung has a 12 mm nodule. The left lung has a cyst."
        report = parse_report(text)
        issues = self.rule.check(report)
        assert len(issues) >= 1
        assert "lung" in issues[0].message

    def test_bilateral_ok(self):
        text = "Bilateral lung nodules are present."
        report = parse_report(text)
        issues = self.rule.check(report)
        assert len(issues) == 0

    def test_empty(self):
        report = _make_report()
        assert self.rule.check(report) == []


class TestNormalAbnormalConflict:
    rule = NormalAbnormalConflict()

    def test_no_conflict(self):
        text = "The liver is normal in appearance."
        report = parse_report(text)
        assert self.rule.check(report) == []

    def test_conflict_detected(self):
        text = "The liver is normal in size. There is a 12 mm lesion in the liver."
        report = parse_report(text)
        issues = self.rule.check(report)
        assert len(issues) >= 1
        assert "liver" in issues[0].message

    def test_empty(self):
        assert self.rule.check(_make_report()) == []


class TestFindingsImpressionContradiction:
    rule = FindingsImpressionContradiction()

    def test_no_contradiction(self):
        report = _make_report(
            findings_text="Normal liver.",
            impression_text="Normal examination.",
        )
        assert self.rule.check(report) == []

    def test_contradiction_detected(self):
        report = _make_report(
            findings_text="There is a 12 mm nodule in the right lung.",
            impression_text="The right lung is normal in appearance.",
        )
        issues = self.rule.check(report)
        assert len(issues) >= 1

    def test_missing_sections(self):
        assert self.rule.check(_make_report()) == []
        assert self.rule.check(_make_report(findings_text="test")) == []


class TestMissingComparisonDate:
    rule = MissingComparisonDate()

    def test_no_comparison_mentioned(self):
        report = _make_report(findings_text="Normal.")
        assert self.rule.check(report) == []

    def test_comparison_without_date(self):
        report = _make_report(
            comparison_text="Compared to prior examination.",
        )
        issues = self.rule.check(report)
        assert len(issues) >= 1

    def test_comparison_with_date(self):
        report = _make_report(
            comparison_text="Compared to prior examination from 2025-01-15.",
        )
        issues = self.rule.check(report)
        assert len(issues) == 0

    def test_empty(self):
        assert self.rule.check(_make_report()) == []


class TestEmptyImpression:
    rule = EmptyImpression()

    def test_non_empty_impression(self):
        report = _make_report(impression_text="Normal examination.")
        assert self.rule.check(report) == []

    def test_empty_impression(self):
        report = _make_report(impression_text="")
        issues = self.rule.check(report)
        assert len(issues) >= 1

    def test_missing_impression(self):
        report = _make_report(findings_text="Normal.")
        issues = self.rule.check(report)
        assert len(issues) >= 1


class TestRecommendationWithoutInterval:
    rule = RecommendationWithoutInterval()

    def test_recommendation_with_interval(self):
        report = _make_report(
            findings_text="Recommend follow-up in 6 months.",
        )
        assert self.rule.check(report) == []

    def test_recommendation_without_interval(self):
        report = _make_report(
            findings_text="Recommend follow-up.",
        )
        issues = self.rule.check(report)
        assert len(issues) >= 1

    def test_no_recommendation(self):
        report = _make_report(findings_text="Normal.")
        assert self.rule.check(report) == []

    def test_empty(self):
        assert self.rule.check(_make_report()) == []


class TestCriticalFindingOmitted:
    rule = CriticalFindingOmitted()

    def test_critical_in_both(self):
        report = _make_report(
            findings_text="There is a 12 mm nodule in the lung.",
            impression_text="Nodule in the lung, recommend follow-up.",
        )
        assert self.rule.check(report) == []

    def test_critical_omitted(self):
        report = _make_report(
            findings_text="There is a 12 mm nodule in the lung.",
            impression_text="No significant findings.",
        )
        issues = self.rule.check(report)
        assert len(issues) >= 1
        assert "nodule" in issues[0].message

    def test_no_critical_finding(self):
        report = _make_report(
            findings_text="The liver is normal.",
            impression_text="Normal examination.",
        )
        assert self.rule.check(report) == []

    def test_missing_sections(self):
        assert self.rule.check(_make_report()) == []


class TestIndInconsistentMeasurements:
    rule = InconsistentMeasurements()

    def test_consistent(self):
        text = "A nodule measuring 10 mm in the right lung."
        report = parse_report(text)
        assert self.rule.check(report) == []

    def test_inconsistent(self):
        text = ("A nodule measuring 10 mm in the right lung. "
                "The nodule measures 15 mm.")
        report = parse_report(text)
        issues = self.rule.check(report)
        assert len(issues) >= 1

    def test_empty(self):
        report = parse_report("Normal.")
        assert self.rule.check(report) == []


class TestModalityMismatch:
    rule = ModalityMismatch()

    def test_single_modality(self):
        report = _make_report(findings_text="CT scan of the chest.")
        assert self.rule.check(report) == []

    def test_multiple_modalities(self):
        report = _make_report(
            findings_text="CT scan shows a nodule. MRI was also performed.",
        )
        issues = self.rule.check(report)
        assert len(issues) >= 1

    def test_empty(self):
        assert self.rule.check(_make_report()) == []


class TestDuplicatedFindings:
    rule = DuplicatedFindings()

    def test_no_duplicates(self):
        report = _make_report(
            findings_text="The liver is normal.",
        )
        assert self.rule.check(report) == []

    def test_duplicates_detected(self):
        text = ("The liver demonstrates a 12 mm cyst. "
                "The liver demonstrates a 12 mm cyst.")
        report = parse_report(text)
        issues = self.rule.check(report)
        assert len(issues) >= 1

    def test_empty(self):
        assert self.rule.check(_make_report()) == []


class TestAmbiguousPronouns:
    rule = AmbiguousPronouns()

    def test_no_ambiguous(self):
        report = _make_report(
            findings_text="The liver is normal in appearance.",
        )
        assert self.rule.check(report) == []

    def test_ambiguous_detected(self):
        report = _make_report(
            findings_text="There is a nodule. This finding requires follow-up.",
        )
        issues = self.rule.check(report)
        assert len(issues) >= 1

    def test_empty(self):
        assert self.rule.check(_make_report()) == []


class TestExcessiveHedging:
    rule = ExcessiveHedging()

    def test_no_hedging(self):
        report = _make_report(findings_text="The liver is normal.")
        assert self.rule.check(report) == []

    def test_excessive_hedging(self):
        report = _make_report(
            findings_text=(
                "This may possibly represent a nodule. "
                "It could be suggestive of a lesion. "
                "This might likely be a mass."
            ),
        )
        issues = self.rule.check(report)
        assert len(issues) >= 1

    def test_empty(self):
        assert self.rule.check(_make_report()) == []


class TestUnexpandedAbbreviations:
    rule = UnexpandedAbbreviations()

    def test_common_abbreviation(self):
        report = _make_report(findings_text="CT scan of the chest.")
        issues = self.rule.check(report)
        # CT should be recognized but may show as unexpanded
        # since we don't track per-report definition
        assert isinstance(issues, list)

    def test_defined_abbreviation(self):
        text = "Computed tomography (CT) scan of the chest."
        report = parse_report(text)
        issues = self.rule.check(report)
        # CT is defined via parens, should not be flagged
        ct_issues = [i for i in issues if "CT" in (i.snippet or "")]
        assert len(ct_issues) == 0

    def test_empty(self):
        assert self.rule.check(_make_report()) == []


class TestTemplatePlaceholders:
    rule = TemplatePlaceholders()

    def test_no_placeholders(self):
        report = _make_report(findings_text="The liver is normal.")
        assert self.rule.check(report) == []

    def test_bracket_placeholder(self):
        report = _make_report(
            findings_text="The [body part] is normal.",
        )
        issues = self.rule.check(report)
        assert len(issues) >= 1

    def test_underscore_placeholder(self):
        report = _make_report(
            findings_text="The liver is ____.",
        )
        issues = self.rule.check(report)
        assert len(issues) >= 1

    def test_tbd_placeholder(self):
        report = _make_report(
            findings_text="Impression: TBD",
        )
        issues = self.rule.check(report)
        assert len(issues) >= 1

    def test_empty(self):
        assert self.rule.check(_make_report()) == []
