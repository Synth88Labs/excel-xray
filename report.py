"""
report.py — Render an AnalysisResult as an embeddable HTML body fragment.

The output is a self-contained block (a scoped <style> plus a <div class="xray">)
with NO document scaffolding (<!doctype>/<head>/<body>), NO brand header and NO
footer — so it can be pasted directly into a page or an Elementor HTML widget.
All CSS is scoped under `.xray` to avoid clashing with the host page.
"""

from __future__ import annotations

import html

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
    """Return an embeddable HTML fragment (no header/footer, no <html>/<body>)."""
    grade_c = _GRADE_COLOR.get(result.grade, "#217346")
    n_findings = len(result.findings)
    highs = sum(1 for f in result.findings if f.severity == "high")

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

    return f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
.xray{{font-family:'Poppins',-apple-system,'Segoe UI',sans-serif;color:#1f2733;line-height:1.6;max-width:960px;margin:0 auto;}}
.xray *{{box-sizing:border-box;}}
.xray .hero{{display:flex;gap:28px;align-items:center;background:#fff;border:1px solid #e3ece7;border-radius:16px;padding:26px 30px;box-shadow:0 6px 20px rgba(15,46,30,.06);flex-wrap:wrap;}}
.xray .ring{{position:relative;width:130px;height:130px;flex:0 0 auto;}}
.xray .ring svg{{transform:rotate(-90deg);}}
.xray .ring .score{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;}}
.xray .ring .score b{{font-size:2.2rem;line-height:1;}} .xray .ring .score small{{color:#8a97a3;font-size:.75rem;}}
.xray .meta h2{{margin:0 0 4px;font-size:1.3rem;}}
.xray .grade{{display:inline-flex;align-items:center;justify-content:center;width:40px;height:40px;border-radius:10px;color:#fff;font-weight:700;font-size:1.3rem;margin-right:10px;vertical-align:middle;}}
.xray .cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:22px 0;}}
.xray .card{{background:#fff;border:1px solid #e3ece7;border-radius:12px;padding:16px;text-align:center;}}
.xray .card .num{{font-size:1.8rem;font-weight:700;color:#16281f;}} .xray .card .lbl{{color:#5b6673;font-size:.85rem;}}
.xray .chips{{display:flex;flex-wrap:wrap;gap:8px;margin:6px 0;}}
.xray .chip{{background:#fff;border:1px solid #e3ece7;border-radius:20px;padding:6px 14px;font-size:.9rem;}}
.xray .chip b{{color:#9C0006;}} .xray .chip.ok{{color:#217346;}}
.xray h3{{margin:26px 0 10px;font-size:1.15rem;}}
.xray table{{width:100%;border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden;font-size:.93rem;box-shadow:0 4px 14px rgba(15,46,30,.05);}}
.xray th,.xray td{{padding:11px 13px;text-align:left;border-bottom:1px solid #eef2f0;vertical-align:top;}}
.xray th{{background:#eef6f1;font-weight:600;}}
.xray .mono{{font-family:'Consolas','Courier New',monospace;font-size:.86rem;}}
.xray .badge{{padding:2px 10px;border-radius:20px;font-size:.78rem;font-weight:600;white-space:nowrap;}}
.xray .cat{{font-weight:600;}}
.xray .detail{{font-family:'Consolas',monospace;font-size:.8rem;color:#5b6673;margin-top:4px;word-break:break-all;}}
.xray .clean{{background:#e8f3ec;border:1px solid #bfe3ce;color:#217346;border-radius:12px;padding:20px;font-weight:600;}}
@media(max-width:620px){{.xray .cards{{grid-template-columns:repeat(2,1fr);}}}}
</style>
<div class="xray">
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
</div>"""
