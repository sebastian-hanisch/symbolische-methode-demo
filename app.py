"""Symbolische Methode – Struktur beschreiben, Zahlen erhalten - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 3 der Reihe „Abzählen und erzeugende Funktionen“: Wer eine Struktur aus Bausteinen beschreibt (Atom z, Summe, Produkt, rekursiver Aufruf F), hat ihre erzeugende Funktion
schon hingeschrieben: F = 1 + Σ c·zʲ·Fᵏ. Die Zahlen fallen aus der Gleichung; bei Verschachtelung (k ≥ 2) ist F nicht rational, und das Raten einer Rekursion scheitert.
Aufbau und Regeln: DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import sym_algorithm as A
import sym_constants as C
from sym_evaluation import (
    Settings,
    analyse,
    ambiguity_rows,
    big_text,
    build_up_rows,
    class_experiment,
    de,
    equation_lines,
    equation_rows,
    growth_experiment,
    guess_experiment,
    period_note,
    structure_listing,
    verdict_ambiguity,
    verdict_build_up,
    verdict_classes,
    verdict_equation,
    verdict_growth,
    verdict_guess,
    verdict_summary,
)
from sym_layout import dunkles_design, kopf_css
from sym_pdf_export import build_pdf
from sym_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    sidebar_presets,
    sync_query_params,
)
from sym_scenario import parse_spec, spec_input_text
from sym_visualization import build_classes, build_error, build_series

st.set_page_config(page_title="Symbolische Methode – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _guess(spec_key):
    return guess_experiment(parse_spec(spec_key)[0])


@st.cache_data(show_spinner=False)
def _growth(spec_key):
    return growth_experiment(parse_spec(spec_key)[0])


@st.cache_data(show_spinner=False)
def _ambiguity():
    return ambiguity_rows()


@st.cache_data(show_spinner=False)
def _classes():
    return class_experiment()


def verdict(pair):
    kind, text = pair
    getattr(st, kind)(text)


def cell(x):
    return "–" if x is None else big_text(x)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in sym_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧩 Symbolische Methode – Struktur beschreiben, Zahlen erhalten")
st.markdown(
    """
**Muss man eine Zählfolge raten?** Nein, wenn man die Struktur beschreiben kann. Ein **Atom** ist z, ein **„oder“** ist eine Summe, ein **„und“** ein Produkt, und die Struktur darf sich selbst
enthalten (F). Aus der Beschreibung wird eine **Gleichung für die erzeugende Funktion**, F = 1 + Σ c·zʲ·Fᵏ, und die **Zahlen fallen aus der Gleichung** heraus. Kommt F höchstens einmal je Term vor,
ist F ein Bruch aus Polynomen (Stück 2). Bei **Verschachtelung** (Bäume, Klammern) nicht: Dann gibt es **keine Rekursion mit konstanten Koeffizienten**, und das Raten aus Stück 1 scheitert.

