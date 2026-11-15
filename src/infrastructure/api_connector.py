"""Коннекторы к внешним API: Nominatim (гео) и OpenSky Network (самолёты)."""

import requests

from src.interfaces.base_interfaces import APIConnectorInterface

# Nominatim требует корректный User-Agent, иначе отклоняет запросы
HEADERS = {"User-Agent": "AircraftTrackerCourse/1.0 (educational project)"}


class NominatimAPI(APIConnectorInterface):
    """
    Коннектор к Nominatim (OpenStreetMap).

    Возвращает координаты границ страны (boundingbox):
    южную, северную широту и западную, восточную долготу.

    Атрибут _cache — словарь-кэш: повторный запрос по той же стране
    не отправляет новый HTTP-запрос (Nominatim ограничивает частоту).
    """

    _URL = "https://nominatim.openstreetmap.org/search"

    def __init__(self) -> None:
        self._cache: dict[str, dict] = {}

    def get_data(self, country: str) -> dict:
        """Принимает название страны, возвращает dict с координатами границ."""
        if not isinstance(country, str) or not country.strip():
            raise ValueError("Название страны должно быть непустой строкой")

        country = country.strip()
        if country in self._cache:
            return self._cache[country]

        try:
            response = requests.get(
                self._URL,
                params={"q": country, "format": "json", "limit": 1},
                headers=HEADERS,
                timeout=10,
            )
            response.raise_for_status()
            results = response.json()
        except requests.exceptions.RequestException as error:
            raise ConnectionError(
                f"Не удалось получить координаты страны '{country}': {error}"
            ) from error

        if not results:
            raise ValueError(f"Страна '{country}' не найдена в Nominatim")

        # Nominatim отдаёт boundingbox строками в порядке:
        # [юг (lat), север (lat), запад (lon), восток (lon)]
        bbox = results[0]["boundingbox"]
        coords = {
            "lat_min": float(bbox[0]),
            "lat_max": float(bbox[1]),
            "lon_min": float(bbox[2]),
            "lon_max": float(bbox[3]),
        }
        self._cache[country] = coords
        return coords


class OpenSkyAPI(APIConnectorInterface):
    """
    Коннектор к OpenSky Network.

    По координатам границ получает список всех бортов,
    находящихся в данном воздушном прямоугольнике (в воздухе и на земле).
    """

    _URL = "https://opensky-network.org/api/states/all"

    def get_data(self, coords: dict) -> list[dict]:
        """Принимает границы страны, возвращает список словарей с самолётами."""
        params = {
            "lamin": coords["lat_min"],
            "lomin": coords["lon_min"],
            "lamax": coords["lat_max"],
            "lomax": coords["lon_max"],
        }
        try:
            response = requests.get(self._URL, params=params, timeout=15)
            response.raise_for_status()
            payload = response.json()
        except requests.exceptions.RequestException as error:
            raise ConnectionError(
                f"Не удалось получить данные о самолётах: {error}"
            ) from error

        # Если по региону данных нет, OpenSky возвращает states: null
        states = payload.get("states") or []
        return [self._parse_state(state) for state in states]

    @staticmethod
    def _parse_state(state: list) -> dict:
        """
        Превращает позиционный массив OpenSky в понятный словарь.

        Индексы по документации OpenSky:
        0 — icao24, 1 — callsign, 2 — origin_country,
        9 — velocity, 13 — geo_altitude.
        """
        callsign = (state[1] or "").strip()
        return {
            "icao24": state[0],
            "callsign": callsign if callsign else "unknown",
            "origin_country": state[2],
            "velocity": state[9],
            "geo_altitude": state[13],
        }


class AeroplanesAPI:
    """
    Фасад: объединяет два коннектора в один удобный интерфейс.

    Пример использования (как в задании):
        api = AeroplanesAPI()
        aeroplanes = api.get_aeroplanes("Spain")
    """

    def __init__(self) -> None:
        self._geo_api = NominatimAPI()
        self._sky_api = OpenSkyAPI()

    def get_aeroplanes(self, country: str) -> list[dict]:
        """
        Возвращает словари самолётов в воздушном пространстве страны.

        Борта с неполными данными (нет скорости или высоты) пропускаем:
        OpenSky часто присылает None по слабым транспондерам.
        """
        coords = self._geo_api.get_data(country)
        raw_states = self._sky_api.get_data(coords)

        aeroplanes: list[dict] = []
        for state in raw_states:
            if state["velocity"] is None or state["geo_altitude"] is None:
                continue
            aeroplanes.append(state)
        return aeroplanes
