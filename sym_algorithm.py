"""Kern der Demo (nur Standardbibliothek): aus der Gleichung F = 1 + Σ c·zʲ·Fᵏ die Zahlen, die Strukturen, den Bruch oder die quadratische Lösung und das Wachstum.

Jede Regel ist eine eigene Funktion mit expliziten Ein- und Ausgaben (DEMO-PLAYBOOK §1b):
`series_online` rechnet die Koeffizienten aus der Gleichung, `series_fixpoint` ist der unabhängige Prüfer (Iteration der Gleichung), `enumerate_structures` baut die
Strukturen wirklich auf, `growth` löst das charakteristische System für den Wachstumsfaktor, `rational_form` und `discriminant` lesen den linearen Fall und den quadratischen
Fall ab, `smallest_recurrence` ist das Raten aus Stück 1. Polynome sind Listen von Koeffizienten, aufsteigend (Index = Potenz von z)."""

import math
from dataclasses import dataclass
from fractions import Fraction
from itertools import product

import sym_constants as C
from sym_scenario import period_of

BISECTION_STEPS = 80                         # Halbierungen: bei Gleitkomma genügen etwa 55


def max_k(spec: dict) -> int:
    """Höchste Potenz von F in der Gleichung (0 bei leerer Spezifikation)."""
    return max([k for (_j, k) in spec] + [0])


def kind_of(spec: dict) -> str:
    """„polynom“ (keine Teilstruktur), „linear“ (höchstens eine Teilstruktur je Term, F rational) oder „nichtlinear“ (Verschachtelung)."""
    m = max_k(spec)
    return "polynom" if m == 0 else ("linear" if m == 1 else "nichtlinear")


# ----------------------------------------------------------------------------- Koeffizienten aus der Gleichung

def series_online(spec: dict, n_max: int) -> list[int]:
    """a(0), …, a(n_max) aus F = 1 + Σ c·zʲ·Fᵏ: a(n) = Σ c·[z^(n−j)] Fᵏ. Die Potenzen Fᵏ werden mit jedem bekannten Koeffizienten fortgeschrieben (O(K·n²) ganze Zahlen)."""
    if n_max < 0:
        raise ValueError("n_max darf nicht negativ sein")
    kmax = max(max_k(spec), 1)
    a = [1]
    pw = {0: [1], 1: [1]}
    for k in range(2, kmax + 1):
        pw[k] = [1]
    for n in range(1, n_max + 1):
        total = 0
        for (j, k), c in spec.items():
            if n - j >= 0:
                total += c * pw[k][n - j]
        a.append(total)
        pw[0].append(0)
        pw[1].append(total)
        for k in range(2, kmax + 1):
            pw[k].append(sum(pw[k - 1][i] * a[n - i] for i in range(n + 1)))
    return a


def power_series(a: list[int], k: int, n_max: int) -> list[int]:
    """Koeffizienten von F^k bis n_max, aus den Koeffizienten a von F (k = 0 gibt 1, 0, 0, …)."""
    out = [1] + [0] * n_max
    base = list(a[: n_max + 1]) + [0] * max(0, n_max + 1 - len(a))
    for _ in range(k):
        out = [sum(out[i] * base[m - i] for i in range(m + 1)) for m in range(n_max + 1)]
    return out


def series_fixpoint(spec: dict, n_max: int) -> tuple[list[int], int]:
    """Unabhängiger Rechenweg: die Gleichung F ← 1 + P(z, F) bis zur Abschneidung n_max iterieren; gibt (a(0..n_max), Zahl der Runden) zurück.

    Jede Runde gewinnt mindestens ein richtiges Glied (jeder Term hat ein Atom), nach höchstens n_max + 2 Runden ändert sich nichts mehr."""
    f = [1] + [0] * n_max
    for rounds in range(1, n_max + 3):
        new = [1] + [0] * n_max
        for (j, k), c in spec.items():
            pk = power_series(f, k, n_max)
            for m in range(n_max + 1 - j):
                new[m + j] += c * pk[m]
        if new == f:
            return f, rounds
        f = new
    raise ArithmeticError("Festpunktiteration konvergiert nicht (jeder Term braucht ein Atom)")


