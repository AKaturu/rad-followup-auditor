from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd
from jinja2 import Template

from .. import __version__
from ..analysis import AnalysisOutput

HTML_TEMPLATE = Template("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>rad-followup-auditor Report</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #1a1a2e; background: #f0f2f5; line-height: 1.6; padding: 2rem; }
  .container { max-width: 1000px; margin: 0 auto; }
  h1 { font-size: 1.8rem; margin-bottom: 0.25rem; }
  .subtitle { color: #666; margin-bottom: 2rem; }
  .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
  .stat-card { background: #fff; border-radius: 12px; padding: 1.25rem; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
  .stat-card .label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #666; }
  .stat-card .value { font-size: 1.5rem; font-weight: 700; margin-top: 0.25rem; }
  .stat-card .pct { font-size: 0.9rem; color: #666; }
  table { width: 100%; border-collapse: collapse; background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.08); margin-bottom: 2rem; }
  th { background: #1a1a2e; color: #fff; padding: 0.75rem 1rem; text-align: left; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; }
  td { padding: 0.75rem 1rem; border-bottom: 1px solid #eee; }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: #f8f9ff; }
  .badge { display: inline-block; padding: 0.15rem 0.5rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; }
  .badge-high { background: #d4edda; color: #155724; }
  .badge-medium { background: #fff3cd; color: #856404; }
  .badge-low { background: #f8d7da; color: #721c24; }
  .badge-yes { background: #d4edda; color: #155724; }
  .badge-no { background: #e2e3e5; color: #383d41; }
  .badge-urgent { background: #f8d7da; color: #721c24; }
  .extractions-table { font-size: 0.85rem; }
  .extractions-table td { max-width: 250px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .footer { text-align: center; color: #999; font-size: 0.8rem; margin-top: 3rem; }
</style>
</head>
<body>
<div class="container">
  <h1>rad-followup-auditor Report</h1>
  <p class="subtitle">Generated {{ generated_at }} &mdash; {{ stats.total }} reports analyzed</p>

  <div class="stats-grid">
    <div class="stat-card">
      <div class="label">Total Reports</div>
      <div class="value">{{ stats.total }}</div>
    </div>
    <div class="stat-card">
      <div class="label">With Recommendations</div>
      <div class="value">{{ stats.with_recommendations }}</div>
      <div class="pct">{{ stats.recommendation_rate }}%</div>
    </div>
    <div class="stat-card">
      <div class="label">Negated</div>
      <div class="value">{{ stats.negated }}</div>
      <div class="pct">{{ stats.negation_rate }}%</div>
    </div>
    <div class="stat-card">
      <div class="label">Review Required</div>
      <div class="value">{{ stats.review_required }}</div>
    </div>
  </div>

  <h2>Summary Metrics</h2>
  <table>
    <thead><tr><th>Metric</th><th>Value</th></tr></thead>
    <tbody>
    {% for row in summary_rows %}
    <tr>
      <td>{{ row.metric }}</td>
      <td>
        {% if row.pct is defined and row.pct is not none %}
          {{ row.value }} ({{ row.pct }}%)
        {% else %}
          {{ row.value }}
        {% endif %}
      </td>
    </tr>
    {% endfor %}
    </tbody>
  </table>

  <h2>Extracted Recommendations</h2>
  {% if extractions %}
  <table class="extractions-table">
    <thead>
      <tr>
        <th>Report ID</th>
        <th>Finding</th>
        <th>Modality</th>
        <th>Interval</th>
        <th>Urgency</th>
        <th>Region</th>
        <th>Confidence</th>
        <th>Review</th>
      </tr>
    </thead>
    <tbody>
    {% for r in extractions %}
    <tr>
      <td>{{ r.report_id }}</td>
      <td>{{ r.finding or '-' }}</td>
      <td>{{ r.recommended_modality or '-' }}</td>
      <td>{% if r.interval_value %}{{ r.interval_value }} {{ r.interval_unit }}{% else %}-{% endif %}</td>
      <td>{% if r.urgency %}<span class="badge badge-{{ r.urgency }}">{{ r.urgency }}</span>{% else %}-{% endif %}</td>
      <td>{{ r.anatomic_region or '-' }}</td>
      <td><span class="badge badge-{{ r.confidence }}">{{ r.confidence }}</span></td>
      <td>{% if r.review_required %}<span class="badge badge-urgent">REQUIRED</span>{% else %}<span class="badge badge-no">OK</span>{% endif %}</td>
    </tr>
    {% endfor %}
    </tbody>
  </table>
  {% else %}
  <p>No recommendations extracted.</p>
  {% endif %}

  <div class="footer">
    <p>rad-followup-auditor v{{ version }} &mdash; Powered by rad-followup-auditor</p>
  </div>
</div>
</body>
</html>""")


@dataclass
class ReportArtifacts:
    html: Path
    pdf: Path | None = None
    pdf_error: str | None = None


def generate_report(
    analysis: AnalysisOutput,
    output_dir: str | Path,
    basename: str = "rad_followup_auditor_report",
    include_pdf: bool = True,
) -> ReportArtifacts:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_rows = []
    if not analysis.summary.empty:
        for _, row in analysis.summary.iterrows():
            entry = {"metric": row.get("metric", ""), "value": row.get("value", "")}
            if "pct" in row.index and pd.notna(row.get("pct")):
                entry["pct"] = row["pct"]
            summary_rows.append(entry)

    extractions = []
    df = analysis.extracted
    if not df.empty:
        for _, row in df.head(200).iterrows():
            extractions.append(
                {
                    "report_id": row.get("report_id", ""),
                    "finding": row.get("finding", ""),
                    "recommended_modality": row.get("recommended_modality", ""),
                    "interval_value": row.get("interval_value"),
                    "interval_unit": row.get("interval_unit", ""),
                    "urgency": row.get("urgency", ""),
                    "anatomic_region": row.get("anatomic_region", ""),
                    "confidence": row.get("confidence", "low"),
                    "review_required": bool(row.get("review_required", False)),
                }
            )

    html = HTML_TEMPLATE.render(
        stats=analysis.stats,
        summary_rows=summary_rows,
        extractions=extractions,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        version=__version__,
    )

    html_path = output_dir / f"{basename}.html"
    html_path.write_text(html, encoding="utf-8")

    pdf_path: Path | None = None
    pdf_error: str | None = None

    if include_pdf:
        try:
            pdf_path = output_dir / f"{basename}.pdf"
            from weasyprint import HTML as WeasyPrintHTML

            WeasyPrintHTML(string=html, base_url=str(output_dir)).write_pdf(
                str(pdf_path)
            )
        except Exception as exc:
            try:

                pdf_path = _fallback_pdf(summary_rows, extractions, output_dir, basename)
            except Exception as exc2:
                pdf_path = None
                pdf_error = f"WeasyPrint: {exc}; fpdf2: {exc2}"

    return ReportArtifacts(html=html_path, pdf=pdf_path, pdf_error=pdf_error)


def _fallback_pdf(
    summary_rows: list[dict],
    extractions: list[dict],
    output_dir: Path,
    basename: str,
) -> Path:
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "rad-followup-auditor Report", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 10)
    for row in summary_rows:
        text = f"{row.get('metric', '')}: {row.get('value', '')}"
        if "pct" in row and row["pct"] is not None:
            text += f" ({row['pct']}%)"
        pdf.cell(0, 7, text, new_x="LMARGIN", new_y="NEXT")

    if extractions:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 10, "Extracted Recommendations", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 8)
        for r in extractions[:100]:
            line = f"{r.get('report_id','')} | {r.get('finding','-')} | {r.get('recommended_modality','-')} | {r.get('confidence','')}"
            pdf.cell(0, 5, line, new_x="LMARGIN", new_y="NEXT")

    pdf_path = output_dir / f"{basename}.pdf"
    pdf.output(str(pdf_path))
    return pdf_path
