"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import math

import plotly.graph_objects as go

import sym_algorithm as A
import sym_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=50, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def _log10(x: int) -> float:
    """log10 einer positiven ganzen Zahl beliebiger Größe (float(x) liefe ab 1e308 über), ohne Stringumwandlung."""
    d = A.digit_count(x)
    lead = x if d <= 15 else x // 10 ** (d - 15)
    return d - A.digit_count(lead) + math.log10(lead)


def build_series(seq: list, rho: float | None):
    """log₁₀ a(n) über n (Länge 0 und Nullen ausgelassen) mit der Bezugslinie n·log₁₀(1/ρ) für den Wachstumsfaktor 1/ρ; der Abstand der Linien ist der Faktor c·n^(−α)."""
    ns = [n for n in range(1, len(seq)) if seq[n] > 0]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ns, y=[_log10(seq[n]) for n in ns], mode="lines+markers", name="a(n)", line=dict(color=C.COLOR_SERIES, width=2.5), marker=dict(size=5)))
    if rho is not None and ns:
        fig.add_trace(go.Scatter(x=[ns[0], ns[-1]], y=[ns[0] * -math.log10(rho), ns[-1] * -math.log10(rho)], mode="lines", name="Wachstumsfaktor 1/ρ hoch n",
                                 line=dict(color=C.COLOR_REF, width=1.5, dash="dash")))
    fig.update_xaxes(title_text="Größe n")
    fig.update_yaxes(title_text="Zahl der Strukturen (Zehnerpotenz, log₁₀)")
    return _base(fig)


def build_error(errors: list, tol: float = C.GROWTH_TOL):
    """Fehler |ρ^p·a(n + p)/a(n) − 1| über n (logarithmische Achse; Fehler 0 wird als 1e-17 gezeichnet)."""
    pts = [(n, max(e, 1e-17)) for n, e in errors if e is not None]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[n for n, _ in pts], y=[e for _, e in pts], mode="lines+markers", name="Fehler des Quotienten", line=dict(color=C.COLOR_LINE, width=2.5), marker=dict(size=5)))
    fig.add_hline(y=tol, line=dict(color=C.COLOR_ERROR, width=1.2, dash="dash"), annotation_text=f"{100 * tol:.0f} %", annotation_position="top right")
    fig.update_xaxes(title_text="n")
    fig.update_yaxes(title_text="relativer Fehler (logarithmisch)", type="log")
    return _base(fig)


def build_classes(res: dict):
    """Zahl der Zufallsspezifikationen je Art (Polynom, linear, nichtlinear) und wie viele davon das Raten mit konstanten Koeffizienten löst."""
    kinds = ["polynom", "linear", "nichtlinear"]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=kinds, y=[res["kinds"][k] for k in kinds], name="Spezifikationen", marker_color=C.COLOR_SERIES))
    fig.add_trace(go.Bar(x=kinds, y=[res["guess_found"][k] for k in kinds], name="davon: Raten findet eine Rekursion", marker_color=C.COLOR_LINE))
    fig.update_layout(barmode="group")
    fig.update_yaxes(title_text="Spezifikationen")
    return _base(fig, 320)