Weiter unten: **fünf Experimente** (**🔬**), eine **🎲 Spielwiese**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert die symbolische Methode", expanded=True):
    st.markdown(
        """
1. **Beschreiben:** Eine Struktur ist leer, oder sie ist ein Atom (oder mehrere) mit k Teilstrukturen derselben Art. Beispiel Binärbaum: leer oder ein Atom mit zwei Binärbäumen.
2. **Übersetzen:** Atom ↦ z, „oder“ ↦ +, „und“ ↦ ·, die Struktur selbst ↦ F. Binärbaum: F = 1 + z·F².
3. **Zahlen herausrechnen:** Der Koeffizient von zⁿ in F ist die Zahl a(n) der Strukturen mit n Atomen. Er hängt nur von Koeffizienten kleinerer Größe ab: a(n) = Σ c·[z^(n−j)] Fᵏ.
4. **Einordnen:** Höchstens ein F je Term: linear, F rational (Stück 2). Zwei oder mehr: nichtlinear, F algebraisch und **nicht** rational. Die Gleichung verrät auch das Wachstum.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Gleichung F = 1 + …**")
    spec_text_in = st.text_input("Terme", key="spec_input", max_chars=C.SPEC_TEXT_MAX,
                                 help=f"Terme der Form c z^j F^k, durch + getrennt: z F^2 heißt ein Atom mit zwei Teilstrukturen. Höchstens {C.MAX_TERMS} Terme, c bis {C.MAX_COEF}, j bis {C.MAX_J}, "
                                      f"k bis {C.MAX_K}; jeder Term braucht mindestens ein z.")
    n = st.slider("Größe n", *bounds("n_slider"), key="n_slider", help="Wie viele Atome die Strukturen haben, die die Zahl, das Diagramm und die Probe zeigen.")

sync_query_params({"spec_input": spec_text_in, "n_slider": int(n)})

settings = Settings(spec_text_in, int(n))
a = _analysis(settings)
for message in a.parse_problems:
    st.warning(message)
if a.problems:   # unabhängiger Prüfer, nicht nur im Test: lieber eine Fehlermeldung als eine stille falsche Zahl
    st.error("Die Zahlen bestehen den Prüfer nicht: " + "; ".join(a.problems))

g = a.growth
spec_key = spec_input_text(a.spec)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
m1, m2, m3, m4 = st.columns(4)
m1.metric(f"Strukturen mit {settings.n} Atomen", big_text(a.count), help="Anzahl a(n) der Strukturen der Größe n, aus der Gleichung gerechnet.")
m2.metric("Art der Gleichung", g.kind, help="Polynom: keine Teilstruktur. Linear: höchstens ein F je Term, F rational (Stück 2). Nichtlinear: Verschachtelung, F nicht rational.")
m3.metric("Wachstumsfaktor 1/ρ", "–" if g.rho is None else de(1 / g.rho, 4), help="Um diesen Faktor wächst a(n) je zusätzlichem Atom; ρ ist der Konvergenzradius der erzeugenden Funktion.")
m4.metric("Periode", f"{g.period}", help="Größter gemeinsamer Teiler der Atomzahlen j: Alle Größen sind Vielfache davon.")
if len(a.seq) > 1:
    st.plotly_chart(build_series(a.seq, g.rho), width="stretch", key="main_chart")
    st.caption("Grün: log₁₀ a(n). Grau gestrichelt: der Wachstumsfaktor hoch n. Der wachsende Abstand ist bei Verschachtelung der Faktor n^(−3/2) (Stück 9), bei linearen Gleichungen bleibt er konstant.")

st.markdown("### Die Gleichung")
st.markdown("  \n".join(equation_lines(a.spec)))
if period_note(a.spec):
    st.caption(period_note(a.spec))

with st.expander("Strukturen von Hand ansehen"):
    size = st.slider("Größe", 0, C.ENUM_SHOW_N, min(3, C.ENUM_SHOW_N), key="show_size", help=f"Bis Größe {C.ENUM_SHOW_N} lassen sich die Strukturen noch auflisten.")
    listing, total = structure_listing(a.spec, size)
    st.markdown(f"**{total}** Strukturen der Größe {size}" + (f" (die ersten {C.ENUM_SHOW_COUNT}):" if total > C.ENUM_SHOW_COUNT else ":"))
    st.code("\n".join(listing))
    st.caption("∅ ist die leere Struktur, z[…] ein Atom mit seinen Teilstrukturen in Klammern, Buchstaben hinter z unterscheiden Farben.")

if st.button("📄 PDF der aktuellen Gleichung erstellen", key="pdf_make"):
    st.session_state["pdf_made"] = (settings, build_pdf(a))
made = st.session_state.get("pdf_made")
if made and made[0] == settings:
    st.download_button("⬇️ PDF herunterladen", data=made[1], file_name="symbolische-methode.pdf", mime="application/pdf", key="pdf_download")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wie wird aus einer Beschreibung eine Zahlenfolge?")
verdict(verdict_summary(a))

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 1: Von der Gleichung zu den Zahlen")
st.caption("Drei Wege zu derselben Zahl: die Online-Rechnung aus der Gleichung, die **Festpunktiteration** (die Gleichung F ← 1 + P(z, F) immer wieder einsetzen) und das **Aufzählen** der Strukturen "
           f"(wirklich aufbauen und zählen, solange es höchstens {C.ENUM_COUNT_CAP} gibt).")
eq_rows = equation_rows(a.spec, a.seq)
st.dataframe([{"n": r["n"], "Gleichung": cell(r["Gleichung"]), "Festpunkt": cell(r["Festpunkt"]), "Aufzählen": cell(r["Aufzählen"])} for r in eq_rows], hide_index=True, width="stretch")
verdict(verdict_equation(eq_rows))

st.markdown("---")

st.subheader("🔬 Experiment 2: Raten scheitert bei Verschachtelung")
st.caption("Stück 1 hat Rekursionen mit konstanten Koeffizienten aus den ersten Gliedern geraten. Das gelingt genau, wenn F rational ist.")
guess_res = _guess(spec_key)
st.dataframe([{"Art": guess_res["kind"], "kleinste geratene Ordnung": "keine" if guess_res["order"] is None else str(guess_res["order"]),
               "Glieder geprüft": guess_res["terms"]}], hide_index=True, width="stretch")
verdict(verdict_guess(guess_res))

st.markdown("---")

st.subheader("🔬 Experiment 3: Die Beschreibung muss eindeutig sein")
st.caption("Die Grammatik E → E E | a (ein Ausdruck ist ein a oder zwei Ausdrücke hintereinander) hat die Gleichung F = 1 + z·F²: Sie zählt **Ableitungsbäume**. "
           "Für aⁿ gibt es nur ein Wort, aber viele Ableitungen.")
amb_rows = _ambiguity()
st.dataframe(amb_rows, hide_index=True, width="stretch")
verdict(verdict_ambiguity(amb_rows))

st.markdown("---")

st.subheader("🔬 Experiment 4: Wachstum aus der Gleichung")
st.caption(f"Der Konvergenzradius ρ folgt aus der Gleichung (nichtlinear: aus dem System τ = 1 + P(ρ, τ), 1 = P_F(ρ, τ), linear: aus 1 = B(ρ)). Gemessen: ρ^p·a(n + p)/a(n) gegen 1, "
           f"bei n bis {C.ERROR_N} im Diagramm und bei n = {C.GROWTH_N} im Text (p = Periode).")
growth_res = _growth(spec_key)
if growth_res["errors"]:
    st.plotly_chart(build_error(growth_res["errors"]), width="stretch", key="error_chart")
verdict(verdict_growth(growth_res))

st.markdown("---")

st.subheader("🔬 Experiment 5: Zufallsspezifikationen")
st.caption(f"{C.CLASS_SETS} Zufallsspezifikationen (feste Seeds ab {C.CLASS_SEED_BASE}, 1 bis 3 Terme mit j ∈ {{1, 2}}, k ∈ {{0, …, 3}}, Koeffizient 1 oder 2): Gleichung gegen Aufzählen, Raten, Quotient. "
           "Rechnet einige Sekunden.")
if st.button("🔬 Experiment 5 rechnen", key="class_run"):
    st.session_state["class_res"] = _classes()
class_res = st.session_state.get("class_res")
if class_res:
    st.plotly_chart(build_classes(class_res), width="stretch", key="class_chart")
    st.dataframe([{"Gruppe": key, "getestet": v[0], "auf 2 % genau": v[1], "größte Abweichung": de(100 * v[2], 2) + " %"} for key, v in class_res["quotient"].items()],
                 hide_index=True, width="stretch")
    verdict(verdict_classes(class_res))
else:
    st.info("Noch nicht gerechnet.")

st.markdown("---")

# --- Spielwiese ----------------------------------------------------------------------------------------------------------------------------

st.subheader("🎲 Spielwiese: Wie entsteht a(n)?")
st.caption("Jeder Term der Gleichung trägt zu a(n) bei: c mal der Koeffizient von z^(n−j) in Fᵏ, also die Zahl der Möglichkeiten, die restlichen n − j Atome auf die k Teilstrukturen zu verteilen.")
if a.settings.n >= 2:
    play_n = st.slider("Größe n", 1, a.settings.n, min(5, a.settings.n), key="play_n")
else:
    play_n = 1
    st.caption("Bei n = 1 gibt es nur diese Größe.")
rows = build_up_rows(a, play_n)
st.dataframe([{"Term": r["Term"], "Koeffizient von z^(n−j) in F^k": big_text(r["Koeffizient"]), "Beitrag": big_text(r["Beitrag"])} for r in rows], hide_index=True, width="stretch")
verdict(verdict_build_up(rows, play_n, a.seq[play_n]))

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    f"""
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Eine Sorte, ohne Beschriftung, nur Summe, Produkt und Rekursion** | Mengen (ungeordnete Teile), Zyklen, mehrere Sorten und beschriftete Strukturen brauchen weitere Bausteine; die Demo rechnet nur Gleichungen F = 1 + Σ c·zʲ·Fᵏ. | Stück 5 und 6 der Reihe: Multimengen, beschriftete Strukturen |
| **Jede Struktur wird genau einmal aufgebaut** | Bei mehrdeutiger Beschreibung zählt die Gleichung Ableitungen statt Gestalten (Experiment 3). Die App kann die Eindeutigkeit einer eingegebenen Gleichung nicht prüfen. | – |
| **Jeder Term hat mindestens ein Atom** | Ohne Atom (F = 1 + F²) hat die Gleichung keine eindeutige Lösung als Potenzreihe; der Parser lehnt solche Terme ab. | – |
| **Nichtlinear heißt nicht rational** | Beobachtet an {C.CLASS_SETS} Zufallsspezifikationen (Experiment 5: das Raten findet keine konstante Rekursion), nicht hier bewiesen. | Stück 9 der Reihe: Asymptotik |
| **Wachstum aus dem System** | Das System wird mit Bisektion gelöst; sie setzt voraus, dass die Funktion nur einmal das Vorzeichen wechselt. Schlägt sie fehl, nennt die App keine Zahl. Die Konvergenz des Quotienten ist ein Messbefund (Fehler wie 1/n), die Erklärung gehört zu Stück 9. | Stück 9 der Reihe: Asymptotik |
| **Zufallsspezifikationen sind klein** | Koeffizienten 1 bis 2, j ∈ {{1, 2}}, k ≤ 3: Aussagen darüber gelten für diese Familie, nicht allgemein. | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Beschreibung.** Eine Struktur der Klasse $\mathcal{F}$ ist leer ($\varepsilon$, Größe 0) oder entsteht aus einem Term $(j, k, c)$: eine von $c$ Farben, $j$ Atome und eine Folge von $k$ Strukturen aus $\mathcal{F}$. Die Größe ist die Zahl der Atome.

**Erzeugende Funktion.** Mit $a(n)$ der Zahl der Strukturen der Größe $n$ ist $F(z) = \sum_{n \ge 0} a(n) z^n$, und die Übersetzung (Atom $\mapsto z$, Summe $\mapsto +$, Produkt $\mapsto \cdot$) gibt
$F = 1 + \sum_{(j,k)} c_{jk}\, z^j F^k$. Jeder Term hat $j \ge 1$, deshalb bestimmt die Gleichung die Reihe eindeutig.

**Koeffizienten.** $a(0) = 1$ und $a(n) = \sum_{(j,k)} c_{jk}\, [z^{n-j}]\, F^k$ für $n \ge 1$; die rechte Seite braucht nur $a(0), \dots, a(n-1)$.

**Linearer Fall** ($k \le 1$). $F = \dfrac{1 + A(z)}{1 - B(z)}$ mit $A = \sum_{k=0} c_{j0} z^j$, $B = \sum_{k=1} c_{j1} z^j$: rational, Nenner $1 - B$ (Stück 2). Der Konvergenzradius $\rho$ ist die kleinste positive Nullstelle von $1 - B$.

**Quadratischer Fall** ($k \le 2$). Mit $A_2 = \sum_{k=2} c_{j2} z^j$, $B$ wie oben und $C = \sum_{k=0} c_{j0} z^j$ gilt $A_2 F^2 + (B - 1)F + (1 + C) = 0$, also
$F = \dfrac{(1 - B) - \sqrt{\Delta}}{2 A_2}$ mit $\Delta = (1 - B)^2 - 4 A_2 (1 + C)$. Beispiel $F = 1 + zF^2$: $\Delta = 1 - 4z$ und $F = \dfrac{1 - \sqrt{1 - 4z}}{2z}$, die Catalan-Zahlen $C_n = \binom{2n}{n}/(n+1)$.

**Wachstum (nichtlinear).** Der Konvergenzradius $\rho$ und der Wert $\tau = F(\rho)$ lösen das charakteristische System $\tau = 1 + P(\rho, \tau)$, $1 = P_F(\rho, \tau)$ (die Ableitung nach $F$): dort wird die Auflösung der Gleichung nach $F$ singulär. Gemessen: $a(n) \approx c\, \rho^{-n} n^{-\alpha}$ mit $\alpha$ nahe $3/2$ (Wurzelsingularität), der Quotient $\rho\, a(n+1)/a(n)$ konvergiert dann nur wie $1/n$. Bei Periode $p$ (alle Größen Vielfache von $p$) gilt dies für $\rho^p a(n+p)/a(n)$.

**Raten.** Eine lineare Rekursion mit konstanten Koeffizienten gibt es genau für rationale $F$; Catalan-Zahlen erfüllen $(n+2)\,C_{n+1} = 2(2n+1)\,C_n$ mit Koeffizienten, die von $n$ abhängen.

**Literatur** (Titel und Fundstelle aus dem Gedächtnis, nicht eingesehen).
P. Flajolet und R. Sedgewick: *Analytic Combinatorics*, Cambridge University Press 2009, Kapitel I (die symbolische Methode) und VII (positive Gleichungssysteme, Satz von Drmota, Lalley und Woods).
R. P. Stanley: *Catalan Numbers*, Cambridge University Press 2015.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
