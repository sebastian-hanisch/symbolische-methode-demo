"""Verdikte und Formatierung an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier."""

import sym_algorithm as A
import sym_constants as C
import sym_evaluation as ev


def _analysis(spec: str, n: int = 10):
    return ev.analyse(ev.Settings(spec, n))


def test_big_text_and_de():
    assert ev.big_text(0) == "0" and ev.big_text(1234567) == "1.234.567" and ev.big_text(999_999_999_999) == "999.999.999.999"
    assert ev.big_text(10 ** 12) == "1,00·10¹² (13 Stellen)" and ev.big_text(10 ** 5000) == "1,00·10⁵⁰⁰⁰ (5001 Stellen)"
    assert ev.de(4.0, 4) == "4,0000" and ev.de(0.3712, 2) == "0,37"


def test_poly_text():
    assert ev.poly_text([1, -2, -1, -1]) == "1 − 2z − z² − z³" and ev.poly_text([]) == "0" and ev.poly_text([0, 1]) == "z" and ev.poly_text([0, -1]) == "−z"
    assert ev.poly_text([1, 0, -4]) == "1 − 4z²" and ev.poly_text([A.Fraction(1), A.Fraction(1, 2)]) == "1 + (1/2)z"


def test_equation_lines_for_the_three_kinds():
    assert ev.equation_lines({(1, 2): 1}) == [
        "Gleichung: F = 1 + z F²",
        "Normalform: (z)·F² + (−1)·F + (1) = 0",
        "Lösung: F(z) = (1 − B(z) − √Δ(z)) / (2·A(z)) mit A(z) = z, B(z) = 0, Δ(z) = 1 − 4z",
    ]
    lines = ev.equation_lines({(1, 1): 1, (2, 1): 1})
    assert lines == ["Gleichung: F = 1 + z F + z² F", "Lösung: F(z) = P(z)/Q(z) mit P(z) = 1 und Q(z) = 1 − z − z² (gekürzt)"]
    assert ev.equation_lines({(1, 3): 1})[1] == "Normalform: Polynomgleichung vom Grad 3 in F; eine Wurzelformel gibt die App nicht an"
    assert ev.equation_lines({}) == ["Gleichung: F = 1", "Lösung: F(z) = P(z)/Q(z) mit P(z) = 1 und Q(z) = 1 (gekürzt)"]


def test_summary_verdict_for_every_kind():
    kind, text = ev.verdict_summary(_analysis("z F^2"))
    assert kind == "success" and text == ("Die Gleichung ist **nichtlinear** (Verschachtelung): F ist **kein** Bruch aus Polynomen, eine Rekursion mit konstanten Koeffizienten gibt es nicht. "
                                          "Die Zahl der Strukturen wächst um den Faktor 4,0000 je Atom.")
    kind, text = ev.verdict_summary(_analysis("z F + z^2 F"))
    assert kind == "success" and text == "Die Gleichung ist **linear**: F ist ein Bruch aus Polynomen (wie in Stück 2). Die Zahl der Strukturen wächst um den Faktor 1,6180 je Atom."
    assert ev.verdict_summary(_analysis("z^2 F^2"))[1].endswith("Faktor 2,0000 je Atom. Alle Größen sind Vielfache von 2.")
    assert ev.verdict_summary(_analysis("z^2")) == ("info", "Die Gleichung hat keine Teilstrukturen: F ist ein Polynom, es gibt Strukturen nur bis zur Größe 2. Alle Größen sind Vielfache von 2.")
    assert ev.verdict_summary(_analysis("z + z^2")) == ("info", "Die Gleichung hat keine Teilstrukturen: F ist ein Polynom, es gibt Strukturen nur bis zur Größe 2.")


def test_equation_rows_and_verdict():
    a = _analysis("z F^2")
    rows = ev.equation_rows(a.spec, a.seq)
    assert [r["Gleichung"] for r in rows[:6]] == [1, 1, 2, 5, 14, 42] and rows[5]["Festpunkt"] == 42 and rows[5]["Aufzählen"] == 42
    assert ev.verdict_equation(rows) == ("success", "Gleichung, Festpunktiteration (11 Runden bis n = 10) und Aufzählen der Strukturen geben bis n = 10 dieselben Zahlen.")
    bad = [dict(r) for r in rows]
    bad[2]["Aufzählen"] = 3
    kind, text = ev.verdict_equation(bad)
    assert kind == "error" and "n = 2" in text
    none = [dict(r, Aufzählen=None) for r in rows]
    assert ev.verdict_equation(none)[1].endswith("Aufzählen wurde nicht gerechnet (zu viele Strukturen).")


