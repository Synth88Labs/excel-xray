"""
report.py — Render an AnalysisResult as a self-contained, branded HTML report.

The output is a single .html file (all CSS inline) that opens offline and is
easy to share. Colors follow the ExcelGuru palette.
"""

from __future__ import annotations

import html
from datetime import datetime

from analyze import AnalysisResult, Finding

_SEV = {
    "high": ("#9C0006", "#FFC7CE", "High"),
    "medium": ("#8a5b00", "#FFF0C2", "Medium"),
    "low": ("#1d4ed8", "#dbeafe", "Low"),
    "info": ("#475569", "#e2e8f0", "Info"),
}
_GRADE_COLOR = {"A": "#217346", "B": "#33C481", "C": "#d19a00", "D": "#e06b1f", "F": "#c0392b"}


def _esc(s: object) -> str:
    return html.escape(str(s))


def _finding_rows(findings: list[Finding]) -> str:
    rows = []
    for f in findings:
        color, bg, label = _SEV.get(f.severity, _SEV["info"])
        detail = f'<div class="detail">{_esc(f.detail)}</div>' if f.detail else ""
        rows.append(
            f'<tr>'
            f'<td><span class="badge" style="color:{color};background:{bg}">{label}</span></td>'
            f'<td class="cat">{_esc(f.category)}</td>'
            f'<td class="mono">{_esc(f.sheet)}</td>'
            f'<td class="mono">{_esc(f.cell)}</td>'
            f'<td>{_esc(f.message)}{detail}</td>'
            f'</tr>'
        )
    return "\n".join(rows)


