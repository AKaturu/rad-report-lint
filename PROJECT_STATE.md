# rad-report-lint — Project State

## Status: Complete

A deterministic linter for radiology reports with 14 rules, CLI, and full CI.

## What's Built

### Source (`src/rad_report_lint/`)
- **models.py** — ParsedReport, Finding, Measurement, LintIssue, SyntheticReport + StrEnum types (Severity, ReportSection, Laterality)
- **report_parser.py** — regex-based section splitter, findings extractor (body part + laterality + normal/abnormal), measurement extractor
- **rules/** — 14 rule classes in 5 files:
  - `contradictions.py`: ContradictoryLaterality, NormalAbnormalConflict, FindingsImpressionContradiction
  - `completeness.py`: MissingComparisonDate, EmptyImpression, RecommendationWithoutInterval
  - `consistency.py`: ModalityMismatch, DuplicatedFindings, CriticalFindingOmitted, InconsistentMeasurements
  - `clarity.py`: AmbiguousPronouns, ExcessiveHedging, UnexpandedAbbreviations
  - `placeholders.py`: TemplatePlaceholders
- **rules/base.py** — Rule ABC + RuleRegistry with register/get/get_all/run_all
- **rules/\_\_init\_\_.py** — default_registry() factory
- **engine.py** — LintEngine: lint(text), lint_with_report(text)
- **synthetic.py** — generate_demo_report() for 11 scenarios, generate_all_demo_reports()
- **cli.py** — 4 Typer commands: lint, check, demo, rules
- **exporter.py** — Rich table output + JSON export

### Tests (`tests/`)
- 79 tests across 6 files (models, parser, rules, engine, synthetic, exporter)
- All passing on Python 3.11 and 3.12

### Validation
- ruff: clean
- mypy: 0 errors (20 source files)
- CI: GitHub Actions (ruff -> mypy -> pytest -> demo) green on both versions

### Delivery
- GitHub: https://github.com/AKaturu/rad-report-lint
- MIT License
- `rad-report-lint` CLI entry point

## No Known Issues
- All tests pass
- No mypy errors
- No ruff violations
