# Excel X-Ray 🩻

[![CI](https://github.com/Synth88Labs/excel-xray/actions/workflows/ci.yml/badge.svg)](https://github.com/Synth88Labs/excel-xray/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Understand and de-risk any Excel workbook in seconds.** Point X-Ray at a `.xlsx`
and it produces a beautiful HTML report that finds the hidden problems spreadsheets
are famous for — with a **Health Score** and a ranked list of issues.

> Studies have found the vast majority of business spreadsheets contain errors, and
> spreadsheet mistakes have caused real, headline-making losses. Most of those bugs
> are invisible until it's too late. X-Ray shines a light on them.

Think of it as **a spell-checker — or an X-ray — for your spreadsheets.**

> 🌐 **Prefer no install?** Use the **free in-browser version** — drop a workbook and get
> an instant report, with nothing uploaded (it runs entirely on your device):
> [Audit Any Spreadsheet for Hidden Errors](https://excelguru.io/tutorials/audit-any-spreadsheet-for-hidden-errors/) on ExcelGuru.io.

## What it detects

| Check | Why it matters |
|---|---|
| 🔴 **Formula errors** (`#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`, …) | Broken results hiding in cells |
| 🟠 **Inconsistent formulas** | A cell that **breaks its column's pattern** — the #1 source of silent bugs |
| 🟠 **Broken references** (`#REF!` in a formula) | Points at a range that no longer exists |
| 🟡 **External links** | Formulas linking to other files that break when they move |
| 🟡 **Volatile functions** (`INDIRECT`, `OFFSET`, `NOW`, `RAND`…) | Instability and slow, unpredictable recalcs |
| 🔵 **Hidden / very-hidden sheets** | Where forgotten (and risky) logic likes to live |

Everything rolls up into a **Health Score (0–100)** and a letter grade.

## The star feature: inconsistent-formula detection

X-Ray normalizes each formula to a relative pattern (an R1C1-style fingerprint) and
flags any cell that **doesn't match the pattern of the column around it**. That's how
it catches the classic disaster — one cell in a "total" column that quietly does
something different from all its neighbours.

## Installation

```bash
git clone https://github.com/Synth88Labs/excel-xray.git
cd excel-xray
pip install -r requirements.txt
```

Requires Python 3.9+.

## Usage

```bash
python xray.py <workbook.xlsx> [-o report.html]
```

### Example

```bash
python xray.py budget.xlsx -o budget_xray.html
```

Console output:

```
Excel X-Ray — budget.xlsx
  Health Score: 76/100  (Grade B — Low-moderate risk)
  Sheets: 2   Formula cells: 11   Findings: 6
    - Volatile function: 2
    - Broken reference: 1
    - External link: 1
    - Inconsistent formula: 1
    - Hidden sheet: 1

Report saved: .../budget_xray.html
```

…plus a self-contained **HTML report** (opens offline, easy to share) with the Health
Score ring, overview cards, and a severity-ranked findings table.

## How it works (and its limits)

- Reads formulas **and** cached values via `openpyxl` — no Excel install needed, and
  your file never leaves your machine.
- Inconsistency detection is **heuristic**: it compares formulas within contiguous
  runs in each column. It's excellent at catching the common "one odd cell" bug, but
  it won't understand every intentional exception — treat findings as leads to review.
- Cached-error detection depends on the values Excel last saved in the file.

## Roadmap

- Row-pattern (horizontal) inconsistency detection
- Dependency / precedent maps between sheets
- A **drag-and-drop web version** on [ExcelGuru.io](https://excelguru.io/) — audit a
  workbook in your browser, nothing uploaded

## Running the tests

```bash
pip install pytest
python -m pytest
```

## 📚 Learn More — Free Excel Tutorials

Level up your Excel and automation skills with free, practical guides at
**[ExcelGuru.io](https://excelguru.io/category/tutorials/)**.

## License

MIT — see [LICENSE](LICENSE).
