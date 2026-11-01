"""AppTest-Durchläufe der Experimente, des Permalinks und der Spielwiese (die allgemeinen Rauchtests stehen in test_app.py)."""

import os
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import sym_constants as C

APP = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))


def _app(query: dict | None = None) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    for key, value in (query or {}).items():
        at.query_params[key] = value
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _all_text(at) -> str:
    return " | ".join(e.value for e in list(at.success) + list(at.info) + list(at.warning) + list(at.error))


def test_standard_case_shows_the_hand_values_and_no_error():
    at = _app()
    assert not at.error
    metrics = {m.label: m.value for m in at.metric}
    assert metrics["Strukturen mit 10 Atomen"] == "16.796" and metrics["Art der Gleichung"] == "nichtlinear"
    assert metrics["Wachstumsfaktor 1/ρ"] == "4,0000" and metrics["Periode"] == "1"
    assert any("Gleichung: F = 1 + z F²" in m.value and "Δ(z) = 1 − 4z" in m.value for m in at.markdown)


def test_experiments_one_to_four_show_their_verdicts_without_a_click():
    text = _all_text(_app())
    assert "geben bis n = 10 dieselben Zahlen" in text and "findet **keine** Rekursion" in text
    assert "429 Ableitungen bei n = 8" in text and "Der Fehler fällt nur wie 1/n" in text


def test_class_experiment_runs_on_click():
    at = _app()
    at.button(key="class_run").click().run(timeout=TIMEOUT)
    assert not at.exception and not at.error
    assert any(f"Von {C.CLASS_SETS} Zufallsspezifikationen sind 41 linear, 219 nichtlinear und 40 Polynome" in s.value for s in at.success)


def test_playground_slider_changes_the_decomposition():
    at = _app()
    at.slider(key="play_n").set_value(3).run(timeout=TIMEOUT)
    assert not at.exception and any(s.value.startswith("a(3) = 5:") for s in at.success)
    at.slider(key="play_n").set_value(10).run(timeout=TIMEOUT)
    assert any(s.value.startswith("a(10) = 16.796:") for s in at.success)


def test_n_equal_one_has_no_playground_slider_and_does_not_crash():
    at = _app({"n": "1"})
    assert not at.error and not [s for s in at.slider if s.key == "play_n"]
    assert at.metric[0].value == "1"


def test_structure_viewer():
    at = _app()
    at.slider(key="show_size").set_value(3).run(timeout=TIMEOUT)
    assert any("5** Strukturen der Größe 3" in m.value for m in at.markdown)
    assert any("z[z[∅, ∅], z[∅, ∅]]" in c.value for c in at.code)


def test_permalink_loads_and_clamps_the_values():
    at = _app({"spec": "z F + z^2 F^2", "n": "9999"})
    assert at.sidebar.text_input(key="spec_input").value == "z F + z^2 F^2" and at.sidebar.slider(key="n_slider").value == C.N_MAX
    assert at.metric[1].value == "nichtlinear"


def test_permalink_with_garbage_is_ignored_or_cut():
    at = _app({"spec": "z" * 500, "n": "abc"})
    assert len(at.sidebar.text_input(key="spec_input").value) <= C.SPEC_TEXT_MAX and at.sidebar.slider(key="n_slider").value == C.DEFAULT_N


@pytest.mark.parametrize("text, fragment", [("F^2", "mindestens ein z"), ("z F^9", "höher als F^4"), ("z F^2 - z", "Minuszeichen"), ("10 z", "Koeffizient 10")])
def test_invalid_terms_are_reported_and_do_not_crash(text, fragment):
    at = _app()
    at.sidebar.text_input(key="spec_input").set_value(text).run(timeout=TIMEOUT)
    assert not at.exception and any(fragment in w.value for w in at.warning)


def test_empty_specification_renders():
    at = _app()
    at.sidebar.text_input(key="spec_input").set_value("").run(timeout=TIMEOUT)
    assert not at.exception and not at.error and any("keine Teilstrukturen" in i.value for i in at.info)


@pytest.mark.parametrize("spec", ["9 z F^4 + 9 z^2 F^4", "z^12 F^4", "z^2", "3 z F", "z + z^2 + z^3 + z^4 + z^5 + z^6"])
def test_extreme_specifications_render_without_error(spec):
    at = _app()
    at.sidebar.text_input(key="spec_input").set_value(spec).run(timeout=TIMEOUT)
    assert not at.exception and not at.error, spec


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_every_preset_renders_without_error_or_checker_message(name):
    at = _app()
    at.sidebar.button(key=f"preset_{name}").click().run(timeout=TIMEOUT)
    assert not at.exception and not at.error, name


def test_pdf_can_be_made_for_the_extreme_settings():
    for query in ({"n": "1"}, {"n": "100"}, {"spec": ""}, {"spec": "z^2 F^2"}):
        at = _app(query)
        at.button(key="pdf_make").click().run(timeout=TIMEOUT)
        assert not at.exception, query
