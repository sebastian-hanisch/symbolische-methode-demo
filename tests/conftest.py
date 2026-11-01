"""Gemeinsame Fixtures: die Mini-Instanzen, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def binary():
    """Binärbäume F = 1 + z·F². Handrechnung: a(0) = 1; a(1) = [z⁰]F² = 1; a(2) = [z¹]F² = 2·a(0)·a(1) = 2; a(3) = [z²]F² = 2·a(0)·a(2) + a(1)² = 5; a(4) = 2·a(0)·a(3) + 2·a(1)·a(2) = 14."""
    return {(1, 2): 1}


@pytest.fixture
def motzkin():
    """Motzkin-Pfade F = 1 + z·F + z²·F². Handrechnung: a(3) = [z²]F + [z¹]F² = a(2) + 2·a(0)·a(1) = 2 + 2 = 4."""
    return {(1, 1): 1, (2, 2): 1}


@pytest.fixture
def fibonacci():
    """Wörter aus Schritten der Länge 1 und 2: F = 1 + z·F + z²·F, F = 1/(1 − z − z²), die Fibonacci-Zahlen 1, 1, 2, 3, 5, 8."""
    return {(1, 1): 1, (2, 1): 1}
