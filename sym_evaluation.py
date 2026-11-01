"""Kennzahlen, Experimente und Verdikte. Jedes Verdikt ist eine reine Funktion (Art, Text); die App ruft st.<Art>(Text)."""

import math
from dataclasses import dataclass
from fractions import Fraction

import sym_algorithm as A
import sym_constants as C
from sym_scenario import parse_spec, period_of, random_spec, spec_text, term_text

_SUPER = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


@dataclass(frozen=True)
class Settings:
    spec: str = C.DEFAULT_SPEC             # Eingabetext der Terme
    n: int = C.DEFAULT_N


@dataclass(frozen=True, eq=False)
class Analysis:
    settings: Settings
    spec: dict
    parse_problems: list
    seq: list                              # a(0), …, a(n) als ganze Zahlen
    growth: A.Growth
    rational: tuple | None                 # (P, Q) gekürzt bei linearer oder polynomialer Spezifikation, sonst None
    problems: list                         # Meldungen des unabhängigen Prüfers

    @property
    def count(self) -> int:
        return self.seq[-1]


def check_series(spec: dict, seq: list, rational) -> list[str]:
    """Unabhängiger Prüfer (läuft auch in der App): Festpunktiteration bis CHECK_FIXPOINT_N, Aufzählen der Strukturen bis CHECK_ENUM_N (solange es höchstens ENUM_COUNT_CAP gibt),
    bei rationalem F die Reihe des Bruchs bis n = 40. Gibt Meldungen zurück, leer wenn alles stimmt."""
    problems = []
    n = len(seq) - 1
    m = min(n, C.CHECK_FIXPOINT_N)
    fix, _ = A.series_fixpoint(spec, m)
    if fix != seq[: m + 1]:
        problems.append("Die Festpunktiteration der Gleichung gibt andere Zahlen als die Online-Rechnung")
    memo: dict = {}
    for k in range(min(n, C.CHECK_ENUM_N) + 1):
        if seq[k] > C.ENUM_COUNT_CAP:
            break
        if len(A.enumerate_structures(spec, k, memo)) != seq[k]:
            problems.append(f"Beim Aufzählen der Strukturen der Größe {k} kommt eine andere Zahl heraus")
            break
    if rational is not None:
        top = min(n, 40)
        if A.series_from_rational(rational[0], rational[1], top) != [Fraction(x) for x in seq[: top + 1]]:
            problems.append("Die Reihe des Bruchs weicht von der Online-Rechnung ab")
    return problems


def analyse(settings: Settings) -> Analysis:
    spec, parse_problems = parse_spec(settings.spec)
    seq = A.series_online(spec, settings.n)
    rational = A.rational_form(spec)
    return Analysis(settings, spec, parse_problems, seq, A.growth(spec), rational, check_series(spec, seq, rational))


# ----------------------------------------------------------------------------- Formatierung

def de(x: float, digits: int = 2) -> str:
    """Zahl mit deutschem Dezimalkomma."""
    return f"{x:.{digits}f}".replace(".", ",")


def big_text(x: int) -> str:
    """Ganze Zahl lesbar: bis 12 Stellen mit Tausenderpunkt, darüber Mantisse mal Zehnerpotenz mit der Zahl der Stellen (ohne Stringumwandlung der ganzen Zahl)."""
    if x < 10 ** 12:
        return f"{x:,}".replace(",", ".")
    d = A.digit_count(x)
    lead = x // 10 ** (d - 3)
    s = str(lead)
    return f"{s[0]},{s[1:3]}·10{str(d - 1).translate(_SUPER)} ({d} Stellen)"


def coef_text(c) -> str:
    c = Fraction(c)
    return str(c.numerator) if c.denominator == 1 else f"{c.numerator}/{c.denominator}"


def poly_text(coeffs, var: str = "z") -> str:
    """Polynom aufsteigend als Text: [1, -2, -1, -1] → „1 − 2z − z² − z³“; das Nullpolynom ist „0“."""
    parts = []
    for k, c in enumerate(coeffs):
        c = Fraction(c)
        if c == 0:
            continue
        mag = abs(c)
        body = "" if k > 0 and mag == 1 else coef_text(mag) if mag.denominator == 1 else f"({coef_text(mag)})"
        power = "" if k == 0 else var if k == 1 else var + str(k).translate(_SUPER)
        parts.append(("−" if c < 0 else "+") + " " + ((body + power) or "1"))
    if not parts:
        return "0"
    first = parts[0]
    return " ".join([first[2:] if first[0] == "+" else "−" + first[2:]] + parts[1:])