def test_guess_verdicts_and_experiment():
    nonlinear = {"kind": "nichtlinear", "order": None, "coeffs": None, "terms": 80, "catalan": True}
    kind, text = ev.verdict_guess(nonlinear)
    assert kind == "success" and text == ("Das Raten (konstante Koeffizienten bis Ordnung 12, 80 Glieder) findet **keine** Rekursion, wie es bei Verschachtelung sein muss. "
                                          "Für die Catalan-Zahlen (z F²) gibt es eine Rekursion mit n-abhängigen Koeffizienten: (n + 2)·C(n+1) = 2·(2n + 1)·C(n), geprüft bis n = 199: stimmt.")
    assert "stimmt nicht" in ev.verdict_guess(dict(nonlinear, catalan=False))[1]
    kind, text = ev.verdict_guess(dict(nonlinear, order=3))
    assert kind == "warning" and "Ordnung 3, obwohl die Gleichung nichtlinear ist" in text
    assert ev.verdict_guess({"kind": "linear", "order": 2, "terms": 80, "catalan": True}) == (
        "success", "Das Raten (konstante Koeffizienten bis Ordnung 12, 80 Glieder) findet bei dieser linearen Gleichung die Ordnung 2.")
    assert "polynomialen" in ev.verdict_guess({"kind": "polynom", "order": 1, "terms": 80, "catalan": True})[1]
    assert ev.verdict_guess({"kind": "linear", "order": None, "terms": 80, "catalan": True})[0] == "warning"
    res = ev.guess_experiment({(1, 1): 1, (2, 1): 1})
    assert res["order"] == 2 and res["kind"] == "linear" and res["terms"] == C.GUESS_TERMS and res["catalan"] is True
    assert ev.guess_experiment({(1, 2): 1})["order"] is None


def test_catalan_identity():
    assert ev.catalan_identity(50) is True


def test_ambiguity_rows_and_verdict():
    rows = ev.ambiguity_rows()
    assert [r["Gleichung"] for r in rows] == [1, 1, 2, 5, 14, 42, 132, 429] and all(r["aufgezählt"] == r["Gleichung"] and r["verschiedene Wörter"] == 1 for r in rows)
    assert ev.verdict_ambiguity(rows) == ("warning", "Für aⁿ zählt die Gleichung 429 Ableitungen bei n = 8, aber es gibt nur 1 Wort. "
                                                     "Eine mehrdeutige Beschreibung zählt Ableitungen, nicht Wörter: Die Beschreibung muss jede Gestalt genau einmal aufbauen.")
    bad = [dict(r) for r in rows]
    bad[3]["aufgezählt"] = 4
    assert ev.verdict_ambiguity(bad) == ("error", "Gleichung und Aufzählung weichen bei n = 4 ab.")


def test_growth_verdicts():
    g = A.Growth("nichtlinear", 0.25, 2.0, 1)
    res = {"growth": g, "errors": [], "alpha": 1.4926, "final_error": 0.0037, "n_eval": 400}
    kind, text = ev.verdict_growth(res)
    assert kind == "success" and text == ("Aus dem System τ = 1 + P(ρ, τ), 1 = P_F(ρ, τ): ρ = 0,250000 (Wachstumsfaktor 1/ρ = 4,000000, τ = F(ρ) = 2,000000). "
                                          "Bei n = 400 weicht ρ^1·a(n + 1)/a(n) um 0,37 % von 1 ab, α ≈ 1,493. "
                                          "Der Fehler fällt nur wie 1/n (α nahe 3/2): Das ist die Wurzelsingularität, die Stück 9 erklärt.")
    kind, text = ev.verdict_growth({"growth": A.Growth("linear", 0.5, None, 1), "errors": [], "alpha": 1e-13, "final_error": 4e-16, "n_eval": 400})
    assert kind == "success" and text == ("Aus 1 = B(ρ): ρ = 0,500000 (Wachstumsfaktor 1/ρ = 2,000000). Bei n = 400 weicht ρ^1·a(n + 1)/a(n) um 0,00 % von 1 ab, α ≈ 0,000. "
                                          "Der Fehler fällt exponentiell schnell (α nahe 0), wie bei Stück 2.")
    periodic = ev.verdict_growth({"growth": A.Growth("nichtlinear", 0.5, 2.0, 2), "errors": [], "alpha": 1.4, "final_error": 0.0074, "n_eval": 400})[1]
    assert " Wegen der Periode 2 wird a(n + 2)/a(n) betrachtet. " in periodic and "ρ^2·a(n + 2)/a(n)" in periodic
    assert ev.verdict_growth({"growth": A.Growth("polynom", None, None, 1)})[0] == "info"
    assert ev.verdict_growth({"growth": A.Growth("nichtlinear", None, None, 1)})[0] == "warning"