def render_html(result: AnalysisResult, generated: str | None = None) -> str:
    when = generated or datetime.now().strftime("%B %d, %Y %H:%M")
    grade_c = _GRADE_COLOR.get(result.grade, "#217346")
    n_findings = len(result.findings)
    highs = sum(1 for f in result.findings if f.severity == "high")
    filename = result.path.replace("\\", "/").split("/")[-1]

    # ring geometry (health out of 100)
    circ = 2 * 3.14159 * 54
    dash = circ * result.health / 100

    cards = [
        ("Sheets", result.n_sheets),
        ("Formula cells", result.n_formulas),
        ("Findings", n_findings),
        ("High severity", highs),
    ]
    card_html = "".join(
        f'<div class="card"><div class="num">{v}</div><div class="lbl">{_esc(k)}</div></div>'
        for k, v in cards
    )

    cat_html = "".join(
        f'<div class="chip">{_esc(cat)} <b>{n}</b></div>'
        for cat, n in sorted(result.counts.items(), key=lambda kv: -kv[1])
    ) or '<div class="chip ok">No issues detected 🎉</div>'

    sheet_rows = "".join(
        f'<tr><td class="mono">{_esc(s.name)}</td><td>{_esc(s.state)}</td>'
        f'<td>{s.rows}</td><td>{s.cols}</td><td>{s.formulas}</td></tr>'
        for s in result.sheets
    )

    findings_table = (
        f'<table class="findings"><thead><tr>'
        f'<th>Severity</th><th>Issue</th><th>Sheet</th><th>Cell</th><th>What it means</th>'
        f'</tr></thead><tbody>{_finding_rows(result.findings)}</tbody></table>'
        if result.findings else
        '<div class="clean">✅ No issues detected. This workbook looks healthy.</div>'
    )

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Excel X-Ray Report — {_esc(filename)}</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
*{{box-sizing:border-box}}
body{{font-family:'Poppins',-apple-system,'Segoe UI',sans-serif;margin:0;background:#f4faf6;color:#1f2733;}}
.wrap{{max-width:960px;margin:0 auto;padding:32px 20px 60px;}}
.brand{{display:flex;align-items:center;gap:12px;margin-bottom:8px;}}
.logo{{width:44px;height:44px;border-radius:11px;background:linear-gradient(135deg,#33C481,#217346);display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:20px;}}
.brand .name{{font-weight:700;font-size:20px;}} .brand .name span{{color:#217346;}}
h1{{font-size:1.9rem;margin:14px 0 2px;}}
.sub{{color:#5b6673;font-size:.95rem;margin-bottom:24px;}}
.hero{{display:flex;gap:28px;align-items:center;background:#fff;border:1px solid #e3ece7;border-radius:16px;padding:26px 30px;box-shadow:0 6px 20px rgba(15,46,30,.06);flex-wrap:wrap;}}
.ring{{position:relative;width:130px;height:130px;flex:0 0 auto;}}
.ring svg{{transform:rotate(-90deg);}}
.ring .score{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;}}
.ring .score b{{font-size:2.2rem;line-height:1;}} .ring .score small{{color:#8a97a3;font-size:.75rem;}}
.hero .meta h2{{margin:0 0 4px;font-size:1.3rem;}}
.grade{{display:inline-flex;align-items:center;justify-content:center;width:40px;height:40px;border-radius:10px;color:#fff;font-weight:700;font-size:1.3rem;margin-right:10px;vertical-align:middle;}}
.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:22px 0;}}
.card{{background:#fff;border:1px solid #e3ece7;border-radius:12px;padding:16px;text-align:center;}}
.card .num{{font-size:1.8rem;font-weight:700;color:#16281f;}} .card .lbl{{color:#5b6673;font-size:.85rem;}}
.chips{{display:flex;flex-wrap:wrap;gap:8px;margin:6px 0 26px;}}
.chip{{background:#fff;border:1px solid #e3ece7;border-radius:20px;padding:6px 14px;font-size:.9rem;}}
.chip b{{color:#9C0006;}} .chip.ok{{color:#217346;}}
h3{{margin:26px 0 10px;font-size:1.15rem;}}
table{{width:100%;border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden;font-size:.93rem;box-shadow:0 4px 14px rgba(15,46,30,.05);}}
th,td{{padding:11px 13px;text-align:left;border-bottom:1px solid #eef2f0;vertical-align:top;}}
th{{background:#eef6f1;font-weight:600;}}
.mono{{font-family:'Consolas','Courier New',monospace;font-size:.86rem;}}
.badge{{padding:2px 10px;border-radius:20px;font-size:.78rem;font-weight:600;white-space:nowrap;}}
.cat{{font-weight:600;}}
.detail{{font-family:'Consolas',monospace;font-size:.8rem;color:#5b6673;margin-top:4px;word-break:break-all;}}
.clean{{background:#e8f3ec;border:1px solid #bfe3ce;color:#217346;border-radius:12px;padding:20px;font-weight:600;}}
.footer{{margin-top:36px;color:#5b6673;font-size:.85rem;text-align:center;}}
.footer a{{color:#217346;text-decoration:none;font-weight:600;}}
@media(max-width:620px){{.cards{{grid-template-columns:repeat(2,1fr)}}}}
</style></head>
<body><div class="wrap">
  <div class="brand"><div class="logo">✓</div><div class="name">ExcelGuru<span>.io</span></div></div>
  <h1>🩻 Excel X-Ray Report</h1>
  <div class="sub">{_esc(filename)} · generated {_esc(when)}</div>

  <div class="hero">
    <div class="ring">
      <svg width="130" height="130">
        <circle cx="65" cy="65" r="54" fill="none" stroke="#e6efe9" stroke-width="14"/>
        <circle cx="65" cy="65" r="54" fill="none" stroke="{grade_c}" stroke-width="14"
                stroke-linecap="round" stroke-dasharray="{dash:.1f} {circ:.1f}"/>
      </svg>
      <div class="score"><b>{result.health}</b><small>HEALTH / 100</small></div>
    </div>
    <div class="meta">
      <h2><span class="grade" style="background:{grade_c}">{result.grade}</span>{_esc(result.risk_label)}</h2>
      <div class="chips">{cat_html}</div>
    </div>
  </div>

  <div class="cards">{card_html}</div>

  <h3>Findings</h3>
  {findings_table}

  <h3>Sheet breakdown</h3>
  <table><thead><tr><th>Sheet</th><th>State</th><th>Rows</th><th>Cols</th><th>Formulas</th></tr></thead>
  <tbody>{sheet_rows}</tbody></table>

  <div class="footer">
    Generated by <b>Excel X-Ray</b> · a free, open-source tool by
    <a href="https://excelguru.io/">ExcelGuru.io</a> ·
    <a href="https://github.com/Synth88Labs/excel-xray">source on GitHub</a>
  </div>
</div></body></html>"""