def equation_lines(spec: dict) -> list[str]:
    """Die Gleichung und ihre Lösung als Textzeilen: Gleichung, Normalform, bei k ≤ 1 der Bruch, bei k = 2 die Wurzelformel mit der Diskriminante."""
    lines = [f"Gleichung: {spec_text(spec)}"]
    kind = A.kind_of(spec)
    if kind in ("polynom", "linear"):
        pr, qr = A.rational_form(spec)
        lines.append(f"Lösung: F(z) = P(z)/Q(z) mit P(z) = {poly_text(pr)} und Q(z) = {poly_text(qr)} (gekürzt)")
    elif A.max_k(spec) == 2:
        a2, b, c = A.quadratic_parts(spec)
        lines.append(f"Normalform: ({poly_text(a2)})·F² + ({poly_text([-1 + (b[0] if b else 0)] + list(b[1:]))})·F + ({poly_text([1 + (c[0] if c else 0)] + list(c[1:]))}) = 0")
        lines.append(f"Lösung: F(z) = (1 − B(z) − √Δ(z)) / (2·A(z)) mit A(z) = {poly_text(a2)}, B(z) = {poly_text(b)}, Δ(z) = {poly_text(A.discriminant(spec))}")
    else:
        lines.append(f"Normalform: Polynomgleichung vom Grad {A.max_k(spec)} in F; eine Wurzelformel gibt die App nicht an")
    return lines


# ----------------------------------------------------------------------------- Kernfrage

def verdict_summary(a: Analysis) -> tuple[str, str]:
    """Was die Gleichung verrät: Art, Wachstum und Periode in einem Satz."""
    g = a.growth
    period = f" Alle Größen sind Vielfache von {g.period}." if g.period > 1 else ""
    if g.kind == "polynom":
        top = max([j for (j, _k) in a.spec] + [0])
        return "info", f"Die Gleichung hat keine Teilstrukturen: F ist ein Polynom, es gibt Strukturen nur bis zur Größe {top}.{period}"
    rho = "nicht bestimmt" if g.rho is None else de(1 / g.rho, 4)
    if g.kind == "linear":
        return "success", (f"Die Gleichung ist **linear**: F ist ein Bruch aus Polynomen (wie in Stück 2). Die Zahl der Strukturen wächst um den Faktor {rho} je Atom.{period}")
    return "success", (f"Die Gleichung ist **nichtlinear** (Verschachtelung): F ist **kein** Bruch aus Polynomen, eine Rekursion mit konstanten Koeffizienten gibt es nicht. "
                       f"Die Zahl der Strukturen wächst um den Faktor {rho} je Atom.{period}")


# ----------------------------------------------------------------------------- Experiment 1: von der Gleichung zu den Zahlen

def equation_rows(spec: dict, seq: list, max_n: int = 12) -> list[dict]:
    """Je Größe: Zahl aus der Online-Rechnung, aus der Festpunktiteration (bis CHECK_FIXPOINT_N) und aus dem Aufzählen der Strukturen (solange höchstens ENUM_COUNT_CAP)."""
    top = min(len(seq) - 1, max_n)
    fix, rounds = A.series_fixpoint(spec, min(top, C.CHECK_FIXPOINT_N))
    memo: dict = {}
    rows = []
    for k in range(top + 1):
        enum = len(A.enumerate_structures(spec, k, memo)) if seq[k] <= C.ENUM_COUNT_CAP else None
        rows.append({"n": k, "Gleichung": seq[k], "Festpunkt": fix[k] if k < len(fix) else None, "Aufzählen": enum, "Runden": rounds})
    return rows


def structure_listing(spec: dict, size: int) -> tuple[list[str], int]:
    """(Textform der ersten ENUM_SHOW_COUNT Strukturen der Größe size, Gesamtzahl); nur für size ≤ ENUM_SHOW_N."""
    if not 0 <= size <= C.ENUM_SHOW_N:
        raise ValueError(f"size muss zwischen 0 und {C.ENUM_SHOW_N} liegen")
    items = A.enumerate_structures(spec, size)
    return [A.structure_text(s, spec) for s in items[: C.ENUM_SHOW_COUNT]], len(items)


