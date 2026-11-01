"""Jede Zahl aus der README und aus den Texten der App, nachgerechnet (DEMO-PLAYBOOK §4). Die Zufallsspezifikationen sind `random_spec(seed)` mit festen Seeds. Es gibt keine Zeitmessung."""

import math
import random

import sym_algorithm as A
import sym_constants as C
import sym_evaluation as ev
from sym_scenario import parse_spec, random_spec


def test_readme_hand_values_of_the_presets():
    spec = {name: parse_spec(p["spec"])[0] for name, p in C.PRESETS.items()}
    assert A.series_online(spec["Binärbäume (Catalan)"], 10) == [1, 1, 2, 5, 14, 42, 132, 429, 1430, 4862, 16796]
    assert A.series_online(spec["Motzkin-Pfade"], 7) == [1, 1, 2, 4, 9, 21, 51, 127]
    assert A.series_online(spec["Schröder (groß)"], 5) == [1, 2, 6, 22, 90, 394]
    assert A.series_online(spec["Ternäre Bäume"], 5) == [1, 1, 3, 12, 55, 273]
    assert A.series_online(spec["Fibonacci-Wörter"], 6) == [1, 1, 2, 3, 5, 8, 13]
    assert A.series_online(spec["Kompositionen mit Teilen 1 bis 3"], 7) == [1, 1, 2, 4, 7, 13, 24, 44]
    assert A.series_online(spec["Nur gerade Größen"], 8) == [1, 0, 1, 0, 2, 0, 5, 0, 14]


def test_readme_known_radii_and_fixed_points():
    expected = {"Binärbäume (Catalan)": (0.25, 2.0), "Motzkin-Pfade": (1 / 3, 3.0), "Schröder (groß)": (3 - 2 * math.sqrt(2), 1 + math.sqrt(2)), "Ternäre Bäume": (4 / 27, 1.5)}
    for name, (rho, tau) in expected.items():
        g = A.growth(parse_spec(C.PRESETS[name]["spec"])[0])
        assert abs(g.rho - rho) < 1e-12 and abs(g.tau - tau) < 1e-9, name
    assert abs(A.growth(parse_spec("3 z F")[0]).rho - 1 / 3) < 1e-12 and abs(A.growth(parse_spec("z F + z^2 F")[0]).rho - (math.sqrt(5) - 1) / 2) < 1e-12


def test_readme_fixpoint_rounds_and_discriminants():
    assert A.series_fixpoint({(1, 2): 1}, 10)[1] == 11 and A.series_fixpoint({(2, 2): 1}, 10)[1] == 6
    assert A.discriminant({(1, 2): 1}) == [1, -4] and A.discriminant({(1, 1): 1, (2, 2): 1}) == [1, -2, -3] and A.discriminant({(1, 1): 1, (1, 2): 1}) == [1, -6, 1]


def test_readme_the_quotient_converges_like_one_over_n_for_nested_specs_and_exponentially_for_linear_ones():
    binary = {(1, 2): 1}
    a = A.series_online(binary, 410)
    assert abs(A.quotient_error(a, 0.25, 1, 10) - 0.125) < 1e-12                       # C(11)/C(10) = 3,5 gegen 4
    assert 0.0140 < A.quotient_error(a, 0.25, 1, 100) < 0.0150
    assert 1.49 < A.exponent_alpha(a, 0.25, 1, 400) < 1.50
    fib = A.series_online({(1, 1): 1, (2, 1): 1}, 410)
    rho = (math.sqrt(5) - 1) / 2
    assert 3e-5 < A.quotient_error(fib, rho, 1, 10) < 4e-5 and A.quotient_error(fib, rho, 1, 100) < 1e-12


def test_readme_alpha_of_the_four_nested_presets_at_n_1000():
    for name in ("Binärbäume (Catalan)", "Motzkin-Pfade", "Schröder (groß)", "Ternäre Bäume"):
        spec = parse_spec(C.PRESETS[name]["spec"])[0]
        a = A.series_online(spec, 1001)
        assert 1.49 < A.exponent_alpha(a, A.growth(spec).rho, 1, 1000) < 1.50, name


