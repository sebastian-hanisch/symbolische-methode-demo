# Symbolische Methode – Struktur beschreiben, Zahlen erhalten – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-symbolische-methode-demo.streamlit.app/)** -->

Stück 3 von 16 der Reihe **„Abzählen und erzeugende Funktionen“** in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ (die Linie wird erst vollständig veröffentlicht). Vorgänger sind `aufzaehlen-rekursion-demo` (Stück 1: Zustandsrekursion) und `rationale-ef-demo` (Stück 2: der Bruch P/Q aus dem Automaten). Diese Demo schreibt die erzeugende Funktion **aus einer Beschreibung** hin: Atom = z, „oder“ = +, „und“ = ·, rekursiver Aufruf = F, also F = 1 + Σ c·zʲ·Fᵏ, und die Zahlen fallen aus der Gleichung. Eingabe ist die Gleichung als Text (Presets: Binärbäume, Motzkin-Pfade, große Schröder-Zahlen, ternäre Bäume, Fibonacci-Wörter, Wörter, Kompositionen, ein periodischer Fall). Kante zu Stück 2: Strukturen mit Verschachtelung (k ≥ 2) haben keinen endlichen Automaten, F ist dort **nicht** rational.

## Warum dieses Problem

Muss man eine Zählfolge raten? Nein, wenn man die Struktur beschreiben kann. Die Demo zeigt zwei Welten mit demselben Verfahren: Bei höchstens einem F je Term ist die Gleichung linear und F ein Bruch (Stück 2); bei Verschachtelung ist sie nichtlinear, eine Rekursion mit konstanten Koeffizienten gibt es nicht, und das Raten aus Stück 1 scheitert.

## Befunde und Korrekturen gegenüber dem Plan

- **Hook bestätigt:** „Catalan-Zahlen liegen vor, ohne eine Rekursion zu raten“; das Raten findet bei den nichtlinearen Presets nie eine Rekursion.
- **Zufallsspezifikationen der App anders als in Phase 0:** In der App rechnet Experiment 5 die Seeds ab 5000 mit Quotient bei n = 200 (statt 400), damit es in etwa zehn Sekunden fertig ist. Die Phase-0-Zahlen bei n = 400 (Seeds ab 7000) sind im Test nachgerechnet (siehe Befunde).
- **Neu gegenüber der Gliederung:** der Quotient a(n+1)/a(n) konvergiert bei Verschachtelung nur wie 1/n (Exponent α nahe 3/2), bei linearen Gleichungen exponentiell schnell; bei **Periode** p > 1 (alle Größen Vielfache von p) ist der einfache Quotient wertlos und a(n + p)/a(n) richtig.
- **Zwei Fehler beim ersten Testlauf:** Ein Test erwartete bei einem Polynom mit Periode keinen Periodenhinweis (der Hinweis ist richtig, der Test wurde korrigiert); die Zerlegung beschriftete Terme als „z^3“, die Gleichung als „z³“ (jetzt überall `term_text`). Dazu ein schwacher Prüftest (`… or …`), den ich durch einen gezielten ersetzt habe, der nur das Aufzählen anschlagen lässt.
- **Port:** Der Plan sah 9313 vor; ihn hat inzwischen `sekretaerproblem-demo` belegt, die Demo läuft auf 9314.
- **Browser-Lehre (wiederholt aus Stück 2):** Ist das Vorschau-Fenster verdeckt, messen die Diagramme 16 px Breite, und Plotly meldet `<text> attribute y: Expected length, "-Infinity"`. Mit festem Viewport (1100 × 800) stimmen die Breiten (630 px), die Achsenbereiche sind sinnvoll und es kommen keine neuen Konsolenfehler dazu.
- **Wachstumsberechnung beschleunigt:** Die verschachtelte Bisektion (200 mal 200 Schritte) kostete in Experiment 5 etwa 18 Sekunden; mit 80 Halbierungen (Gleitkomma braucht etwa 55) sind es 5.

## Modell

