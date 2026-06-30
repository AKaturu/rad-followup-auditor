from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Annotated

import pandas as pd
import typer
from rich.console import Console
from rich.table import Table

from .analysis import compute_summary, load_and_extract, run_analysis, write_json_outputs
from .data import write_synthetic_csv
from .report import generate_report
from .rules import load_extraction_config

app = typer.Typer(
    name="rad-followup-auditor",
    help="Extract and track incidental finding follow-up recommendations from radiology reports.",
    no_args_is_help=True,
)
console = Console()


@app.command()
def demo(
    output: Annotated[Path, typer.Option(help="Output directory.")] = Path(
        "outputs/demo"
    ),
    n: Annotated[int, typer.Option(help="Number of synthetic reports.")] = 100,
    seed: Annotated[int, typer.Option(help="Random seed.")] = 42,
    followup_rate: Annotated[
        float, typer.Option(help="Fraction of reports with follow-up.")
    ] = 0.55,
    pdf: Annotated[bool, typer.Option("--pdf/--no-pdf", help="Attempt PDF export.")] = True,
) -> None:
    """Generate synthetic reports and run extraction."""
    output.mkdir(parents=True, exist_ok=True)

    csv_path = output / "synthetic_reports.csv"
    write_synthetic_csv(csv_path, n=n, seed=seed, followup_rate=followup_rate)
    console.print(f"[green]Wrote {n} synthetic reports:[/green] {csv_path}")

    analysis = run_analysis(csv_path)
    extracted_path = output / "extracted_results.csv"
    analysis.extracted.to_csv(extracted_path, index=False)
    console.print(f"[green]Wrote extraction results:[/green] {extracted_path}")

    summary_path = output / "extraction_summary.csv"
    analysis.summary.to_csv(summary_path, index=False)
    console.print(f"[green]Wrote summary:[/green] {summary_path}")
    for name, path in write_json_outputs(
        analysis.extracted,
        analysis.summary,
        output,
        stats=analysis.stats,
    ).items():
        console.print(f"[green]Wrote {name.replace('_', ' ')}:[/green] {path}")

    _print_summary_table(analysis.summary)

    artifacts = generate_report(
        analysis,
        output,
        include_pdf=pdf,
    )
    console.print(f"[green]Wrote HTML report:[/green] {artifacts.html}")
    if artifacts.pdf:
        console.print(f"[green]Wrote PDF report:[/green] {artifacts.pdf}")
    elif artifacts.pdf_error:
        console.print(f"[yellow]PDF skipped:[/yellow] {artifacts.pdf_error}")


@app.command()
def extract(
    csv: Annotated[
        Path, typer.Option("--csv", help="CSV of radiology reports to process.")
    ],
    output: Annotated[Path, typer.Option(help="Output directory.")] = Path(
        "outputs/extract"
    ),
    custom_patterns: Annotated[
        Path | None,
        typer.Option(help="JSON or text file with custom recommendation regexes."),
    ] = None,
    exclude_patterns: Annotated[
        Path | None,
        typer.Option(help="JSON or text file with false-positive suppression regexes."),
    ] = None,
) -> None:
    """Extract follow-up recommendations from a CSV of reports."""
    output.mkdir(parents=True, exist_ok=True)

    config = load_extraction_config(custom_patterns, exclude_patterns)
    extracted = load_and_extract(csv, config=config)
    extracted_path = output / "extracted_results.csv"
    extracted.to_csv(extracted_path, index=False)
    console.print(f"[green]Wrote extraction results:[/green] {extracted_path}")

    summary = compute_summary(extracted)
    summary_path = output / "extraction_summary.csv"
    summary.to_csv(summary_path, index=False)
    console.print(f"[green]Wrote summary:[/green] {summary_path}")
    for name, path in write_json_outputs(extracted, summary, output).items():
        console.print(f"[green]Wrote {name.replace('_', ' ')}:[/green] {path}")

    _print_summary_table(summary)


@app.command("report")
def report_command(
    csv: Annotated[
        Path,
        typer.Option("--csv", help="CSV of radiology reports to analyze."),
    ],
    output: Annotated[Path, typer.Option(help="Output directory.")] = Path(
        "outputs/report"
    ),
    pdf: Annotated[
        bool, typer.Option("--pdf/--no-pdf", help="Attempt PDF export.")
    ] = True,
    custom_patterns: Annotated[
        Path | None,
        typer.Option(help="JSON or text file with custom recommendation regexes."),
    ] = None,
    exclude_patterns: Annotated[
        Path | None,
        typer.Option(help="JSON or text file with false-positive suppression regexes."),
    ] = None,
) -> None:
    """Generate an HTML report and optional PDF."""
    output.mkdir(parents=True, exist_ok=True)
    config = load_extraction_config(custom_patterns, exclude_patterns)
    analysis = run_analysis(csv, config=config)
    extracted_path = output / "extracted_results.csv"
    analysis.extracted.to_csv(extracted_path, index=False)
    for name, path in write_json_outputs(
        analysis.extracted,
        analysis.summary,
        output,
        stats=analysis.stats,
    ).items():
        console.print(f"[green]Wrote {name.replace('_', ' ')}:[/green] {path}")

    artifacts = generate_report(
        analysis,
        output,
        include_pdf=pdf,
    )
    console.print(f"[green]Wrote HTML report:[/green] {artifacts.html}")
    if artifacts.pdf:
        console.print(f"[green]Wrote PDF report:[/green] {artifacts.pdf}")
    elif artifacts.pdf_error:
        console.print(f"[yellow]PDF skipped:[/yellow] {artifacts.pdf_error}")


@app.command()
def serve(
    host: Annotated[str, typer.Option(help="Streamlit host.")] = "localhost",
    port: Annotated[int, typer.Option(help="Streamlit port.")] = 8501,
) -> None:
    """Launch the Streamlit dashboard."""
    app_path = Path(__file__).parent / "app" / "main.py"
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.address",
        host,
        "--server.port",
        str(port),
    ]
    raise typer.Exit(subprocess.run(cmd, check=False).returncode)


def _print_summary_table(df: pd.DataFrame) -> None:
    import math

    table = Table(title="rad-followup-auditor summary")
    for col in df.columns:
        table.add_column(str(col))
    for row in df.itertuples(index=False):
        vals = []
        for v in row:
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                vals.append("-")
            else:
                vals.append(str(v))
        table.add_row(*vals)
    console.print(table)


if __name__ == "__main__":
    app()
