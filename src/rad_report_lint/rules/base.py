from __future__ import annotations

from abc import ABC, abstractmethod

from rad_report_lint.models import LintIssue, ParsedReport


class Rule(ABC):
    name: str
    description: str

    @abstractmethod
    def check(self, report: ParsedReport) -> list[LintIssue]:
        ...


class RuleRegistry:
    def __init__(self):
        self._rules: dict[str, Rule] = {}

    def register(self, rule: Rule) -> None:
        self._rules[rule.name] = rule

    def get(self, name: str) -> Rule | None:
        return self._rules.get(name)

    def get_all(self) -> list[Rule]:
        return list(self._rules.values())

    def run_all(self, report: ParsedReport) -> list[LintIssue]:
        issues: list[LintIssue] = []
        for rule in self._rules.values():
            issues.extend(rule.check(report))
        return issues
