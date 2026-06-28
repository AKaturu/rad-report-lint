from __future__ import annotations

import json

from rich.console import Console
from rich.table import Table

from rad_report_lint.models import LintIssue, ParsedReport, Severity

console = Console()


def print_lint_results(report: ParsedReport, issues: list[LintIssue]) -> None:
    if not issues:
        console.print("[green]✓ No issues found![/green]")
        return

    for sev in (Severity.error, Severity.warning, Severity.info):
        filtered = [i for i in issues if i.severity == sev]
        if not filtered:
            continue

        label = sev.value.upper()
        color = {"error": "red", "warning": "yellow", "info": "blue"}[sev.value]
        console.print(f"\n[bold {color}]{label}[/bold {color}]")

        for issue in filtered:
            line_info = f" [dim](line {issue.line})[/dim]" if issue.line else ""
            snippet_info = f"  [dim]`{issue.snippet}`[/dim]" if issue.snippet else ""
            console.print(f"  [{color}]•[/{color}] [{color}]{issue.rule_name}[/{color}]"
                          f"{line_info}")
            console.print(f"    {issue.message}{snippet_info}")

    console.print(f"\n[bold]Total: {len(issues)} issue(s)[/bold]")
    error_count = sum(1 for i in issues if i.severity == Severity.error)
    warning_count = sum(1 for i in issues if i.severity == Severity.warning)
    if error_count:
        console.print(f"  [red]{error_count} error(s)[/red]")
    if warning_count:
        console.print(f"  [yellow]{warning_count} warning(s)[/yellow]")


def export_json(issues: list[LintIssue]) -> str:
    data = [
        {
            "rule": i.rule_name,
            "severity": i.severity.value,
            "message": i.message,
            "line": i.line,
            "snippet": i.snippet,
        }
        for i in issues
    ]
    return json.dumps(data, indent=2)


def print_rules_table(rules: list) -> None:
    table = Table(title="Available Rules")
    table.add_column("Rule Name", style="cyan")
    table.add_column("Description")

    for rule in rules:
        table.add_row(rule.name, rule.description)

    console.print(table)
