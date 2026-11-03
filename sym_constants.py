"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

DEFAULT_SPEC = "z F^2"                       # Binärbäume: F = 1 + z·F², die Catalan-Zahlen
SPEC_TEXT_MAX = 80                           # längere Eingaben aus der Adresszeile werden abgeschnitten
N_MIN, N_MAX, DEFAULT_N = 1, 100, 10         # Größe n; die Online-Rechnung kostet O(K·n²) große Ganzzahlen
MAX_TERMS, MAX_J, MAX_K, MAX_COEF = 6, 12, 4, 9   # Terme, Zahl der Atome z^j, Potenz F^k, Farben (Koeffizient)

CHECK_FIXPOINT_N = 12                        # bis hierher prüft die App die Reihe durch Festpunktiteration
CHECK_ENUM_N = 7                             # bis hierher prüft die App durch Aufzählen der Strukturen ...
ENUM_COUNT_CAP = 30000                       # ... solange es höchstens so viele Strukturen gibt
ENUM_SHOW_N = 5                              # größte Größe, für die die App Strukturen als Text auflistet
ENUM_SHOW_COUNT = 24                         # höchstens so viele Strukturen werden aufgelistet
GUESS_RMAX = 12                              # größte Ordnung, die das Raten (Stück 1) versucht
GUESS_TERMS = 80                             # so viele Glieder prüft das Raten
GROWTH_N = 400                               # so weit wird der Quotient a(n + p)/a(n) für das Wachstum gerechnet
ERROR_N = 60                                 # so weit zeigt das Diagramm den Quotientenfehler
GROWTH_TOL = 0.02                            # relative Genauigkeit des Quotienten bei n = GROWTH_N, bis zu der das Wachstum als bestätigt gilt
CLASS_SETS = 300                             # Zahl der Zufallsspezifikationen in Experiment 5
CLASS_SEED_BASE = 5000                       # feste Seeds: nie eine einzelne Spezifikation als Befund
CLASS_ENUM_N = 6                             # Aufzählen der Strukturen in Experiment 5 bis zu dieser Größe (und höchstens ENUM_COUNT_CAP Strukturen)
CLASS_SERIES_N = 90                          # Glieder für das Raten in Experiment 5
AMBIGUITY_N = 8                              # größte Länge der Tabelle zur mehrdeutigen Grammatik
CATALAN_IDENTITY_N = 200                     # (n + 2)·C(n+1) = 2·(2n + 1)·C(n) wird bis hierher live geprüft
SEED_MAX, DEFAULT_SEED = 999999, 35

COLOR_SERIES = "#2F6B65"
COLOR_REF = "rgba(150,150,150,0.75)"
COLOR_ERROR = "#c0504d"
COLOR_LINE = "#4c78a8"

PRESETS = {
    "Binärbäume (Catalan)": {"spec": "z F^2", "n": 10},
    "Motzkin-Pfade": {"spec": "z F + z^2 F^2", "n": 10},
    "Schröder (groß)": {"spec": "z F + z F^2", "n": 10},
    "Ternäre Bäume": {"spec": "z F^3", "n": 10},
    "Fibonacci-Wörter": {"spec": "z F + z^2 F", "n": 10},
    "Wörter über 3 Buchstaben": {"spec": "3 z F", "n": 10},
    "Kompositionen mit Teilen 1 bis 3": {"spec": "z F + z^2 F + z^3 F", "n": 10},
    "Nur gerade Größen": {"spec": "z^2 F^2", "n": 10},
}
PRESET_HELP = {
    "Binärbäume (Catalan)": "Ein Binärbaum ist leer oder ein Atom mit zwei Binärbäumen: F = 1 + z·F². Die Zahlen sind die Catalan-Zahlen 1, 1, 2, 5, 14, 42. Verschachtelt, also nicht rational.",
    "Motzkin-Pfade": "F = 1 + z·F + z²·F²: Ein Pfad hat einen flachen Schritt oder einen Berg mit zwei Teilpfaden. Verschachtelt.",
    "Schröder (groß)": "F = 1 + z·F + z·F²: dieselben Atome, aber drei Fälle je Atom. Verschachtelt.",
    "Ternäre Bäume": "F = 1 + z·F³: jeder Knoten hat drei Teilbäume. Verschachtelt.",
    "Fibonacci-Wörter": "F = 1 + z·F + z²·F: eine Folge aus Schritten der Länge 1 und 2. Linear, die Zahlen sind die Fibonacci-Zahlen (derselbe Nenner wie in Stück 2, die Folge um einen Index verschoben).",
    "Wörter über 3 Buchstaben": "F = 1 + 3z·F: ein Buchstabe aus drei, dann ein Wort. Linear, 3ⁿ Wörter.",
    "Kompositionen mit Teilen 1 bis 3": "F = 1 + z·F + z²·F + z³·F: Zerlegungen von n in Summanden 1, 2 und 3 mit Reihenfolge. Linear.",
    "Nur gerade Größen": "F = 1 + z²·F²: alle Größen sind Vielfache von 2, ungerade Größen gibt es nicht. Zeigt die Periode.",
}

CLASS_QUOTIENT_N = 200                       # Quotient a(n + p)/a(n) bei dieser Größe (Vielfaches der Periode) in Experiment 5
