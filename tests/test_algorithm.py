"""Kern gegen Handrechnung (DEMO-PLAYBOOK §1b): Mini-Instanzen aus conftest.py, jeder Erwartungswert als Rechnung."""

import math
from fractions import Fraction

import pytest

import sym_algorithm as A
from sym_scenario import parse_spec, period_of, spec_input_text, spec_text


def test_hand_series(binary, motzkin, fibonacci):
    assert A.series_online(binary, 4) == [1, 1, 2, 5, 14]
    assert A.series_online(motzkin, 3)[3] == 4 and A.series_online(motzkin, 6) == [1, 1, 2, 4, 9, 21, 51]
    assert A.series_online(fibonacci, 6) == [1, 1, 2, 3, 5, 8, 13]


def test_other_presets_by_hand():
    assert A.series_online({(1, 3): 1}, 4) == [1, 1, 3, 12, 55]                    # ternär: a(2) = [z¹]F³ = 3·a(1) = 3
    assert A.series_online({(1, 1): 1, (1, 2): 1}, 4) == [1, 2, 6, 22, 90]          # große Schröder-Zahlen
    assert A.series_online({(1, 1): 3}, 4) == [1, 3, 9, 27, 81]
    assert A.series_online({(2, 2): 1}, 6) == [1, 0, 1, 0, 2, 0, 5]                 # nur gerade Größen: Catalan auf den geraden Stellen


def test_polynomial_and_empty_specifications():
    assert A.series_online({(2, 0): 3}, 4) == [1, 0, 3, 0, 0]                       # F = 1 + 3z²
    assert A.series_online({}, 3) == [1, 0, 0, 0]                                   # F = 1
    assert A.series_online({(1, 0): 1, (3, 0): 2}, 4) == [1, 1, 0, 2, 0]


def test_fixpoint_iteration_agrees_and_needs_n_plus_one_rounds(binary):
    a, rounds = A.series_fixpoint(binary, 10)
    assert a == A.series_online(binary, 10) and rounds == 11
    assert A.series_fixpoint({}, 5) == ([1, 0, 0, 0, 0, 0], 1)


def test_contributions_by_hand(binary, motzkin):
    rows = A.contributions(binary, A.series_online(binary, 3), 3)
    assert rows == [{"j": 1, "k": 2, "c": 1, "coefficient": 5, "contribution": 5}]    # [z²]F² = 5
    rows = A.contributions(motzkin, A.series_online(motzkin, 3), 3)
    assert [(r["j"], r["k"], r["coefficient"]) for r in rows] == [(1, 1, 2), (2, 2, 2)] and sum(r["contribution"] for r in rows) == 4
    with pytest.raises(ValueError):
        A.contributions(binary, [1, 1], 2)


def test_the_five_binary_trees_of_size_three_by_hand(binary):
    texts = {A.structure_text(s, binary) for s in A.enumerate_structures(binary, 3)}
    assert texts == {"z[z[z[∅, ∅], ∅], ∅]", "z[z[∅, z[∅, ∅]], ∅]", "z[z[∅, ∅], z[∅, ∅]]", "z[∅, z[z[∅, ∅], ∅]]", "z[∅, z[∅, z[∅, ∅]]]"}
    assert A.enumerate_structures(binary, 0) == [()] and A.structure_size(A.enumerate_structures(binary, 3)[0]) == 3


def test_colors_and_larger_atoms_in_structure_text():
    spec = {(2, 0): 2}                                                              # zwei Farben, zwei Atome
    assert [A.structure_text(s, spec) for s in A.enumerate_structures(spec, 2)] == ["z²a", "z²b"]
    assert A.enumerate_structures(spec, 1) == []


