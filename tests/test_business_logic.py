"""Тесты класса Aeroplane: валидация, сравнение, сериализация."""

import pytest

from src.application.business_logic import Aeroplane


@pytest.fixture
def plane() -> Aeroplane:
    """Готовый объект для тестов."""
    return Aeroplane("abc123", "UAL1621", "United States", 250.0, 10000.0)


# --- Создание и валидация -------------------------------------------------

def test_create_valid_plane(plane):
    assert plane.icao24 == "abc123"
    assert plane.callsign == "UAL1621"
    assert plane.velocity == 250.0
    assert plane.geo_altitude == 10000.0


def test_empty_icao_raises_error():
    with pytest.raises(ValueError):
        Aeroplane("   ", "UAL1621", "USA", 250.0, 10000.0)


def test_negative_velocity_raises_error():
    with pytest.raises(ValueError):
        Aeroplane("abc123", "UAL1621", "USA", -50.0, 10000.0)


def test_none_altitude_raises_error():
    with pytest.raises(ValueError):
        Aeroplane("abc123", "UAL1621", "USA", 250.0, None)


def test_non_numeric_velocity_raises_error():
    with pytest.raises(TypeError):
        Aeroplane("abc123", "UAL1621", "USA", "быстро", 10000.0)


def test_bool_velocity_raises_error():
    # bool — это подкласс int, но скорость True не имеет смысла
    with pytest.raises(TypeError):
        Aeroplane("abc123", "UAL1621", "USA", True, 10000.0)


def test_empty_country_raises_error():
    with pytest.raises(ValueError):
        Aeroplane("abc123", "UAL1621", "", 250.0, 10000.0)


# --- Сравнение ------------------------------------------------------------

def test_comparison_by_altitude():
    low = Aeroplane("aaa", "LOW01", "Spain", 200.0, 1000.0)
    high = Aeroplane("bbb", "HGH01", "Spain", 300.0, 11000.0)
    assert high > low
    assert low < high


def test_equality_by_icao24():
    p1 = Aeroplane("xyz", "CALL1", "France", 200.0, 5000.0)
    p2 = Aeroplane("xyz", "CALL2", "Germany", 300.0, 9000.0)
    assert p1 == p2  # тот же борт, даже если данные другие


def test_sorting_desc_by_altitude():
    planes = [
        Aeroplane("a", "P1", "Spain", 200.0, 5000.0),
        Aeroplane("b", "P2", "Spain", 210.0, 11000.0),
        Aeroplane("c", "P3", "Spain", 220.0, 8000.0),
    ]
    sorted_planes = sorted(planes, reverse=True)
    assert [p.callsign for p in sorted_planes] == ["P2", "P3", "P1"]


# --- Сериализация ----------------------------------------------------------

def test_to_dict_and_back(plane):
    data = plane.to_dict()
    restored = Aeroplane.from_dict(data)
    assert restored == plane


def test_from_dict_with_none_callsign():
    data = {
        "icao24": "abc",
        "callsign": None,
        "origin_country": "Spain",
        "velocity": 200.0,
        "geo_altitude": 9000.0,
    }
    plane = Aeroplane.from_dict(data)
    assert plane.callsign == "unknown"


def test_cast_to_object_list_skips_bad_records():
    data = [
        {"icao24": "a", "callsign": "OK1", "origin_country": "Spain",
         "velocity": 200.0, "geo_altitude": 9000.0},
        {"icao24": "b", "callsign": "BAD", "origin_country": "Spain",
         "velocity": None, "geo_altitude": 9000.0},  # битая запись
    ]
    planes = Aeroplane.cast_to_object_list(data)
    assert len(planes) == 1
    assert planes[0].callsign == "OK1"