Eine Spezifikation ist ein Wörterbuch {(j, k): c}: Term c·zʲ·Fᵏ mit c Farben, j ≥ 1 Atomen und k Teilstrukturen derselben Klasse; die Struktur ist leer (Größe 0) oder entsteht aus einem Term. Die Koeffizienten folgen aus a(n) = Σ c·[z^(n−j)] Fᵏ (`series_online`, O(K·n²) große ganze Zahlen). Linearer Fall: F = (1 + A)/(1 − B), gekürzt (`rational_form`). Quadratischer Fall: F = ((1 − B) − √Δ)/(2A) mit Δ = (1 − B)² − 4A(1 + C) (`discriminant`). Wachstum: kleinste Nullstelle von 1 − B (linear) beziehungsweise Lösung des Systems τ = 1 + P(ρ, τ), 1 = P_F(ρ, τ) durch Bisektion (`growth`). Die Formeln stehen im 📐-Expander der App.

## Methodik

- **Unabhängiger Prüfer in der App** (`check_series`): Festpunktiteration der Gleichung bis n = 12 (`series_fixpoint`), Aufzählen der wirklich aufgebauten Strukturen bis n = 7 (solange es höchstens 30 000 gibt, `enumerate_structures`), bei rationalem F die Reihe des Bruchs bis n = 40; bei Abweichung zeigt die App einen Fehler statt einer Zahl.
- **Raten** (`smallest_recurrence`, Stück 1): Rekursion mit konstanten Koeffizienten aus den ersten 2r Gliedern, bis Ordnung 12 an den ersten 80 Gliedern.
- **Wachstum**: ρ aus der Gleichung, geprüft am Quotienten ρ^p·a(n + p)/a(n) (p = ggT der Exponenten j), Exponent α ≈ n(1 − Quotient)/p.
- **Eindeutigkeit**: die mehrdeutige Grammatik E → E E | a als feste Tabelle (Gleichung, aufgezählte Ableitungsbäume, verschiedene Wörter).
- **Eingabe**: strenger Parser (`parse_spec`), höchstens 6 Terme, c ≤ 9, j ≤ 12, k ≤ 4, jeder Term mit mindestens einem z; ungültige Terme werden gemeldet und verworfen.

## Befunde (gemessen, keine Behauptungen)

Jede Zahl steht in `tests/test_claims.py`, `tests/test_algorithm.py`, `tests/test_verdicts.py` oder `tests/test_oracle_symbolische_methode.py`. **Zeiten** (Aufzählen gegen Gleichung gegen Formel) stehen in keinem Test; Phase 0 maß sie als Größenordnung (Catalan, n = 12: Aufzählen 0,36 s, Gleichung 0,09 ms; n = 1000: Gleichung 0,56 s); sie hängen vom Rechner ab, eine unabhängige Nachmessung ergab dieselbe Größenordnung (0,18 s, 0,047 ms, 0,32 s).

