"""Хранилище данных о самолётах: абстрактный класс и JSON-реализация."""

import json
from abc import ABC, abstractmethod
from pathlib import Path


class FileSaverInterface(ABC):
    """
    Абстрактное хранилище данных о самолётах.

    Наследники (JSONSaver, а в будущем CSVSaver или коннектор к БД)
    обязаны реализовать добавление, получение по критериям и удаление.
    """

    @abstractmethod
    def add_aeroplanes(self, aeroplanes: list[dict]) -> None:
        """Добавить самолёты в хранилище (дубли по icao24 пропускаются)."""

    @abstractmethod
    def get_data(self, **criteria) -> list[dict]:
        """Получить данные по критериям: country, min_altitude, max_altitude."""

    @abstractmethod
    def delete_aeroplanes(self, icao24_list: list[str]) -> int:
        """Удалить самолёты по списку icao24, вернуть число удалённых."""


class JSONSaver(FileSaverInterface):
    """Сохранение информации о самолётах в JSON-файл."""

    def __init__(self, filepath: str = "data/aeroplanes.json") -> None:
        self._filepath = Path(filepath)

    # --- внутренние методы чтения/записи файла -----------------------------

    def _load_all(self) -> list[dict]:
        if not self._filepath.exists():
            return []
        try:
            with self._filepath.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError:
            # Повреждённый файл не должен ронять программу
            return []
        return data if isinstance(data, list) else []

    def _save_all(self, data: list[dict]) -> None:
        self._filepath.parent.mkdir(parents=True, exist_ok=True)
        with self._filepath.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    # --- реализация абстрактных методов ------------------------------------

    def add_aeroplanes(self, aeroplanes: list[dict]) -> None:
        """Добавляет борта в файл. Повторный icao24 не дублируется."""
        existing = self._load_all()
        known = {item.get("icao24") for item in existing}
        added = 0
        for item in aeroplanes:
            if isinstance(item, dict) and item.get("icao24") not in known:
                existing.append(item)
                known.add(item.get("icao24"))
                added += 1
        self._save_all(existing)
        return added

    def get_data(self, **criteria) -> list[dict]:
        """Получает данные из файла по критериям.

        Поддерживаются: country (точное совпадение),
        min_altitude и max_altitude (границы высоты, метры).
        """
        data = self._load_all()
        country = criteria.get("country")
        min_alt = criteria.get("min_altitude")
        max_alt = criteria.get("max_altitude")

        result = []
        for item in data:
            if country and item.get("origin_country") != country:
                continue
            altitude = item.get("geo_altitude")
            if min_alt is not None and (altitude is None or altitude < min_alt):
                continue
            if max_alt is not None and (altitude is None or altitude > max_alt):
                continue
            result.append(item)
        return result

    def delete_aeroplanes(self, icao24_list: list[str]) -> int:
        """Удаляет борта по списку icao24. Возвращает число удалённых."""
        to_delete = set(icao24_list or [])
        if not to_delete:
            return 0
        existing = self._load_all()
        kept = [item for item in existing if item.get("icao24") not in to_delete]
        removed = len(existing) - len(kept)
        if removed:
            self._save_all(kept)
        return removed

    # --- заглушки на будущее (пригодятся при интеграции с БД) ---------------

    def update_aeroplane(self, icao24: str, changes: dict) -> None:
        """Заглушка: изменение записи понадобится при работе с БД."""
        pass