def verdict_equation(rows: list[dict]) -> tuple[str, str]:
    checked = [r for r in rows if r["Aufzählen"] is not None]
    bad = [r["n"] for r in rows if (r["Festpunkt"] is not None and r["Festpunkt"] != r["Gleichung"]) or (r["Aufzählen"] is not None and r["Aufzählen"] != r["Gleichung"])]
    if bad:
        return "error", f"Die drei Wege geben bei n = {', '.join(map(str, bad))} verschiedene Zahlen: Das darf nicht passieren."
    rounds, top_fix = rows[0]["Runden"], min(rows[-1]["n"], C.CHECK_FIXPOINT_N)
    if not checked:
        return "success", f"Gleichung und Festpunktiteration ({rounds} Runden bis n = {top_fix}) geben dieselben Zahlen; Aufzählen wurde nicht gerechnet (zu viele Strukturen)."
    return "success", f"Gleichung, Festpunktiteration ({rounds} Runden bis n = {top_fix}) und Aufzählen der Strukturen geben bis n = {checked[-1]['n']} dieselben Zahlen."


# ----------------------------------------------------------------------------- Experiment 2: Raten scheitert bei Verschachtelung

def catalan_identity(n_max: int = C.CATALAN_IDENTITY_N) -> bool:
    """(n + 2)·C(n+1) = 2·(2n + 1)·C(n) für n = 0 … n_max − 1, mit den Zahlen aus F = 1 + zF²: eine Rekursion mit n-abhängigen Koeffizienten."""
    cat = A.series_online({(1, 2): 1}, n_max)
    return all((n + 2) * cat[n + 1] == 2 * (2 * n + 1) * cat[n] for n in range(n_max))


def guess_experiment(spec: dict) -> dict:
    """Das Raten aus Stück 1 (konstante Koeffizienten, kleinste Ordnung bis GUESS_RMAX) an den ersten GUESS_TERMS Gliedern."""
    a = A.series_online(spec, C.GUESS_TERMS - 1)
    r, coeffs = A.smallest_recurrence(a, C.GUESS_RMAX)
    return {"kind": A.kind_of(spec), "order": r, "coeffs": coeffs, "terms": len(a), "catalan": catalan_identity()}


def verdict_guess(res: dict) -> tuple[str, str]:
    base = f"Das Raten (konstante Koeffizienten bis Ordnung {C.GUESS_RMAX}, {res['terms']} Glieder) "
    if res["kind"] == "nichtlinear":
        if res["order"] is None:
            return "success", base + (f"findet **keine** Rekursion, wie es bei Verschachtelung sein muss. Für die Catalan-Zahlen (z F²) gibt es eine Rekursion mit n-abhängigen Koeffizienten: "
                                      f"(n + 2)·C(n+1) = 2·(2n + 1)·C(n), geprüft bis n = {C.CATALAN_IDENTITY_N - 1}: {'stimmt' if res['catalan'] else 'stimmt nicht'}.")
        return "warning", base + f"findet Ordnung {res['order']}, obwohl die Gleichung nichtlinear ist: Das ist überraschend und kein Beweis für Rationalität."
    if res["order"] is None:
        return "warning", base + "findet bei einer linearen Gleichung keine Rekursion (zu hohe Ordnung?)."
    return "success", base + f"findet bei dieser {'polynomialen' if res['kind'] == 'polynom' else 'linearen'} Gleichung die Ordnung {res['order']}."


# ----------------------------------------------------------------------------- Experiment 3: Eindeutigkeit

def leaves(s) -> int:
    """Zahl der leeren Blätter einer Struktur (∅ zählt 1)."""
    return 1 if s == () else sum(leaves(x) for x in s[2])


def ambiguity_rows(n_max: int = C.AMBIGUITY_N) -> list[dict]:
    """Grammatik E → E E | a. Ihre Ableitungsbäume für aⁿ sind die Binärbäume mit n − 1 inneren Knoten (F = 1 + zF²), das Wort aⁿ gibt es nur einmal."""
    binary = {(1, 2): 1}
    a = A.series_online(binary, n_max - 1)
    rows = []
    for n in range(1, n_max + 1):
        trees = A.enumerate_structures(binary, n - 1)
        words = {"a" * leaves(t) for t in trees}
        rows.append({"n": n, "Gleichung": a[n - 1], "aufgezählt": len(trees), "verschiedene Wörter": len(words)})
    return rows