def contributions(spec: dict, a: list[int], n: int) -> list[dict]:
    """Beitrag jedes Terms zu a(n) (n ≥ 1): c·[z^(n−j)] Fᵏ; die Summe ist a(n). Für Experiment „Wie entsteht a(n)?“."""
    if n < 1 or n >= len(a):
        raise ValueError("n muss zwischen 1 und len(a) − 1 liegen")
    rows = []
    for (j, k), c in sorted(spec.items()):
        coeff = power_series(a, k, n)[n - j] if n - j >= 0 else 0
        rows.append({"j": j, "k": k, "c": c, "coefficient": coeff, "contribution": c * coeff})
    return rows


# ----------------------------------------------------------------------------- Strukturen aufbauen

def compositions(total: int, parts: int):
    """Alle Folgen von `parts` ganzen Zahlen ≥ 0 mit Summe `total`; für parts = 0 genau die leere Folge, wenn total = 0."""
    if parts == 0:
        if total == 0:
            yield ()
        return
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in compositions(total - first, parts - 1):
            yield (first,) + rest


def enumerate_structures(spec: dict, n: int, memo: dict | None = None) -> list:
    """Alle Strukturen der Größe n als verschachtelte Tupel ((j, k), Farbe, Teilstrukturen); die leere Struktur () hat Größe 0."""
    memo = {} if memo is None else memo
    if n in memo:
        return memo[n]
    out: list = [()] if n == 0 else []
    for (j, k), c in sorted(spec.items()):
        rest = n - j
        if rest < 0:
            continue
        for sizes in compositions(rest, k):
            for subs in product(*[enumerate_structures(spec, s, memo) for s in sizes]):
                for color in range(c):
                    out.append(((j, k), color, subs))
    memo[n] = out
    return out


