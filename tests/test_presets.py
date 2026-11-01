"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, jedes Preset zeigt etwas anderes."""

import sym_algorithm as A
import sym_constants as C
import sym_evaluation as ev
import sym_presets as P
from sym_scenario import parse_spec


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_regler_bounds():
    for name, preset in C.PRESETS.items():
        assert C.N_MIN <= preset["n"] <= C.N_MAX and len(preset["spec"]) <= C.SPEC_TEXT_MAX, name


def test_every_preset_parses_without_a_message_and_passes_the_checker():
    for name, preset in C.PRESETS.items():
        assert parse_spec(preset["spec"])[1] == [], name
        a = ev.analyse(ev.Settings(**preset))
        assert a.problems == [] and a.parse_problems == [], name


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS["Binärbäume (Catalan)"]) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_presets_cover_the_three_worlds_and_the_period():
    """Kein totes Preset: lineare und nichtlineare Gleichungen, eine mit Periode, und die Zahlenfolgen unterscheiden sich."""
    kinds, periods, sequences = {}, {}, set()
    for name, preset in C.PRESETS.items():
        spec = parse_spec(preset["spec"])[0]
        kinds[name], periods[name] = A.kind_of(spec), A.growth(spec).period
        sequences.add(tuple(A.series_online(spec, 8)))
    assert sorted(set(kinds.values())) == ["linear", "nichtlinear"] and sum(k == "linear" for k in kinds.values()) == 3 and sum(k == "nichtlinear" for k in kinds.values()) == 5
    assert [n for n, p in periods.items() if p == 2] == ["Nur gerade Größen"]
    assert len(sequences) == len(C.PRESETS)
