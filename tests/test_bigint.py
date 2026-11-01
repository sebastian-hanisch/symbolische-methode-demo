"""Große ganze Zahlen: Python wandelt Zahlen mit mehr als 4300 Stellen nicht in Text um (ValueError). Die Demo rechnet bis n = 100 mit bis zu 9ⁿ·… Strukturen; keine Stelle darf str(x)
auf Zählwerte anwenden. Die Grenze wird über `digit_count` und Zehnerpotenzen umgangen."""

import math
import sys

import pytest

import sym_algorithm as A
import sym_evaluation as ev
import sym_visualization as V


def _digits_by_string(x: int) -> int:
    old = sys.get_int_max_str_digits()
    sys.set_int_max_str_digits(0)
    try:
        return len(str(x))
    finally:
        sys.set_int_max_str_digits(old)


@pytest.mark.parametrize("x", [pytest.param(v, id=label) for v, label in [(0, "0"), (1, "1"), (9, "9"), (10, "10"), (99, "99"), (100, "100"), (10 ** 17, "1e17"), (3 ** 10000, "3^10000"),
                                                                             (10 ** 5000, "1e5000"), (10 ** 5000 - 1, "1e5000-1")]])
def test_digit_count_equals_the_string_length(x):
    assert A.digit_count(x) == _digits_by_string(x)


def test_big_text_and_log10_for_huge_numbers():
    assert ev.big_text(10 ** 5000) == "1,00·10⁵⁰⁰⁰ (5001 Stellen)"
    assert abs(V._log10(10 ** 5000) - 5000.0) < 1e-9 and abs(V._log10(3 ** 10000) - 10000 * math.log10(3)) < 1e-6
    assert V._log10(1) == 0.0 and abs(V._log10(12345) - math.log10(12345)) < 1e-12


def test_the_largest_analysis_with_huge_counts_renders_its_texts():
    a = ev.analyse(ev.Settings("9 z F^4 + 9 z^2 F^4", 100))
    assert a.count > 10 ** 100 and "Stellen" in ev.big_text(a.count)
    fig = V.build_series(a.seq, a.growth.rho)
    assert len(fig.data) == 2 and fig.data[0].y[-1] > 100
    rows = ev.build_up_rows(a, 100)
    assert ev.verdict_build_up(rows, 100, a.count)[0] == "success"
