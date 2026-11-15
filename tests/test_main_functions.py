"""Тесты функций фильтрации из main.py."""

import pytest

from main import filter_aeroplanes, get_aeroplanes_by_altitude
from src.application.business_logic import Aeroplane


def make(icao: str, country: str, vel: float, alt: float) -> Aeroplane:
    return Aeroplane(icao, f"FL{icao}", country, vel, alt)


PLANES = [
    make("a", "Spain", 200.0, 9000.0),
    make("b", "France", 250.0, 11000.0),
    make("c", "United States", 220.0, 5000.0),
]


class TestFilterAeroplanes:

    def test_filter_by_country(self):
        result = filter_aeroplanes(PLANES, ["Spain"])
        assert [p.icao24 for p in result] == ["a"]

    def test_filter_case_insensitive(self):
        result = filter_aeroplanes(PLANES, ["france"])
        assert [p.icao24 for p in result] == ["b"]

    def test_filter_multiple_words(self):
        result = filter_aeroplanes(PLANES, ["Spain", "France"])
        assert [p.icao24 for p in result] == ["a", "b"]

    def test_empty_words_returns_all(self):
        assert filter_aeroplanes(PLANES, []) == PLANES

    def test_no_match_returns_empty(self):
        assert filter_aeroplanes(PLANES, ["Германия"]) == []


class TestGetAeroplanesByAltitude:

    def test_normal_range(self):
        result = get_aeroplanes_by_altitude(PLANES, "6000 - 10000")
        assert [p.icao24 for p in result] == ["a"]

    def test_bounds_reversed_swaps(self):
        result = get_aeroplanes_by_altitude(PLANES, "10000 - 6000")
        assert [p.icao24 for p in result] == ["a"]

    def test_invalid_string_returns_empty(self, capsys):
        result = get_aeroplanes_by_altitude(PLANES, "высоко")
        assert result == []
        assert "Ошибка" in capsys.readouterr().out

    def test_boundaries_included(self):
        result = get_aeroplanes_by_altitude(PLANES, "9000 - 11000")
        assert [p.icao24 for p in result] == ["a", "b"]
