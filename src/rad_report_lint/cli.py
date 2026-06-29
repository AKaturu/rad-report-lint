from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from rad_report_lint.engine import LintEngine
from rad_report_lint.exporter import (
    export_json,
    print_lint_results,
    print_rules_table,
)
from rad_report_lint.rules import default_registry
from rad_report_lint.models import Severity
from rad_report_lint.synthetic import generate_all_demo_reports, generate_demo_report

app = typer.Typer(
    name="rad-report-lint",
    help="A deterministic linter for radiology reports",
)
console = Console()


@app.command()
def lint(
    file: Path = typer.Argument(  # noqa: B008
        None,
        help="Path to a radiology report text file",
        exists=True,
        readable=True,
    ),
    text: str = typer.Option(None, help="Report text to lint (inline)"),
    json_output: bool = typer.Option(
        False, "--json", help="Output results as JSON",
    ),
):
    """Lint a radiology report for quality issues."""
    engine = LintEngine()

    if text:
        report_text = text
    elif file:
        report_text = file.read_text(encoding="utf-8")
    else:
        report_text = typer.prompt("Paste report text")

    parsed, issues = engine.lint_with_report(report_text)

    if json_output:
        console.print(export_json(issues))
    else:
        print_lint_results(parsed, issues)


@app.command()
def demo(
    scenario: str = typer.Argument(
        None,
        help="Specific scenario to demonstrate",
    ),
    list_scenarios: bool = typer.Option(
        False, "--list", help="List available demo scenarios",
    ),
):
    """Generate and lint a synthetic radiology report."""
    engine = LintEngine()

    if list_scenarios:
        scenarios = [
            "normal",
            "contradictory-laterality",
            "normal-abnormal-conflict",
            "missing-comparison-date",
            "empty-impression",
            "recommendation-without-interval",
            "critical-omitted",
            "hedging",
            "placeholder",
            "findings-impression-contradiction",
            "duplicated",
        ]
        console.print("[bold]Available scenarios:[/bold]")
        for s in scenarios:
            console.print(f"  - {s}")
        return

    if scenario:
        text = generate_demo_report(scenario)
        if not text:
            console.print(f"[red]Unknown scenario: {scenario}[/red]")
            raise typer.Exit(code=1)
        console.print("[bold]Report:[/bold]\n")
        console.print(text)
        console.print("\n" + "=" * 60 + "\n")
        parsed, issues = engine.lint_with_report(text)
        print_lint_results(parsed, issues)
    else:
        reports = generate_all_demo_reports()
        total_issues = 0
        for name, text in sorted(reports.items()):
            console.print(f"\n[bold cyan]═══ {name} ═══[/bold cyan]")
            console.print(text[:200] + ("..." if len(text) > 200 else ""))
            parsed, issues = engine.lint_with_report(text)
            total_issues += len(issues)
            print_lint_results(parsed, issues)
        console.print(f"\n[bold]Total issues across all demo reports: {total_issues}[/bold]")


@app.command()
def rules():
    """List all available lint rules."""
    registry = default_registry()
    print_rules_table(registry.get_all())


@app.command()
def check(
    file: Path = typer.Argument(  # noqa: B008
        ..., help="Path to report text file", exists=True, readable=True,
    ),
):
    """Lint a file and exit with non-zero status if any errors found."""
    engine = LintEngine()
    text = file.read_text(encoding="utf-8")
    issues = engine.lint(text)

    if issues:
        parsed, _ = engine.lint_with_report(text)
        print_lint_results(parsed, issues)
        has_errors = any(i.severity == Severity.error for i in issues)
        raise typer.Exit(code=1 if has_errors else 0)
    else:
        console.print("[green]✓ No issues found![/green]")


if __name__ == "__main__":
    app()