def structure_text(s, spec: dict) -> str:
    """Eine Struktur als Text: ∅ für die leere, sonst z[…], z²[…] mit den Teilstrukturen in eckigen Klammern; Farben als Buchstaben (nur wenn der Term mehrere hat)."""
    if s == ():
        return "∅"
    (j, k), color, subs = s
    label = "z" if j == 1 else "z" + str(j).translate(str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹"))
    if spec.get((j, k), 1) > 1:
        label += chr(ord("a") + color)
    return label + ("[" + ", ".join(structure_text(x, spec) for x in subs) + "]" if subs else "")


def structure_size(s) -> int:
    """Größe = Zahl der Atome in der Struktur."""
    if s == ():
        return 0
    (j, _k), _color, subs = s
    return j + sum(structure_size(x) for x in subs)


# ----------------------------------------------------------------------------- Polynome über Q (aufsteigend)

def trim(p) -> list:
    p = list(p)
    while p and p[-1] == 0:
        p.pop()
    return p


def poly_mul(a, b) -> list:
    if not a or not b:
        return []
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def poly_divmod(a, b):
    a, b = trim(a), trim(b)
    if not b:
        raise ZeroDivisionError("Division durch das Nullpolynom")
    q = [Fraction(0)] * max(1, len(a) - len(b) + 1)
    r = list(a)
    while len(r) >= len(b) and r:
        c = r[-1] / b[-1]
        k = len(r) - len(b)
        q[k] = c
        for i, y in enumerate(b):
            r[i + k] -= c * y
        r = trim(r)
    return trim(q), r


def poly_gcd(a, b) -> list:
    a, b = trim(a), trim(b)
    while b:
        _, r = poly_divmod(a, b)
        a, b = b, r
    return [x / a[-1] for x in a]


def poly_eval(p, z):
    v = 0
    for c in reversed(p):
        v = v * z + c
    return v


def terms_poly(spec: dict, k: int) -> list[int]:
    """Das Polynom Σ c·zʲ über alle Terme mit genau k Teilstrukturen (aufsteigend, Index = j)."""
    out: list[int] = []
    for (j, kk), c in spec.items():
        if kk == k:
            out += [0] * (j + 1 - len(out))
            out[j] += c
    return out


def series_from_rational(pr, qr, n: int) -> list[Fraction]:
    """Die ersten n + 1 Glieder der Reihe von P/Q (Q(0) = 1)."""
    out: list[Fraction] = []
    for k in range(n + 1):
        v = pr[k] if k < len(pr) else Fraction(0)
        for j in range(1, min(k, len(qr) - 1) + 1):
            v -= qr[j] * out[k - j]
        out.append(v)
    return out


def rational_form(spec: dict):
    """Linearer oder polynomialer Fall (max k ≤ 1): F = (1 + A)/(1 − B) mit A = Terme ohne F, B = Terme mit einem F, gekürzt; (P, Q) mit Q(0) = 1.

    Nichtlineare Spezifikationen haben keinen solchen Bruch (None)."""
    if max_k(spec) > 1:
        return None
    a = [Fraction(c) for c in terms_poly(spec, 0)]
    b = [Fraction(c) for c in terms_poly(spec, 1)]
    p = [Fraction(1) + (a[0] if a else 0)] + a[1:]
    q = [Fraction(1) - (b[0] if b else 0)] + [-x for x in b[1:]]
    p, q = trim(p), trim(q)
    g = poly_gcd(p, q)
    pr, _ = poly_divmod(p, g)
    qr, _ = poly_divmod(q, g)
    c = qr[0]
    return [x / c for x in pr], [x / c for x in qr]


def quadratic_parts(spec: dict):
    """Für max k = 2: die Gleichung A·F² + (B − 1)·F + (1 + C) = 0 mit ganzzahligen Polynomen A (Terme mit F²), B (Terme mit F), C (Terme ohne F); sonst None."""
    if max_k(spec) != 2:
        return None
    return terms_poly(spec, 2), terms_poly(spec, 1), terms_poly(spec, 0)


def discriminant(spec: dict):
    """Δ(z) = (1 − B)² − 4·A·(1 + C) für max k = 2 (ganzzahlige Koeffizienten); F = ((1 − B) − √Δ)/(2A). Sonst None."""
    parts = quadratic_parts(spec)
    if parts is None:
        return None
    a, b, c = [Fraction(x) for x in parts[0]], [Fraction(x) for x in parts[1]], [Fraction(x) for x in parts[2]]
    one_minus_b = [Fraction(1) - (b[0] if b else 0)] + [-x for x in b[1:]]
    one_plus_c = [Fraction(1) + (c[0] if c else 0)] + c[1:]
    sq = poly_mul(one_minus_b, one_minus_b)
    ac = [4 * x for x in poly_mul(a, one_plus_c)]
    n = max(len(sq), len(ac))
    d = [(sq[i] if i < len(sq) else 0) - (ac[i] if i < len(ac) else 0) for i in range(n)]
    return [int(x) for x in trim(d)]


def quadratic_value(spec: dict, z: float):
    """F(z) aus der geschlossenen Lösung der quadratischen Gleichung (kleinere Wurzel), für z im Konvergenzbereich; sonst None."""
    parts = quadratic_parts(spec)
    if parts is None:
        return None
    a, b, c = (float(poly_eval(p, z)) for p in parts)
    disc = float(poly_eval(discriminant(spec), z))
    if disc < 0 or a == 0:
        return None
    return ((1 - b) - math.sqrt(disc)) / (2 * a) if a else None


# ----------------------------------------------------------------------------- Wachstum

@dataclass(frozen=True)
class Growth:
    kind: str                  # „polynom“, „linear“ oder „nichtlinear“
    rho: float | None          # Konvergenzradius ρ der erzeugenden Funktion (Wachstumsfaktor 1/ρ); None bei Polynom oder wenn das System nicht gelöst wurde
    tau: float | None          # F(ρ) bei nichtlinearen Spezifikationen
    period: int                # ggT der Exponenten j


def growth(spec: dict) -> Growth:
    """Konvergenzradius ρ: linear = kleinste positive Nullstelle von 1 − B(z); nichtlinear = Lösung des charakteristischen Systems τ = 1 + P(ρ, τ), 1 = P_F(ρ, τ) (Bisektion);
    Polynom: kein ρ. Schlägt die Bisektion fehl, ist ρ = None (die App meldet es, statt eine Zahl zu erfinden)."""
    kind = kind_of(spec)
    period = period_of(spec)
    if kind == "polynom":
        return Growth(kind, None, None, period)

    def P(z, f):
        return sum(c * z ** j * f ** k for (j, k), c in spec.items())

    def PF(z, f):
        return sum(c * k * z ** j * f ** (k - 1) for (j, k), c in spec.items() if k >= 1)

    if kind == "linear":
        lin = {j: c for (j, k), c in spec.items() if k == 1}
        lo, hi = 0.0, 1.0
        while sum(c * hi ** j for j, c in lin.items()) < 1:
            hi *= 2
        for _ in range(BISECTION_STEPS):
            mid = (lo + hi) / 2
            if sum(c * mid ** j for j, c in lin.items()) < 1:
                lo = mid
            else:
                hi = mid
        return Growth(kind, (lo + hi) / 2, None, period)

    def z_of(tau):
        lo, hi = 0.0, 1.0
        while P(hi, tau) < tau - 1:
            hi *= 2
        for _ in range(BISECTION_STEPS):
            mid = (lo + hi) / 2
            if P(mid, tau) < tau - 1:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    lo, hi = 1.0 + 1e-12, 2.0
    while PF(z_of(hi), hi) - 1 < 0:
        hi *= 2
        if hi > 1e12:
            return Growth(kind, None, None, period)
    for _ in range(BISECTION_STEPS):
        mid = (lo + hi) / 2
        if PF(z_of(mid), mid) - 1 < 0:
            lo = mid
        else:
            hi = mid
    tau = (lo + hi) / 2
    return Growth(kind, z_of(tau), tau, period)


def ratio_quantity(a: list[int], rho: float, period: int, n: int) -> float | None:
    """ρ^p · a(n + p) / a(n): strebt gegen 1 (p = Periode, n ein Vielfaches von p); None, wenn a(n) = 0 oder die Glieder fehlen."""
    if n + period >= len(a) or a[n] == 0:
        return None
    return (a[n + period] * 10 ** 15 // a[n]) / 10 ** 15 * rho ** period


def quotient_error(a: list[int], rho: float, period: int, n: int) -> float | None:
    """|ρ^p · a(n + p)/a(n) − 1|; None, wenn nicht definiert."""
    r = ratio_quantity(a, rho, period, n)
    return None if r is None else abs(r - 1)


def exponent_alpha(a: list[int], rho: float, period: int, n: int) -> float | None:
    """α ≈ n·(1 − ρ^p·a(n + p)/a(n)) / p: der Exponent in a(n) ≈ c·ρ^(−n)·n^(−α); bei linearer Spezifikation nahe 0, bei nichtlinearer nahe 3/2."""
    r = ratio_quantity(a, rho, period, n)
    return None if r is None else n * (1 - r) / period


# ----------------------------------------------------------------------------- Raten aus Stück 1 und Hilfen

def solve_recurrence(a: list[int], r: int):
    """Koeffizienten c_1..c_r mit a(n) = Σ c_j a(n−j) aus a(0)..a(2r−1) (Brüche); None, wenn das System singulär ist."""
    if r < 1 or len(a) < 2 * r:
        return None
    m = [[Fraction(a[n - j]) for j in range(1, r + 1)] + [Fraction(a[n])] for n in range(r, 2 * r)]
    for i in range(r):
        p = next((k for k in range(i, r) if m[k][i] != 0), None)
        if p is None:
            return None
        m[i], m[p] = m[p], m[i]
        d = m[i][i]
        m[i] = [x / d for x in m[i]]
        for k in range(r):
            if k != i and m[k][i] != 0:
                f = m[k][i]
                m[k] = [x - f * y for x, y in zip(m[k], m[i])]
    return [m[i][r] for i in range(r)]


def fits_until(a: list[int], c) -> int | None:
    """Größtes n, bis zu dem die Rekursion mit den Koeffizienten c alle Glieder ab n = len(c) trifft; len(a) − 1, wenn sie alle trifft."""
    r = len(c)
    last_ok = None
    for n in range(r, len(a)):
        if a[n] != sum(c[j - 1] * a[n - j] for j in range(1, r + 1)):
            return last_ok if last_ok is not None else r - 1
        last_ok = n
    return len(a) - 1


def smallest_recurrence(a: list[int], rmax: int):
    """Kleinste Ordnung r ≤ rmax, deren aus 2r Gliedern bestimmte Rekursion mit konstanten Koeffizienten alle weiteren Glieder trifft; (r, Koeffizienten) oder (None, None)."""
    for r in range(1, rmax + 1):
        if len(a) < 2 * r + 1:
            break
        c = solve_recurrence(a, r)
        if c is not None and fits_until(a, c) == len(a) - 1:
            return r, c
    return None, None


def digit_count(x: int) -> int:
    """Zahl der Dezimalstellen einer ganzen Zahl x ≥ 0, ohne sie in einen String zu wandeln (Python begrenzt die Umwandlung auf 4300 Stellen)."""
    if x < 0:
        raise ValueError("x darf nicht negativ sein")
    d = max(1, int(x.bit_length() * 0.30102999566398))
    while 10 ** d <= x:
        d += 1
    while d > 1 and 10 ** (d - 1) > x:
        d -= 1
    return d


def catalan(n: int) -> int:
    """Catalan-Zahl C(2n, n)/(n + 1): geschlossene Formel, Orakel für F = 1 + zF²."""
    return math.comb(2 * n, n) // (n + 1)
