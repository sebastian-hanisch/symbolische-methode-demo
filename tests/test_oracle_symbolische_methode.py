"""Orakel-Tests: die Gleichung gegen unabhängige Rechenwege (DEMO-PLAYBOOK §12, ORACLE-PLAYBOOK §5).

Unabhängig heißt: Aufzählen der wirklich aufgebauten Strukturen, die Festpunktiteration der Gleichung (anderes Verfahren als die Online-Rechnung), die Reihe des Bruchs (linearer
Fall), die geschlossene Lösung der quadratischen Gleichung, bekannte Formeln aus der Literatur (Catalan, Motzkin, Fuss–Catalan, Schröder) und der Quotient bei großem n. Feste Zufallsstände."""

import math
from fractions import Fraction

import pytest

import sym_algorithm as A
import sym_constants as C
from sym_scenario import parse_spec, random_spec


def _spec(seed: int) -> dict:
    return random_spec(1000 + seed)


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_every_preset_equation_equals_enumeration_up_to_n8(name):
    spec = parse_spec(C.PRESETS[name]["spec"])[0]
    a = A.series_online(spec, 8)
    top = 8 if a[8] <= 60000 else 6
    memo: dict = {}
    assert [len(A.enumerate_structures(spec, n, memo)) for n in range(top + 1)] == a[: top + 1]


@pytest.mark.parametrize("seed", range(60))
def test_random_specs_equation_equals_enumeration_and_fixpoint(seed):
    spec = _spec(seed)
    a = A.series_online(spec, 12)
    fix, _ = A.series_fixpoint(spec, 12)
    assert fix == a, spec
    memo: dict = {}
    for n in range(8):
        if a[n] > 20000:
            break
        assert len(A.enumerate_structures(spec, n, memo)) == a[n], (spec, n)


def test_linear_random_specs_equal_the_series_of_their_fraction():
    """Mindestens 15 der 100 Zufallsspezifikationen sind linear oder Polynom; für alle gleicht die Reihe des Bruchs der Online-Rechnung."""
    checked = 0
    for seed in range(100):
        spec = _spec(seed)
        rational = A.rational_form(spec)
        if rational is None:
            continue
        checked += 1
        assert A.series_from_rational(rational[0], rational[1], 40) == [Fraction(x) for x in A.series_online(spec, 40)], spec
    assert checked >= 15


def test_literature_catalan_motzkin_schroeder_and_fuss_catalan():
    binary = A.series_online({(1, 2): 1}, 30)
    assert binary == [math.comb(2 * n, n) // (n + 1) for n in range(31)]
    assert all((n + 2) * binary[n + 1] == 2 * (2 * n + 1) * binary[n] for n in range(30))
    motzkin = A.series_online({(1, 1): 1, (2, 2): 1}, 30)
    assert motzkin[:8] == [1, 1, 2, 4, 9, 21, 51, 127]
    assert all((n + 2) * motzkin[n] == (2 * n + 1) * motzkin[n - 1] + 3 * (n - 1) * motzkin[n - 2] for n in range(2, 31))
    assert A.series_online({(1, 1): 1, (1, 2): 1}, 6) == [1, 2, 6, 22, 90, 394, 1806]
    assert A.series_online({(1, 3): 1}, 25) == [math.comb(3 * n, n) // (2 * n + 1) for n in range(26)]


def test_compositions_literature():
    """Kompositionen von n in beliebigen Summanden: 2^(n−1); in Summanden 1 und 2 die Fibonacci-Zahlen."""
    every = {(j, 1): 1 for j in range(1, 13)}                                       # Summanden 1 bis 12
    a = A.series_online(every, 12)
    assert a[:13] == [1] + [2 ** (n - 1) for n in range(1, 13)]
    fib = A.series_online({(1, 1): 1, (2, 1): 1}, 20)
    f = [1, 1]
    for _ in range(19):
        f.append(f[-1] + f[-2])
    assert fib == f


@pytest.mark.parametrize("name", ["Binärbäume (Catalan)", "Motzkin-Pfade", "Schröder (groß)", "Ternäre Bäume", "Fibonacci-Wörter", "Wörter über 3 Buchstaben"])
def test_radius_of_convergence_equals_the_limit_of_the_quotient(name):
    spec = parse_spec(C.PRESETS[name]["spec"])[0]
    g = A.growth(spec)
    a = A.series_online(spec, 410)
    assert A.quotient_error(a, g.rho, g.period, 400) < 0.02, name


@pytest.mark.parametrize("name", ["Fibonacci-Wörter", "Wörter über 3 Buchstaben", "Kompositionen mit Teilen 1 bis 3"])
def test_linear_radius_is_a_root_of_one_minus_b(name):
    spec = parse_spec(C.PRESETS[name]["spec"])[0]
    g = A.growth(spec)
    assert abs(sum(c * g.rho ** j for (j, k), c in spec.items() if k == 1) - 1) < 1e-12


@pytest.mark.parametrize("seed", range(60))
def test_random_specs_the_guessing_finds_a_constant_recurrence_exactly_for_rational_f(seed):
    spec = _spec(seed)
    r, _ = A.smallest_recurrence(A.series_online(spec, 89), 12)
    assert (r is not None) == (A.kind_of(spec) != "nichtlinear"), spec


def test_tribonacci_like_compositions_have_the_tribonacci_constant():
    spec = parse_spec("z F + z^2 F + z^3 F")[0]
    assert abs(1 / A.growth(spec).rho - 1.8392867552141612) < 1e-12
    assert A.series_online(spec, 7) == [1, 1, 2, 4, 7, 13, 24, 44]