def test_kinds_and_periods():
    assert [A.kind_of(s) for s in ({}, {(1, 0): 1}, {(1, 1): 2, (2, 0): 1}, {(1, 2): 1}, {(2, 4): 1})] == ["polynom", "polynom", "linear", "nichtlinear", "nichtlinear"]
    assert [period_of(s) for s in ({}, {(2, 2): 1}, {(2, 0): 1, (4, 1): 1}, {(2, 0): 1, (3, 1): 1})] == [1, 2, 2, 1]


def test_rational_form_of_the_linear_cases(fibonacci):
    pr, qr = A.rational_form(fibonacci)
    assert pr == [1] and qr == [1, -1, -1]                                           # 1/(1 − z − z²)
    pr, qr = A.rational_form({(1, 1): 3})
    assert pr == [1] and qr == [1, -3]
    pr, qr = A.rational_form({(1, 0): 1, (1, 1): 1})                                 # (1 + z)/(1 − z) = 1 + 2z + 2z² + …
    assert pr == [1, 1] and qr == [1, -1]
    assert A.series_from_rational(pr, qr, 4) == [1, 2, 2, 2, 2]
    assert A.rational_form({(1, 2): 1}) is None


def test_cancellation_in_the_rational_form():
    pr, qr = A.rational_form({(1, 0): 1, (1, 1): 1})
    assert len(pr) == len(qr) == 2
    spec = {(2, 0): 1, (1, 1): 1, (2, 1): 1}                                         # (1 + z²)/(1 − z − z²): kein gemeinsamer Faktor
    pr, qr = A.rational_form(spec)
    assert pr == [1, 0, 1] and qr == [1, -1, -1]
    pr, qr = A.rational_form({(1, 0): 1, (2, 0): 1, (1, 1): 1})                      # (1 + z + z²)/(1 − z) bleibt
    assert pr == [1, 1, 1] and qr == [1, -1]


def test_discriminants_by_hand(binary, motzkin):
    assert A.discriminant(binary) == [1, -4]                                         # 1 − 4z
    assert A.discriminant(motzkin) == [1, -2, -3]                                    # (1 − z)² − 4z²
    assert A.discriminant({(1, 1): 1, (1, 2): 1}) == [1, -6, 1]                      # (1 − z)² − 4z
    assert A.discriminant({(1, 1): 1}) is None and A.discriminant({(1, 3): 1}) is None
    assert A.quadratic_parts({(1, 2): 1, (1, 1): 2, (3, 0): 1}) == ([0, 1], [0, 2], [0, 0, 0, 1])


def test_closed_form_of_the_quadratic_case_equals_the_series(binary, motzkin):
    for spec in (binary, motzkin, {(1, 1): 1, (1, 2): 1}):
        a = A.series_online(spec, 80)
        for z in (0.02, 0.05, 0.1):                                               # innerhalb des Konvergenzradius jeder der drei Beispiele (kleinster: Schröder 0,1716)
            assert abs(A.quadratic_value(spec, z) - sum(float(x) * z ** n for n, x in enumerate(a))) < 1e-9
    assert A.quadratic_value({(1, 1): 1}, 0.1) is None and A.quadratic_value(binary, 0.3) is None      # Δ < 0 hinter ρ = 1/4


def test_growth_values_by_hand(binary, motzkin):
    g = A.growth(binary)
    assert g.kind == "nichtlinear" and abs(g.rho - 0.25) < 1e-12 and abs(g.tau - 2.0) < 1e-9
    assert abs(A.growth(motzkin).rho - 1 / 3) < 1e-12 and abs(A.growth(motzkin).tau - 3.0) < 1e-9
    assert abs(A.growth({(1, 1): 1, (1, 2): 1}).rho - (3 - 2 * math.sqrt(2))) < 1e-12
    assert abs(A.growth({(1, 3): 1}).rho - 4 / 27) < 1e-12 and abs(A.growth({(1, 3): 1}).tau - 1.5) < 1e-9
    assert A.growth({(1, 1): 3}).rho == pytest.approx(1 / 3) and A.growth({(1, 1): 3}).tau is None
    assert A.growth({(1, 1): 1, (2, 1): 1}).rho == pytest.approx((math.sqrt(5) - 1) / 2)
    assert A.growth({(1, 0): 1}).rho is None and A.growth({}).kind == "polynom" and A.growth({(2, 2): 1}).period == 2