def test_growth_experiment_on_the_presets():
    res = ev.growth_experiment({(1, 2): 1})
    assert res["growth"].rho == 0.25 and res["n_eval"] == 400 and 1.45 < res["alpha"] < 1.52 and res["final_error"] < C.GROWTH_TOL
    assert res["errors"][0] == (1, 0.5) and res["errors"][-1][0] == C.ERROR_N
    res = ev.growth_experiment({(2, 2): 1})
    assert res["growth"].period == 2 and res["n_eval"] == 400 and [n for n, _ in res["errors"]][:3] == [2, 4, 6] and res["final_error"] < C.GROWTH_TOL
    res = ev.growth_experiment({(1, 0): 1})
    assert res["errors"] == [] and res["alpha"] is None and res["final_error"] is None


def test_class_verdict_and_small_experiment():
    res = {"count": 300, "kinds": {"polynom": 40, "linear": 41, "nichtlinear": 219}, "guess_found": {"polynom": 40, "linear": 41, "nichtlinear": 0}, "enum_bad": 0, "enum_checked": 2048,
           "quotient": {"aperiodisch": [154, 154, 0.0074], "periodisch": [65, 65, 0.0148], "periodisch ohne Schritt p": [65, 0, 1.0]}}
    kind, text = ev.verdict_classes(res)
    assert kind == "success" and text == (
        "Von 300 Zufallsspezifikationen sind 41 linear, 219 nichtlinear und 40 Polynome. Das Raten findet bei 41 der linearen und bei 0 der nichtlinearen eine konstante Rekursion. "
        "Gleichung und Aufzählen weichen in 0 von 2048 Größen ab. Der Quotient ρ^p·a(n + p)/a(n) liegt bei n = 200 bei 154 von 154 aperiodischen und 65 von 65 periodischen "
        "auf 2 % genau (periodisch ohne Schritt p: 0 von 65).")
    assert ev.verdict_classes(dict(res, enum_bad=1))[0] == "warning"
    assert ev.verdict_classes(dict(res, guess_found={"polynom": 40, "linear": 41, "nichtlinear": 2}))[0] == "warning"
    small = ev.class_experiment(count=20, seed_base=5000)
    assert sum(small["kinds"].values()) == 20 and all(small["guess_found"][k] <= small["kinds"][k] for k in small["kinds"]) and small["enum_bad"] == 0


def test_build_up_rows_and_verdict():
    a = _analysis("3 z F + z^2 F^2", 4)
    rows = ev.build_up_rows(a, 2)
    assert rows == [{"Term": "3 z F", "Koeffizient": 3, "Beitrag": 9}, {"Term": "z² F²", "Koeffizient": 1, "Beitrag": 1}] and a.seq[2] == 10
    assert ev.verdict_build_up(rows, 2, 10) == ("success", "a(2) = 10: die Beiträge der Terme ergeben genau diese Zahl.")
    assert ev.verdict_build_up(rows, 2, 11)[0] == "error"
    assert [r["Term"] for r in ev.build_up_rows(_analysis("z F^2 + z^3"), 3)] == ["z F²", "z³"]


def test_period_note():
    assert ev.period_note({(1, 2): 1}) == "" and ev.period_note({(2, 2): 1}) == "Periode 2: Es gibt nur Größen, die Vielfache von 2 sind."


def test_checker_flags_wrong_numbers(monkeypatch):
    spec = {(1, 2): 1}
    good = A.series_online(spec, 8)
    assert ev.check_series(spec, good, None) == []
    wrong = list(good)
    wrong[5] += 1
    assert any("Festpunktiteration" in m for m in ev.check_series(spec, wrong, None))
    # Nur das Aufzählen soll anschlagen: die Festpunktiteration liefert hier absichtlich dieselbe falsche Folge
    monkeypatch.setattr(A, "series_fixpoint", lambda sp, m: (wrong[: m + 1], 1))
    messages = ev.check_series(spec, wrong, None)
    assert messages == ["Beim Aufzählen der Strukturen der Größe 5 kommt eine andere Zahl heraus"]
    monkeypatch.undo()
    lin = {(1, 1): 1, (2, 1): 1}
    seq = A.series_online(lin, 10)
    assert ev.check_series(lin, seq, A.rational_form(lin)) == []
    assert any("Bruch" in m for m in ev.check_series(lin, seq, ([A.Fraction(1)], [A.Fraction(1), A.Fraction(-1)])))
