"""Тесты JSONSaver: сохранение, загрузка, устойчивость к ошибкам."""

import json

import pytest

from src.infrastructure.json_saver import JSONSaver


def test_save_and_load_roundtrip(tmp_path):
    """Записали — прочитали — данные совпали."""
    filepath = tmp_path / "data" / "planes.json"
    data = [
        {"icao24": "a1", "callsign": "TST1", "origin_country": "Spain",
         "velocity": 200.0, "geo_altitude": 9000.0},
        {"icao24": "b2", "callsign": "TST2", "origin_country": "France",
         "velocity": 210.0, "geo_altitude": 11000.0},
    ]
    JSONSaver.save(data, str(filepath))
    loaded = JSONSaver.load(str(filepath))
    assert loaded == data


def test_save_creates_missing_folder(tmp_path):
    """Папки нет — save сам её создаёт."""
    filepath = tmp_path / "новая_папка" / "out.json"
    JSONSaver.save([{"k": "v"}], str(filepath))
    assert filepath.exists()


def test_cyrillic_stays_readable(tmp_path):
    """ensure_ascii=False: кириллица не превращается в \\u04xx."""
    filepath = tmp_path / "ru.json"
    JSONSaver.save([{"country": "Россия"}], str(filepath))
    text = filepath.read_text(encoding="utf-8")
    assert "Россия" in text


def test_load_missing_file_returns_empty_list(tmp_path):
    """Файла нет — получаем пустой список, а не падение."""
    assert JSONSaver.load(str(tmp_path / "нет_файла.json")) == []
