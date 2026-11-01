"""Eigenschaften (ORACLE-PLAYBOOK §5): Aussagen, die für jede Spezifikation gelten, auf festen Zufallsständen."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

import sym_algorithm as A
from sym_scenario import parse_spec, random_spec, spec_input_text

ROOT = Path(__file__).resolve().parent.parent


def _spec(seed: int) -> dict:
    return random_spec(2000 + seed)


@pytest.mark.parametrize("seed", range(40))
def test_an_additional_term_never_decreases_the_counts(seed):
    spec = _spec(seed)
    more = dict(spec)
    more[(1 + seed % 2, seed % 3)] = more.get((1 + seed % 2, seed % 3), 0) + 1
    a, b = A.series_online(spec, 12), A.series_online(more, 12)
    assert all(y >= x for x, y in zip(a, b)), (spec, more)


@pytest.mark.parametrize("seed", range(40))
def test_a_larger_coefficient_never_decreases_the_counts(seed):
    spec = _spec(seed)
    key = sorted(spec)[0]
    more = dict(spec)
    more[key] = spec[key] + 2
    assert all(y >= x for x, y in zip(A.series_online(spec, 12), A.series_online(more, 12)))


@pytest.mark.parametrize("seed", range(40))
def test_substituting_z_by_z_to_the_p_spreads_the_counts_to_multiples_of_p(seed):
    spec = _spec(seed)
    p = 2 + seed % 3
    spread = {(j * p, k): c for (j, k), c in spec.items()}
    a, b = A.series_online(spec, 8), A.series_online(spread, 8 * p)
    assert [b[p * n] for n in range(9)] == a
    assert all(b[m] == 0 for m in range(8 * p + 1) if m % p)


@pytest.mark.parametrize("seed", range(40))
def test_order_of_terms_and_duplicates_do_not_change_the_counts(seed):
    spec = _spec(seed)
    text = " + ".join(reversed(spec_input_text(spec).split(" + ")))
    assert parse_spec(text)[0] == spec
    doubled = parse_spec(spec_input_text(spec) + " + " + spec_input_text(spec))[0]
    assert doubled == {key: 2 * c for key, c in spec.items()}


@pytest.mark.parametrize("seed", range(40))
def test_structure_sizes_and_the_decomposition_add_up(seed):
    spec = _spec(seed)
    a = A.series_online(spec, 6)
    memo: dict = {}
    for n in range(7):
        if a[n] > 5000:
            break
        assert all(A.structure_size(s) == n for s in A.enumerate_structures(spec, n, memo))
    for n in range(1, 7):
        assert sum(r["contribution"] for r in A.contributions(spec, a, n)) == a[n]


@pytest.mark.parametrize("seed", range(40))
def test_counts_of_a_specification_with_a_period_vanish_outside_its_multiples(seed):
    spec = _spec(seed)
    p = A.growth(spec).period
    a = A.series_online(spec, 20)
    assert all(a[n] == 0 for n in range(1, 21) if n % p)


def test_result_does_not_depend_on_the_hash_seed():
    """Wörterbücher und Mengen ordnen sich je Prozess anders (Hash-Randomisierung, hier von Tupeln und Zeichenketten): dasselbe Szenario in zwei Prozessen muss dasselbe geben."""
    code = (
        "import sym_algorithm as A; from sym_scenario import parse_spec; "
        "s = parse_spec('z F^2 + 2 z^2 F + z^3 F^3 + 3 z')[0]; "
        "print(A.series_online(s, 15), sorted(A.growth(s).__dict__.items()), [A.structure_text(x, s) for x in A.enumerate_structures(s, 3)][:5])"
    )
    outs = []
    for hash_seed in ("1", "2"):
        env = dict(os.environ, PYTHONHASHSEED=hash_seed)
        outs.append(subprocess.run([sys.executable, "-X", "utf8", "-c", code], cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", check=True).stdout)
    assert outs[0] == outs[1] and outs[0].strip()
