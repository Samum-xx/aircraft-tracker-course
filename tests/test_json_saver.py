"""Тесты JSONSaver: добавление, получение по критериям, удаление."""

import pytest

from src.infrastructure.json_saver import JSONSaver


@pytest.fixture
def saver(tmp_path):
    return JSONSaver(str(tmp_path / "data" / "planes.json"))


PLANES = [
    {"icao24": "a1", "callsign": "TST1", "origin_country": "Spain",
     "velocity": 200.0, "geo_altitude": 9000.0},
    {"icao24": "b2", "callsign": "TST2", "origin_country": "France",
     "velocity": 210.0, "geo_altitude": 11000.0},
]


def test_add_and_get_all(saver):
    saver.add_aeroplanes(PLANES)
    assert len(saver.get_data()) == 2


def test_add_skips_duplicates(saver):
    saver.add_aeroplanes(PLANES)
    saver.add_aeroplanes(PLANES)  # повтор — дублей быть не должно
    assert len(saver.get_data()) == 2


def test_get_data_by_country(saver):
    saver.add_aeroplanes(PLANES)
    result = saver.get_data(country="Spain")
    assert len(result) == 1
    assert result[0]["icao24"] == "a1"


def test_get_data_by_altitude_range(saver):
    saver.add_aeroplanes(PLANES)
    result = saver.get_data(min_altitude=10000)
    assert [item["icao24"] for item in result] == ["b2"]


def test_delete_removes_and_counts(saver):
    saver.add_aeroplanes(PLANES)
    removed = saver.delete_aeroplanes(["a1"])
    assert removed == 1
    assert [item["icao24"] for item in saver.get_data()] == ["b2"]


def test_delete_missing_returns_zero(saver):
    saver.add_aeroplanes(PLANES)
    assert saver.delete_aeroplanes(["zzz"]) == 0
    assert len(saver.get_data()) == 2


def test_delete_empty_list_returns_zero(saver):
    saver.add_aeroplanes(PLANES)
    assert saver.delete_aeroplanes([]) == 0


def test_cyrillic_stays_readable(tmp_path):
    saver = JSONSaver(str(tmp_path / "ru.json"))
    saver.add_aeroplanes([{"icao24": "c3", "callsign": "RUS1",
                           "origin_country": "Россия", "velocity": 200.0,
                           "geo_altitude": 9000.0}])
    text = (tmp_path / "ru.json").read_text(encoding="utf-8")
    assert "Россия" in text


def test_corrupted_file_returns_empty(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{битый json", encoding="utf-8")
    saver = JSONSaver(str(path))
    assert saver.get_data() == []


def test_missing_folder_created(tmp_path):
    saver = JSONSaver(str(tmp_path / "новая" / "out.json"))
    saver.add_aeroplanes([{"icao24": "k", "callsign": "X",
                           "origin_country": "Spain", "velocity": 1.0,
                           "geo_altitude": 2.0}])
    assert (tmp_path / "новая" / "out.json").exists()
