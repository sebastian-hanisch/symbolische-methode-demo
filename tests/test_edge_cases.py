"""Randfälle, an denen Kernroutinen und Parser erfahrungsgemäß brechen (DEMO-PLAYBOOK §12)."""

import pytest

import sym_algorithm as A
import sym_constants as C
import sym_evaluation as ev
from sym_scenario import parse_spec, period_of, random_spec


def test_parser_accepts_the_documented_spellings():
    expected = ({(1, 2): 1}, [])
    for text in ("z F^2", "F = 1 + z F^2", "1 + z F^2", "z*F^2", "Z f ^ 2", "  z   F^2  ", "1 + z F^2 + "):
        assert parse_spec(text) == expected, text
    assert parse_spec("2*z^2*F^3 + z f") == ({(2, 3): 2, (1, 1): 1}, [])
    assert parse_spec("z + z") == ({(1, 0): 2}, []) and parse_spec("") == ({}, []) and parse_spec("1") == ({}, []) and parse_spec("F = 1") == ({}, [])


def test_parser_reports_and_drops_invalid_terms():
    for text, fragment in (("F^2", "mindestens ein z"), ("z F^5", "höher als F^4"), ("z^13", "z^13"), ("10 z", "Koeffizient 10"), ("0 z", "Koeffizient 0"),
                           ("z G", "kein Term"), ("z F^2 + 3", "„3“ ist kein Term"), ("z^0 F", "z^0")):
        spec, problems = parse_spec(text)
        assert any(fragment in m for m in problems), (text, problems)
        assert (1, 2) not in spec or text.startswith("z F^2")
    spec, problems = parse_spec("z F^2 + z G")
    assert spec == {(1, 2): 1} and len(problems) == 1


def test_parser_boundaries_are_inclusive():
    assert parse_spec(f"{C.MAX_COEF} z^{C.MAX_J} F^{C.MAX_K}") == ({(C.MAX_J, C.MAX_K): C.MAX_COEF}, [])
    assert parse_spec(f"{C.MAX_COEF + 1} z")[0] == {} and parse_spec(f"z^{C.MAX_J + 1}")[0] == {} and parse_spec(f"z F^{C.MAX_K + 1}")[0] == {}
    seven = " + ".join(f"z^{j}" for j in range(1, 8))
    spec, problems = parse_spec(seven)
    assert len(spec) == C.MAX_TERMS and len(problems) == 1
    six = " + ".join(f"z^{j}" for j in range(1, 7))
    assert len(parse_spec(six)[0]) == 6 and parse_spec(six)[1] == []


def test_parser_minus_signs_and_garbage():
    spec, problems = parse_spec("z F^2 - z")
    assert spec == {(1, 2): 1, (1, 0): 1} and len(problems) == 1 and "Minuszeichen" in problems[0]
    assert parse_spec("§$%&")[0] == {} and parse_spec("z^^2")[0] == {} and parse_spec("z F^")[0] == {}
    assert len(parse_spec("z " * 5000)[1]) == 1                                      # sehr lange Eingabe: abgeschnitten, eine Meldung, kein Absturz


def test_empty_specification_analysis():
    a = ev.analyse(ev.Settings("", 5))
    assert a.seq == [1, 0, 0, 0, 0, 0] and a.growth.kind == "polynom" and a.problems == [] and a.rational == ([1], [1])
    assert ev.verdict_summary(a) == ("info", "Die Gleichung hat keine Teilstrukturen: F ist ein Polynom, es gibt Strukturen nur bis zur Größe 0.")


def test_n_equal_one_and_the_largest_n():
    a = ev.analyse(ev.Settings("z F^2", 1))
    assert a.seq == [1, 1] and a.problems == []
    big = ev.analyse(ev.Settings("9 z F^4 + 9 z^2 F^4", C.N_MAX))
    assert len(big.seq) == C.N_MAX + 1 and big.problems == [] and big.count > 10 ** 100


def test_k_equal_four_is_fuss_catalan():
    a = A.series_online({(1, 4): 1}, 6)
    assert a == [1, 1, 4, 22, 140, 969, 7084]                                       # C(4n, n)/(3n + 1)
    assert A.growth({(1, 4): 1}).rho == pytest.approx(27 / 256)                       # ρ = 3³/4⁴ für F = 1 + zF⁴


def test_negative_arguments_raise():
    with pytest.raises(ValueError):
        A.series_online({}, -1)
    with pytest.raises(ValueError):
        ev.structure_listing({(1, 2): 1}, C.ENUM_SHOW_N + 1)
    with pytest.raises(ValueError):
        ev.structure_listing({(1, 2): 1}, -1)


def test_equation_rows_skip_enumeration_when_there_are_too_many_structures():
    a = ev.analyse(ev.Settings("z F^2", 12))
    rows = ev.equation_rows(a.spec, a.seq)
    assert [r["Aufzählen"] is None for r in rows] == [False] * 11 + [True] * 2 and rows[10]["Aufzählen"] == 16796
    assert ev.verdict_equation(rows)[1].endswith("bis n = 10 dieselben Zahlen.")
    assert rows[12]["Gleichung"] == 208012 and rows[12]["Festpunkt"] == 208012 and rows[0]["Runden"] == 13


def test_a_huge_equation_row_without_any_enumeration():
    a = ev.analyse(ev.Settings("9 z F^4 + 9 z^2 F^4", 12))
    rows = ev.equation_rows(a.spec, a.seq)
    assert any(r["Aufzählen"] is None for r in rows) and all(r["Aufzählen"] is not None for r in rows[:3])


def test_the_period_of_a_random_specification_is_the_gcd_of_the_exponents():
    for seed in range(100):
        spec = random_spec(seed)
        assert period_of(spec) in (1, 2) and (period_of(spec) == 2) == all(j == 2 for (j, _k) in spec)


def test_random_specs_are_deterministic_and_inside_the_documented_ranges():
    assert random_spec(7) == random_spec(7)
    for seed in range(300):
        spec = random_spec(seed)
        assert 1 <= len(spec) <= 3 and all(j in (1, 2) and 0 <= k <= 3 and c in (1, 2) for (j, k), c in spec.items())


def test_listing_of_structures():
    texts, total = ev.structure_listing({(1, 2): 1}, 3)
    assert total == 5 and len(texts) == 5 and ev.structure_listing({(1, 2): 1}, 0) == (["∅"], 1)
    texts, total = ev.structure_listing({(1, 3): 3}, 5)
    assert total == 3 ** 5 * 273 and len(texts) == C.ENUM_SHOW_COUNT