| Frage | Befund |
|---|---|
| Handwerte | Binärbäume 1, 1, 2, 5, 14, 42, 132, 429, 1430, 4862, 16796 (gleich C(2n, n)/(n + 1)); Motzkin 1, 1, 2, 4, 9, 21, 51, 127; Schröder 1, 2, 6, 22, 90, 394; ternär 1, 1, 3, 12, 55, 273; Fibonacci-Wörter 1, 1, 2, 3, 5, 8, 13; Kompositionen mit Teilen 1 bis 3 1, 1, 2, 4, 7, 13, 24, 44; nur gerade Größen 1, 0, 1, 0, 2, 0, 5, 0, 14 |
| Gleichung gegen Aufzählen der Strukturen | alle 8 Presets bis n = 8 (bei mehr als 60 000 Strukturen bis n = 6) gleich; 60 Zufallsspezifikationen (Seeds ab 1000) gegen Aufzählen und Festpunkt bis n = 12 gleich; **300 Spezifikationen (Phase 0) bis n = 6 oder 7: 0 Abweichungen**; Experiment 5 (Seeds ab 5000): 0 von 2048 Größen abweichend |
| Festpunktiteration | n + 1 Runden: 11 bei Binärbäumen bis n = 10, 6 beim periodischen Preset |
| Raten bei den Presets | Binärbäume, Motzkin, Schröder, ternär und „nur gerade Größen“: **keine** Rekursion bis Ordnung 12; Fibonacci-Wörter Ordnung 2, Wörter über 3 Buchstaben Ordnung 1, Kompositionen mit Teilen 1 bis 3 Ordnung 3 |
| Raten bei 300 Zufallsspezifikationen (Seeds ab 5000) | 40 Polynome und 41 lineare: **81 von 81** mit Rekursion; 219 nichtlineare: **0 von 219** |
| Catalan hat eine Rekursion mit n-abhängigen Koeffizienten | (n + 2)·C(n+1) = 2·(2n + 1)·C(n) für n = 0 bis 199 |
| Eindeutigkeit | E → E E \| a: Ableitungen für aⁿ 1, 1, 2, 5, 14, 42, 132, 429 (n = 1 bis 8), verschiedene Wörter jeweils 1 |
| Wachstumsradius | Binärbäume ρ = 1/4 (τ = 2), Motzkin 1/3 (τ = 3), Schröder 3 − 2√2 (τ = 1 + √2), ternär 4/27 (τ = 1,5); linear: 1/3 (Wörter), (√5 − 1)/2 (Fibonacci-Wörter), 0,5437 (Kompositionen, Tribonacci-Konstante 1,8393 als Kehrwert); Abweichung höchstens 10⁻¹² |
| Quotient a(n+1)/a(n) gegen 1/ρ | **nichtlinear nur wie 1/n:** Binärbäume 12,5 % (n = 10), etwa 1,5 % (n = 100), α bei n = 400 etwa 1,49; bei n = 1000 liegt α der vier verschachtelten Presets zwischen 1,49 und 1,50. **Linear exponentiell schnell:** Fibonacci-Wörter etwa 3,5·10⁻⁵ bei n = 10 und unter 10⁻¹² bei n = 100 |
| Zufallsspezifikationen, Quotient bei n = 200 (Experiment 5, 219 nichtlineare) | aperiodisch **154 von 154** auf 2 % genau (größte Abweichung unter 0,75 %); periodisch (Periode 2) **65 von 65** mit Schritt p (unter 1,5 %), **0 von 65** ohne Schritt (zwangsläufig: bei Periode 2 ist a(201) = 0, die Abweichung beträgt 100 %, das ist kein Messbefund) |
| Phase 0, Quotient bei n = 400 (Seeds ab 7000, 202 nichtlineare) | aperiodisch 157, periodisch 45; alle auf 2 % genau; α bei den aperiodischen zwischen 1,489 und 1,494 (n^(−3/2)) |
| Brücke zu Stück 2 | Wörter aus A, B ohne AA (Stück 2: 1, 2, 3, 5, 8, …) sind die Kompositionen in 1 und 2 von n + 1 (1, 1, 2, 3, 5, …), in 11 von 11 Gliedern gleich |
| Diskriminanten | Binärbäume Δ = 1 − 4z; Motzkin Δ = 1 − 2z − 3z²; große Schröder-Zahlen Δ = 1 − 6z + z² |
| Presets | 3 linear, 5 nichtlinear, 1 mit Periode 2 |

## Ehrliche Grenzen

- **Eine Familie, nicht die ganze symbolische Methode:** eine Sorte, unbeschriftet, nur Summe, Produkt und Rekursion mit mindestens einem Atom je Term. Mengen, Zyklen, mehrere Sorten und beschriftete Strukturen kommen mit Stück 5 und 6.
- **Eindeutigkeit prüft die App nicht.** Jede eingegebene Gleichung gilt als eindeutig gemeint; die Aufzählung zählt Konstruktionen, nicht Gestalten (Experiment 3 zeigt den Unterschied).
- **„Nichtlinear heißt nicht rational“** ist hier ein Messbefund (0 von 219) mit bekanntem Hintergrund, kein Beweis der Demo.
- **Wachstums-Solver:** Die Bisektion setzt einen einzigen Vorzeichenwechsel voraus; an 300 + 300 Zufallsspezifikationen kein Ausfall, aber nicht allgemein bewiesen; bei Misserfolg nennt die App keine Zahl.
- **Quotient und Exponent sind Messungen** (n = 200 oder 400), die Erklärung (Wurzelsingularität, n^(−3/2)) gehört zu Stück 9.
- **Zufallsspezifikationen sind klein:** Koeffizienten 1 bis 2, j ∈ {1, 2}, k ≤ 3, höchstens 3 Terme.
- **Die Online-Rechnung wächst mit n²** (große Ganzzahlen); die App begrenzt n auf 100.
- **Browser:** Experiment 5 wurde nur im AppTest per Klick geprüft, im Browser nicht; Handy-Breite nicht geprüft; ohne sichtbares Vorschau-Fenster melden die Diagramme Konsolenfehler (siehe oben).
- Alles simuliert, keine echten Daten.

## Verifikation

