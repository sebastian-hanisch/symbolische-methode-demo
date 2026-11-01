"""Szenario: Spezifikationen F = 1 + Σ c·zʲ·Fᵏ als Text, Parser mit Meldungen, Zufallsspezifikationen für Experiment 5.

Eine Spezifikation ist ein Wörterbuch {(j, k): c}: der Term c·zʲ·Fᵏ heißt „c Farben, j Atome, k Teilstrukturen“. Jeder Term hat mindestens ein Atom (j ≥ 1);
so kostet jeder rekursive Aufruf Größe, und die Gleichung hat genau eine Lösung als Potenzreihe."""

import math
import random
import re

import sym_constants as C

_SUP = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
_TERM = re.compile(r"(\d+)?\s*\*?\s*z(?:\s*\^\s*(\d+))?\s*\*?\s*(?:F(?:\s*\^\s*(\d+))?)?", re.IGNORECASE)


def parse_spec(text: str) -> tuple[dict, list[str]]:
    """Terme aus einem Text wie „z F^2 + 2 z^2 F“ (auch „F = 1 + z F^2“, „2*z^2*F“); Leerraum und * egal, F und z in jeder Schreibweise.

    Gibt (Spezifikation, Meldungen) zurück. Ungültige Terme werden verworfen und gemeldet, nie still ersetzt; gleiche Terme werden addiert."""
    spec: dict = {}
    problems: list[str] = []
    body = text[: C.SPEC_TEXT_MAX * 4].strip()
    body = re.sub(r"^\s*F\s*=\s*", "", body, flags=re.IGNORECASE)
    body = re.sub(r"^\s*1\s*(\+|$)", "", body)
    if "−" in body or "-" in body:
        problems.append("Minuszeichen sind nicht erlaubt: Die Terme werden nur addiert (positive Koeffizienten).")
        body = body.replace("−", "+").replace("-", "+")
    for raw in body.split("+"):
        raw = raw.strip()
        if not raw:
            continue
        m = _TERM.fullmatch(raw)
        if not m:
            hint = " Jeder Term braucht mindestens ein z." if "z" not in raw.lower() else ""
            problems.append(f"„{raw}“ ist kein Term der Form c·z^j·F^k.{hint}")
            continue
        c = int(m.group(1)) if m.group(1) else 1
        j = int(m.group(2)) if m.group(2) else 1
        has_f = "f" in raw.lower()
        k = (int(m.group(3)) if m.group(3) else 1) if has_f else 0
        if c < 1 or c > C.MAX_COEF:
            problems.append(f"„{raw}“: Koeffizient {c} liegt nicht zwischen 1 und {C.MAX_COEF} und zählt nicht.")
            continue
        if not 1 <= j <= C.MAX_J:
            problems.append(f"„{raw}“: z^{j} liegt nicht zwischen z^1 und z^{C.MAX_J} und zählt nicht.")
            continue
        if k > C.MAX_K:
            problems.append(f"„{raw}“: F^{k} ist höher als F^{C.MAX_K} und zählt nicht.")
            continue
        spec[(j, k)] = spec.get((j, k), 0) + c
    if len(spec) > C.MAX_TERMS:
        problems.append(f"Mehr als {C.MAX_TERMS} verschiedene Terme: nur die ersten {C.MAX_TERMS} zählen.")
        spec = dict(list(spec.items())[: C.MAX_TERMS])
    return spec, problems


def term_text(j: int, k: int, c: int = 1) -> str:
    """Ein Term als Text: z, z², 3 z F, z F²; k = 0 lässt F weg."""
    parts = []
    if c != 1:
        parts.append(str(c))
    parts.append("z" if j == 1 else "z" + str(j).translate(_SUP))
    if k >= 1:
        parts.append("F" if k == 1 else "F" + str(k).translate(_SUP))
    return " ".join(parts)


def spec_text(spec: dict) -> str:
    """Gleichung als Text: F = 1 + z F² + z² F; die leere Spezifikation ist F = 1."""
    if not spec:
        return "F = 1"
    return "F = 1 + " + " + ".join(term_text(j, k, c) for (j, k), c in sorted(spec.items()))


def spec_input_text(spec: dict) -> str:
    """Die Terme im Eingabeformat (ASCII), so dass `parse_spec` sie wieder liest."""
    out = []
    for (j, k), c in sorted(spec.items()):
        out.append(" ".join(([str(c)] if c != 1 else []) + ["z" if j == 1 else f"z^{j}"] + ([] if k == 0 else ["F" if k == 1 else f"F^{k}"])))
    return " + ".join(out)


def period_of(spec: dict) -> int:
    """Periode p: der größte gemeinsame Teiler aller Exponenten j (alle Größen sind Vielfache von p); 1 bei leerer Spezifikation."""
    return math.gcd(*[j for (j, _k) in spec]) if spec else 1


def random_spec(seed: int) -> dict:
    """Zufallsspezifikation für Experiment 5, deterministisch aus dem Seed: 1 bis 3 Terme mit j in {1, 2}, k in {0, …, 3} und Koeffizient 1 oder 2 (gleiche Terme werden überschrieben)."""
    rng = random.Random(seed)
    spec: dict = {}
    for _ in range(rng.randint(1, 3)):
        spec[(rng.randint(1, 2), rng.randint(0, 3))] = rng.randint(1, 2)
    return spec
