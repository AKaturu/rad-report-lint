# rad-report-lint — Project Status

## Current Release

**v0.1.0** — Initial release providing a deterministic linter for radiology reports with 14 rules, CLI, and full CI.

## Implemented Features

- 14 deterministic lint rules: contradictory laterality, normal/abnormal conflict, modality mismatch, duplicated findings, missing comparison date, empty impression, recommendation without interval, critical finding omitted, inconsistent measurements, ambiguous pronouns, excessive hedging, unexpanded abbreviations, template placeholders, findings–impression contradiction
- Regex-based report parser (section splitter, findings extractor, measurement extractor)
- LintEngine with multi-rule orchestration
- Rich table and JSON output
- Synthetic demo reports for 11 scenarios
- Typer CLI with 4 commands: lint, check, demo, rules

## Quality Gates

- 79 tests across 6 files — all passing on Python 3.11 and 3.12
- No ruff violations
- No mypy errors (20 source files)
- CI: GitHub Actions green on both versions

## Known Issues

- None at this release