- **Kern:** Handwerte der drei Beispiele, Catalan-Formel, Motzkin-Rekursion, Schröder-Zahlen und die ternäre Formel C(3n, n)/(2n + 1) als Literatur, Aufzählen der Strukturen, Festpunktiteration, Reihe des Bruchs, geschlossene Lösung der quadratischen Gleichung gegen die Teilsummen der Reihe, ρ gegen bekannte Werte und gegen den Quotienten.
- **Eigenschaften:** ein Term oder Koeffizient mehr lässt a(n) nie sinken, Substitution z → zᵖ, Reihenfolge und Doppelungen der Terme, Größe der aufgebauten Strukturen, Zerlegung nach Termen summiert sich zu a(n), Periode, gleiches Ergebnis in zwei Prozessen mit verschiedenem `PYTHONHASHSEED`.
- **Randfälle:** leere Spezifikation, nur Atome, k = 4, j = 12, größte Koeffizienten bei n = 100, Parser an den Grenzen und mit Müll, sehr lange Eingabe, n = 1.
- **Große Zahlen:** `digit_count` statt `str(x)` (Python begrenzt die Umwandlung auf 4300 Stellen), getestet bis 10⁵⁰⁰⁰ und mit dem größten Fall (n = 100, Koeffizienten 9, k = 4).
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler an Minimum und Maximum), Experimente ohne Klick, Experiment 5 auf Klick, Spielwiese, Strukturansicht, Permalink mit Müll und Grenzwerten, ungültige Terme, extreme Gleichungen, jedes Preset, PDF an den Rändern; Footer-Test.
- **Layout:** Schnellstart oben in der Seitenleiste, fester Kopf, aktives Preset hervorgehoben; jede Änderung eines Reglers hebt die Markierung auf (`tests/test_layout.py`).
- **Browser:** Seitentext und Zahlen im frischen Tab mit festem Viewport (1100 × 800) geprüft (Binärbäume, n = 10), Diagrammbreite 630 px, Achsenbereiche sinnvoll.
- **Nicht gemacht:** Mutationstests (seit 2026-10-28 nicht mehr verlangt), Docker-Lauf der Linux-CI (Docker fehlt auf diesem Rechner; die CI nach dem Push entscheidet).

505 Tests (`pytest tests`), zuletzt in rund 90 Sekunden auf dem Entwicklungsrechner (Messung, nicht getestet).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Ergebnis, Gleichung, Kernfrage, fünf Experimente, Spielwiese, Grenzen, Formeln |
| `sym_algorithm.py` | Kern: Koeffizienten aus der Gleichung, Festpunkt, Aufzählen, Bruch, Diskriminante, Wachstum, Raten, Polynomhilfen |
| `sym_constants.py` | Regler-Grenzen, Schwellen, Farben, Presets |
| `sym_evaluation.py` | Kennzahlen, Experimente, Verdikte, Formatierung |
| `sym_layout.py` | Fester Kopf (Stylesheet) |
| `sym_pdf_export.py` | PDF der aktuellen Gleichung (fpdf2) |
| `sym_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben) |
| `sym_scenario.py` | Parser der Gleichung, Textformen, Zufallsspezifikationen |
| `sym_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Handwerte, Orakel, Eigenschaften, Randfälle, Verdikte, Claims, Presets, große Zahlen, Layout, AppTest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Mengen, Zyklen, beschriftete Strukturen, mehrere Sorten:** Stück 5 und 6.
- **Asymptotik** (Singularitätsanalyse, Konstanten wie 4ⁿ/(n^(3/2)·√π)): Stück 9; hier nur die Messung von Quotient und Exponent.
- **Gleichverteilt ziehen** aus der Gleichung: Stück 10.
- **Wurzelformel für k ≥ 3:** nur die Gleichung wird gezeigt.
- **Verwandte Zähler:** `random-spanning-tree-demo` (Spannbäume eines gegebenen Graphen über eine Determinante), Plan Lineare Erweiterungen, Kasteleyn, Permanente: anderes Ziel, nur Verweis.
- **Ein Computer-Algebra-System als zweiter Rechenweg:** nicht gebaut; die Gegenproben sind Aufzählen, Festpunktiteration, Bruchreihe und die geschlossene Lösung.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

Streamlit Cloud: Python-Version nach der Voreinstellung der Plattform (lokal `3.14`, CI `3.12`); der Code nutzt nur Merkmale, die in `3.12` laufen.

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und fpdf2.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