def test_quotient_exponent_and_error(binary, fibonacci):
    a = A.series_online(binary, 410)
    g = A.growth(binary)
    assert 1.45 < A.exponent_alpha(a, g.rho, 1, 400) < 1.52 and A.quotient_error(a, g.rho, 1, 100) < 0.02
    assert A.quotient_error(a, g.rho, 1, 400) < A.quotient_error(a, g.rho, 1, 100) < A.quotient_error(a, g.rho, 1, 10)
    b = A.series_online(fibonacci, 410)
    assert A.quotient_error(b, A.growth(fibonacci).rho, 1, 100) < 1e-12 and abs(A.exponent_alpha(b, A.growth(fibonacci).rho, 1, 400)) < 1e-9
    assert A.quotient_error(a, g.rho, 1, 410) is None                                # a(411) fehlt: nur a(0) bis a(410) sind gerechnet
    assert A.quotient_error([1, 0, 0], 0.5, 1, 1) is None                            # a(1) = 0


def test_periodic_quotient_needs_the_step():
    spec = {(2, 2): 1}
    a = A.series_online(spec, 410)
    g = A.growth(spec)
    assert A.quotient_error(a, g.rho, 1, 400) == pytest.approx(1.0) and A.quotient_error(a, g.rho, 1, 401) is None      # Schritt 1: a(401) = 0 gibt den Fehler 1; an ungeradem n ist a(n) = 0
    assert A.quotient_error(a, g.rho, 2, 400) < 0.02


def test_guessing_the_orders(fibonacci, binary):
    r, c = A.smallest_recurrence(A.series_online(fibonacci, 60), 12)
    assert r == 2 and c == [1, 1]
    assert A.smallest_recurrence(A.series_online(binary, 80), 12) == (None, None)
    assert A.smallest_recurrence(A.series_online({(1, 1): 3}, 40), 12)[0] == 1


def test_catalan_formula_is_the_oracle_for_binary_trees(binary):
    assert A.series_online(binary, 40) == [A.catalan(n) for n in range(41)]
    assert [A.catalan(n) for n in range(6)] == [1, 1, 2, 5, 14, 42]


def test_digit_count_and_text_round_trips():
    assert A.digit_count(0) == 1 and A.digit_count(999) == 3 and A.digit_count(1000) == 4 and A.digit_count(3 ** 10000) == 4772
    with pytest.raises(ValueError):
        A.digit_count(-1)
    assert spec_text({(1, 2): 1}) == "F = 1 + z F²" and spec_text({(1, 1): 3, (2, 2): 1}) == "F = 1 + 3 z F + z² F²" and spec_text({}) == "F = 1" and spec_text({(2, 0): 1}) == "F = 1 + z²"
    for spec in ({(1, 2): 1}, {(1, 1): 3, (2, 2): 1}, {(2, 0): 2, (3, 3): 1, (1, 1): 1}):
        assert parse_spec(spec_input_text(spec)) == (spec, [])


def test_polynomial_helpers_by_hand():
    f = Fraction
    q, r = A.poly_divmod([f(-1), f(0), f(1)], [f(-1), f(1)])
    assert q == [1, 1] and r == []
    assert A.poly_gcd([f(-1), f(0), f(1)], [f(2), f(-3), f(1)]) == [-1, 1]
    assert A.poly_eval([f(1), f(2), f(3)], f(2)) == 17 and A.trim([1, 0, 0]) == [1] and A.poly_mul([], [f(1)]) == []
    assert A.terms_poly({(1, 2): 3, (2, 2): 1, (1, 1): 5}, 2) == [0, 3, 1]
    with pytest.raises(ZeroDivisionError):
        A.poly_divmod([f(1)], [])
