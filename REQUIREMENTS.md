# rad-report-lint — Requirements

## Overview

A deterministic rule-based linter for radiology reports that identifies quality issues, contradictions, inconsistencies, and missing information.

## Functional Requirements

### Core
- Parse free-text radiology reports into sections (FINDINGS, IMPRESSION, TECHNIQUE, HISTORY, COMPARISON)
- Extract structured findings (body part, laterality, normal/abnormal, measurements)
- Run a suite of lint rules against the parsed report
- Report results in human-readable (Rich table) and machine-readable (JSON) formats

### Lint Rules (14)

1. **Contradictory Laterality** — Error if same body part described with both right and left laterality (without bilateral)
2. **Normal/Abnormal Conflict** — Error if same body part described as both normal and abnormal
3. **Modality Mismatch** — Warning if report references multiple imaging modalities
4. **Duplicated Findings** — Warning if same finding sentence appears verbatim more than once
5. **Missing Comparison Date** — Warning if report mentions prior comparison but no date or age is given
6. **Empty Impression** — Error if impression section is empty or missing
7. **Recommendation Without Interval** — Warning if follow-up recommended without a time frame
8. **Critical Finding Omitted** — Error if critical finding (mass, nodule, fracture, etc.) appears in findings but not impression
9. **Inconsistent Measurements** — Warning if same structure is measured at significantly different sizes (>20% variation)
10. **Ambiguous Pronouns** — Info if pronoun like "this finding" lacks clear antecedent
11. **Excessive Hedging** — Warning if ≥5 hedging terms (may, could, possibly, etc.) are used
12. **Unexpanded Abbreviations** — Info if abbreviations are not defined at first use via parenthetical expansion
13. **Template Placeholders** — Error if brackets [...], braces {...}, underscores ___, or TBD/TODO/FILL IN remain
14. **Findings–Impression Contradiction** — Error if findings describe an abnormal finding but impression calls it normal (or vice versa)

### CLI
- `rad-report-lint lint [file]` — Lint a report file or stdin
- `rad-report-lint check <file>` — Lint, exit non-zero on errors (CI mode)
- `rad-report-lint demo [scenario]` — Generate and lint synthetic reports
- `rad-report-lint rules` — List all available rules
- `--json` flag for JSON output

### Data
- All rules are deterministic (no ML/AI)
- Synthetic report generator for demo and testing
- No external API dependencies

## Non-Functional Requirements
- Python >=3.11
- Same project conventions as rad-device-watch (setuptools, src/ layout, ruff, mypy, pytest)
- Zero external runtime dependencies beyond typer, rich, pydantic
- Tests for every rule

## Acceptance Criteria
- All 14 rules produce correct results on known-good and known-bad reports
- CLI demo command generates reports that trigger each rule
- `ruff check .` clean
- `mypy src tests` clean
- 100% of scenarios from synthetic generator correctly trigger expected rules
