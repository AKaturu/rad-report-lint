from rad_report_lint.rules.base import Rule, RuleRegistry
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

__all__ = [
    "AmbiguousPronouns",
    "ContradictoryLaterality",
    "CriticalFindingOmitted",
    "DuplicatedFindings",
    "EmptyImpression",
    "ExcessiveHedging",
    "FindingsImpressionContradiction",
    "InconsistentMeasurements",
    "MissingComparisonDate",
    "ModalityMismatch",
    "NormalAbnormalConflict",
    "RecommendationWithoutInterval",
    "Rule",
    "RuleRegistry",
    "TemplatePlaceholders",
    "UnexpandedAbbreviations",
]


def default_registry() -> RuleRegistry:
    registry = RuleRegistry()
    registry.register(ContradictoryLaterality())
    registry.register(NormalAbnormalConflict())
    registry.register(ModalityMismatch())
    registry.register(DuplicatedFindings())
    registry.register(MissingComparisonDate())
    registry.register(EmptyImpression())
    registry.register(RecommendationWithoutInterval())
    registry.register(CriticalFindingOmitted())
    registry.register(InconsistentMeasurements())
    registry.register(AmbiguousPronouns())
    registry.register(ExcessiveHedging())
    registry.register(UnexpandedAbbreviations())
    registry.register(TemplatePlaceholders())
    registry.register(FindingsImpressionContradiction())
    return registry
