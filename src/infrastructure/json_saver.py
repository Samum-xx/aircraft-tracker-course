"""Модуль для сохранения и загрузки данных о самолётах в JSON."""

import json
from pathlib import Path
from typing import List, Dict, Any


class JSONSaver:
    """
    Абстрактный интерфейс для сохранения данных.

    В рамках задания реализуем конкретный класс JSONSaver,
    который умеет писать и читать JSON-файлы.
    """

    @staticmethod
    def save(data: List[Dict[str, Any]], filepath: str) -> None:
        """
        Сохраняет список словарей в JSON-файл.

        data: список словарей (например, результат api.get_aeroplanes)
        filepath: путь к файлу, например 'data/planes.json'
        """
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("w", encoding="utf-8") as f:
            # ensure_ascii=False, чтобы русские буквы не превращались в \u04xx
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def load(filepath: str) -> List[Dict[str, Any]]:
        """Загружает список словарей из JSON-файла."""
        path = Path(filepath)

        if not path.exists():
            return []

        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                return []
            return data
