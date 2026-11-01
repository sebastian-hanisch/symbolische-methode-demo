"""PDF-Export der aktuellen Spezifikation mit Gleichung, Wachstum und den ersten Zahlen (fpdf2). Kernschriften sind latin-1: Umlaute gehen, Sonderzeichen werden ersetzt."""

from __future__ import annotations

from fpdf import FPDF

from sym_evaluation import Analysis, big_text, de, equation_lines

_REPLACE = {"→": "->", "–": "-", "—": "-", "−": "-", "≤": "<=", "≥": ">=", "·": "*", "€": "EUR", "„": '"', "“": '"', "λ": "lambda", "ρ": "rho", "τ": "tau", "Δ": "Delta",
            "√": "sqrt", "∅": "0", "α": "alpha"}
MAX_ROWS = 40


def _s(text) -> str:
    out = str(text)
    for old, new in _REPLACE.items():
        out = out.replace(old, new)
    for sup, digit in zip("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789"):
        out = out.replace(sup, "^" + digit)
    return out.encode("latin-1", "replace").decode("latin-1")


def build_pdf(a: Analysis) -> bytes:
    g = a.growth
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, _s("Zahlen aus der Gleichung einer Struktur"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, _s("Alles simuliert."), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    for line in equation_lines(a.spec):
        pdf.multi_cell(0, 5, _s(line), new_x="LMARGIN", new_y="NEXT")
    rho = "kein Wachstumsfaktor" if g.rho is None else f"Wachstumsfaktor 1/rho = {de(1 / g.rho, 6)}"
    pdf.multi_cell(0, 5, _s(f"Art: {g.kind}; {rho}; Periode {g.period}."), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 9)
    for h, w in (("n", 22), ("a(n)", 100)):
        pdf.cell(w, 6, _s(h), border=1)
    pdf.ln()
    pdf.set_font("Helvetica", "", 9)
    for n in range(min(len(a.seq), MAX_ROWS)):
        for v, w in ((str(n), 22), (big_text(a.seq[n]), 100)):
            pdf.cell(w, 5.5, _s(v), border=1)
        pdf.ln()
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4, _s(f"Größe n bis {a.settings.n}. Quelle: symbolische-methode-demo, Sebastian Hanisch."), new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())