def test_readme_guessing_on_the_presets():
    orders = {name: A.smallest_recurrence(A.series_online(parse_spec(p["spec"])[0], 79), 12)[0] for name, p in C.PRESETS.items()}
    assert orders == {"Binärbäume (Catalan)": None, "Motzkin-Pfade": None, "Schröder (groß)": None, "Ternäre Bäume": None, "Fibonacci-Wörter": 2, "Wörter über 3 Buchstaben": 1,
                      "Kompositionen mit Teilen 1 bis 3": 3, "Nur gerade Größen": None}
    assert ev.catalan_identity() is True and C.CATALAN_IDENTITY_N == 200


def test_readme_ambiguity_table():
    rows = ev.ambiguity_rows()
    assert [r["Gleichung"] for r in rows] == [1, 1, 2, 5, 14, 42, 132, 429] and {r["verschiedene Wörter"] for r in rows} == {1}


def test_readme_words_without_aa_are_compositions_of_n_plus_one():
    """Brücke zu Stück 2: Wörter aus A, B ohne AA haben 1, 2, 3, 5, 8, … (Stück 2, Fibonacci), Kompositionen in 1 und 2 haben 1, 1, 2, 3, 5, …: um eine Stelle verschoben."""
    comp = A.series_online({(1, 1): 1, (2, 1): 1}, 11)
    assert [comp[n + 1] for n in range(11)] == [1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]


def test_readme_experiment_5_over_300_random_specs():
    res = ev.class_experiment()
    assert res["count"] == 300 == C.CLASS_SETS and C.CLASS_SEED_BASE == 5000
    assert res["kinds"] == {"polynom": 40, "linear": 41, "nichtlinear": 219}
    assert res["guess_found"] == {"polynom": 40, "linear": 41, "nichtlinear": 0}
    assert res["enum_bad"] == 0 and res["enum_checked"] == 2048
    q = res["quotient"]
    assert q["aperiodisch"][:2] == [154, 154] and q["aperiodisch"][2] < 0.0075
    assert q["periodisch"][:2] == [65, 65] and q["periodisch"][2] < 0.015
    assert q["periodisch ohne Schritt p"][:2] == [65, 0] and q["periodisch ohne Schritt p"][2] == 1.0


def test_readme_phase_zero_quotient_at_n_400_over_seeds_from_7000():
    """Phase 0: 202 nichtlineare Zufallsspezifikationen (Seeds ab 7000): aperiodisch 157, periodisch 45; Exponent α bei n = 400 zwischen 1,489 und 1,494."""
    counts = {"aperiodisch": 0, "periodisch": 0}
    alphas = []
    for seed in range(7000, 7300):
        spec = random_spec(seed)
        if A.kind_of(spec) != "nichtlinear":
            continue
        g = A.growth(spec)
        a = A.series_online(spec, 410)
        if a[400] == 0 or g.rho is None:
            continue
        key = "aperiodisch" if g.period == 1 else "periodisch"
        assert A.quotient_error(a, g.rho, g.period, 400) < 0.02, spec
        counts[key] += 1
        if g.period == 1:
            alphas.append(A.exponent_alpha(a, g.rho, 1, 400))
    assert counts == {"aperiodisch": 157, "periodisch": 45}
    assert min(alphas) > 1.488 and max(alphas) < 1.495


def test_readme_all_phase_zero_random_specs_agree_with_enumeration():
    rng = random.Random(20261101)
    checked = bad = 0
    for _ in range(300):
        spec = {}
        for _t in range(rng.randint(1, 3)):
            spec[(rng.randint(1, 2), rng.randint(0, 3))] = rng.randint(1, 2)
        a = A.series_online(spec, 7)
        top = 7
        while top > 2 and a[top] > 30000:
            top -= 1
        memo: dict = {}
        checked += 1
        bad += [len(A.enumerate_structures(spec, n, memo)) for n in range(top + 1)] != a[: top + 1]
    assert (checked, bad) == (300, 0)


def test_app_text_limits_come_from_the_constants():
    assert (C.MAX_TERMS, C.MAX_J, C.MAX_K, C.MAX_COEF, C.N_MAX) == (6, 12, 4, 9, 100)
    assert (C.GUESS_RMAX, C.GUESS_TERMS, C.GROWTH_N, C.ERROR_N, C.GROWTH_TOL, C.CLASS_QUOTIENT_N, C.ENUM_COUNT_CAP, C.ENUM_SHOW_N, C.ENUM_SHOW_COUNT) == (12, 80, 400, 60, 0.02, 200, 30000, 5, 24)