def verdict_ambiguity(rows: list[dict]) -> tuple[str, str]:
    bad = [r["n"] for r in rows if r["Gleichung"] != r["aufgezählt"]]
    if bad:
        return "error", f"Gleichung und Aufzählung weichen bei n = {', '.join(map(str, bad))} ab."
    last = rows[-1]
    return "warning", (f"Für aⁿ zählt die Gleichung {last['Gleichung']} Ableitungen bei n = {last['n']}, aber es gibt nur {last['verschiedene Wörter']} Wort. "
                       "Eine mehrdeutige Beschreibung zählt Ableitungen, nicht Wörter: Die Beschreibung muss jede Gestalt genau einmal aufbauen.")


# ----------------------------------------------------------------------------- Experiment 4: Wachstum aus der Gleichung

def growth_experiment(spec: dict) -> dict:
    """Konvergenzradius ρ aus der Gleichung gegen den Quotienten ρ^p·a(n + p)/a(n) (p = Periode): Fehler über n bis ERROR_N und Exponent α bei n = GROWTH_N."""
    g = A.growth(spec)
    out = {"growth": g, "errors": [], "alpha": None, "final_error": None, "n_eval": None}
    if g.rho is None:
        return out
    p = g.period
    n_eval = (C.GROWTH_N // p) * p
    a = A.series_online(spec, n_eval + p)
    out["errors"] = [(n, A.quotient_error(a, g.rho, p, n)) for n in range(p, C.ERROR_N + 1, p)]
    out["alpha"] = A.exponent_alpha(a, g.rho, p, n_eval)
    out["final_error"] = A.quotient_error(a, g.rho, p, n_eval)
    out["n_eval"] = n_eval
    return out


def verdict_growth(res: dict) -> tuple[str, str]:
    g = res["growth"]
    if g.kind == "polynom":
        return "info", "Ohne Teilstrukturen gibt es kein exponentielles Wachstum: Die Zahlen brechen nach der größten Atomzahl ab."
    if g.rho is None:
        return "warning", "Der Wachstumsfaktor wurde nicht bestimmt (das System lässt sich hier nicht lösen): Die App nennt dann keine Zahl."
    system = (f"ρ = {de(g.rho, 6)} (Wachstumsfaktor 1/ρ = {de(1 / g.rho, 6)}" + (f", τ = F(ρ) = {de(g.tau, 6)}" if g.tau is not None else "") + ")")
    step = f" Wegen der Periode {g.period} wird a(n + {g.period})/a(n) betrachtet." if g.period > 1 else ""
    text = (f"Aus {'dem System τ = 1 + P(ρ, τ), 1 = P_F(ρ, τ)' if g.kind == 'nichtlinear' else '1 = B(ρ)'}: {system}.{step} "
            f"Bei n = {res['n_eval']} weicht ρ^{g.period}·a(n + {g.period})/a(n) um {de(100 * res['final_error'], 2)} % von 1 ab, α ≈ {de(res['alpha'], 3)}.")
    if g.kind == "nichtlinear":
        return "success", text + " Der Fehler fällt nur wie 1/n (α nahe 3/2): Das ist die Wurzelsingularität, die Stück 9 erklärt."
    return "success", text + " Der Fehler fällt exponentiell schnell (α nahe 0), wie bei Stück 2."


# ----------------------------------------------------------------------------- Experiment 5: Zufallsspezifikationen

def class_experiment(count: int = C.CLASS_SETS, seed_base: int = C.CLASS_SEED_BASE) -> dict:
    """`count` Zufallsspezifikationen (feste Seeds): Gleichung gegen Aufzählen (bis CLASS_ENUM_N), Raten, Quotient gegen ρ bei n = CLASS_QUOTIENT_N (nur nichtlineare, exponentiell wachsende)."""
    kinds = {"polynom": 0, "linear": 0, "nichtlinear": 0}
    guess_found = {"polynom": 0, "linear": 0, "nichtlinear": 0}
    enum_bad = enum_checked = 0
    quotient = {"aperiodisch": [0, 0, 0.0], "periodisch": [0, 0, 0.0], "periodisch ohne Schritt p": [0, 0, 0.0]}
    for seed in range(seed_base, seed_base + count):
        spec = random_spec(seed)
        kind = A.kind_of(spec)
        kinds[kind] += 1
        a = A.series_online(spec, C.CLASS_SERIES_N - 1)
        r, _ = A.smallest_recurrence(a, C.GUESS_RMAX)
        guess_found[kind] += r is not None
        memo: dict = {}
        for k in range(C.CLASS_ENUM_N + 1):
            if a[k] > C.ENUM_COUNT_CAP:
                break
            enum_checked += 1
            enum_bad += len(A.enumerate_structures(spec, k, memo)) != a[k]
        if kind != "nichtlinear":
            continue
        g = A.growth(spec)
        if g.rho is None:
            continue
        p = g.period
        n = (C.CLASS_QUOTIENT_N // p) * p
        b = A.series_online(spec, n + p)
        if b[n] == 0:
            continue
        key = "aperiodisch" if p == 1 else "periodisch"
        err = A.quotient_error(b, g.rho, p, n)
        quotient[key][0] += 1
        quotient[key][1] += err < C.GROWTH_TOL
        quotient[key][2] = max(quotient[key][2], err)
        if p > 1:
            err1 = A.quotient_error(b, g.rho, 1, n)
            quotient["periodisch ohne Schritt p"][0] += 1
            quotient["periodisch ohne Schritt p"][1] += err1 < C.GROWTH_TOL
            quotient["periodisch ohne Schritt p"][2] = max(quotient["periodisch ohne Schritt p"][2], err1)
    return {"count": count, "kinds": kinds, "guess_found": guess_found, "enum_bad": enum_bad, "enum_checked": enum_checked, "quotient": quotient}


def verdict_classes(res: dict) -> tuple[str, str]:
    k, g, q = res["kinds"], res["guess_found"], res["quotient"]
    text = (f"Von {res['count']} Zufallsspezifikationen sind {k['linear']} linear, {k['nichtlinear']} nichtlinear und {k['polynom']} Polynome. "
            f"Das Raten findet bei {g['linear']} der linearen und bei {g['nichtlinear']} der nichtlinearen eine konstante Rekursion. "
            f"Gleichung und Aufzählen weichen in {res['enum_bad']} von {res['enum_checked']} Größen ab. "
            f"Der Quotient ρ^p·a(n + p)/a(n) liegt bei n = {C.CLASS_QUOTIENT_N} bei {q['aperiodisch'][1]} von {q['aperiodisch'][0]} aperiodischen und {q['periodisch'][1]} von {q['periodisch'][0]} periodischen "
            f"auf {de(100 * C.GROWTH_TOL, 0)} % genau (periodisch ohne Schritt p: {q['periodisch ohne Schritt p'][1]} von {q['periodisch ohne Schritt p'][0]}).")
    ok = res["enum_bad"] == 0 and g["nichtlinear"] == 0 and g["linear"] == k["linear"] and g["polynom"] == k["polynom"]
    return ("success" if ok else "warning"), text


# ----------------------------------------------------------------------------- Spielwiese: wie entsteht a(n)?

def build_up_rows(a: Analysis, n: int) -> list[dict]:
    """Je Term der Gleichung der Beitrag zu a(n) (n ≥ 1): Term, Koeffizient von z^(n−j) in Fᵏ, c mal dieser Koeffizient. Die Summe ist a(n)."""
    return [{"Term": term_text(r["j"], r["k"], r["c"]), "Koeffizient": r["coefficient"], "Beitrag": r["contribution"]} for r in A.contributions(a.spec, a.seq, n)]


def verdict_build_up(rows: list[dict], n: int, total: int) -> tuple[str, str]:
    s = sum(r["Beitrag"] for r in rows)
    if s != total:
        return "error", f"Die Beiträge ergeben {s}, die Rechnung {total}: Das darf nicht passieren."
    return "success", f"a({n}) = {big_text(total)}: die Beiträge der Terme ergeben genau diese Zahl."


def period_note(spec: dict) -> str:
    p = period_of(spec)
    return "" if p == 1 else f"Periode {p}: Es gibt nur Größen, die Vielfache von {p} sind."
