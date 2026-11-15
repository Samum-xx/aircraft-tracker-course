"""Класс Aeroplane — модель самолёта с инкапсуляцией и валидацией данных."""

import numbers


class Aeroplane:
    """
    Информация о самолёте, полученная от API OpenSky Network.

    Атрибуты инкапсулированы (сделаны приватными) и доступны
    только через свойства (@property / @setter) с валидацией.

    Атрибуты:
        icao24: уникальный бортовой идентификатор (hex-код транспондера).
        callsign: позывной борта, например "UAL1621".
        origin_country: страна регистрации самолёта.
        velocity: скорость полёта, м/с.
        geo_altitude: высота полёта над уровнем моря (WGS-84), метры.
    """

    def __init__(self,
                 icao24: str,
                 callsign: str,
                 origin_country: str,
                 velocity: float,
                 geo_altitude: float) -> None:
        # Строковые поля проверяются до присвоения
        self.icao24 = icao24
        self.callsign = callsign
        self.origin_country = origin_country
        # Числовые поля проходят валидацию в сеттерах
        self.velocity = velocity
        self.geo_altitude = geo_altitude

    # ------------------------------------------------------------------
    # Валидация и инкапсуляция
    # ------------------------------------------------------------------

    @staticmethod
    def _validate_text(value: object, field_name: str) -> str:
        """Проверяет, что значение — непустая строка."""
        if not isinstance(value, str):
            raise TypeError(
                f"Поле '{field_name}' должно быть строкой, "
                f"получен {type(value).__name__}"
            )
        value = value.strip()
        if not value:
            raise ValueError(f"Поле '{field_name}' не может быть пустым")
        return value

    @staticmethod
    def _validate_number(value: object, field_name: str) -> float:
        """
        Проверяет, что значение — число (не отрицательное).

        OpenSky иногда присылает None вместо числа (данных нет),
        поэтому None считаем некорректным значением и сообщаем об этом явно.
        """
        if value is None:
            raise ValueError(
                f"Поле '{field_name}' не получено от API (None)"
            )
        if not isinstance(value, numbers.Number) or isinstance(value, bool):
            raise TypeError(
                f"Поле '{field_name}' должно быть числом, "
                f"получен {type(value).__name__}"
            )
        if value < 0:
            raise ValueError(
                f"Поле '{field_name}' не может быть отрицательным: {value}"
            )
        return float(value)

    # icao24 ------------------------------------------------------------

    @property
    def icao24(self) -> str:
        return self._icao24

    @icao24.setter
    def icao24(self, value: str) -> None:
        self._icao24 = self._validate_text(value, "icao24")

    # callsign ----------------------------------------------------------

    @property
    def callsign(self) -> str:
        return self._callsign

    @callsign.setter
    def callsign(self, value: str) -> None:
        self._callsign = self._validate_text(value, "callsign")

    # origin_country ------------------------------------------------------

    @property
    def origin_country(self) -> str:
        return self._origin_country

    @origin_country.setter
    def origin_country(self, value: str) -> None:
        self._origin_country = self._validate_text(value, "origin_country")

    # velocity ------------------------------------------------------------

    @property
    def velocity(self) -> float:
        return self._velocity

    @velocity.setter
    def velocity(self, value: float) -> None:
        self._velocity = self._validate_number(value, "velocity")

    # geo_altitude ---------------------------------------------------------

    @property
    def geo_altitude(self) -> float:
        return self._geo_altitude

    @geo_altitude.setter
    def geo_altitude(self, value: float) -> None:
        self._geo_altitude = self._validate_number(value, "geo_altitude")

    # ------------------------------------------------------------------
    # Сравнение по скорости и высоте (для сортировки)
    # ------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self.icao24 == other.icao24

    def __hash__(self) -> int:
        """Позволяет хранить самолёты в set и использовать как ключи dict."""
        return hash(self.icao24)

    def __lt__(self, other: object) -> bool:
        """Самолёт меньше другого, если летит ниже."""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self.geo_altitude < other.geo_altitude

    def __gt__(self, other: object) -> bool:
        """Самолёт больше другого, если летит выше."""
        if not isinstance(other, Aeroplane):
            return NotImplemented
        return self.geo_altitude > other.geo_altitude

    def faster_than(self, other: "Aeroplane") -> bool:
        """Сравнение по скорости (дополнительно к высоте)."""
        return self.velocity > other.velocity

    def slower_than(self, other: "Aeroplane") -> bool:
        return self.velocity < other.velocity

    # ------------------------------------------------------------------
    # Сериализация: объект <-> dict (для сохранения в JSON)
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        """Превращает объект в словарь — удобно для json.dump()."""
        return {
            "icao24": self.icao24,
            "callsign": self.callsign,
            "origin_country": self.origin_country,
            "velocity": self.velocity,
            "geo_altitude": self.geo_altitude,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Aeroplane":
        """
        Создаёт объект Aeroplane из словаря (например, из JSON-файла).

        Особенность API OpenSky: вместо числа может прийти None,
        а позывной бывает пустой строкой или строкой из пробелов.
        В таких случаях подставляем заглушку "unknown" / 0.0 вместо
        падения с ошибкой, чтобы не терять запись целиком.
        """
        if not isinstance(data, dict):
            raise TypeError("Данные должны быть словарём")

        def get_number(key: str) -> float:
            value = data.get(key)
            return 0.0 if value is None else value

        callsign = data.get("callsign") or "unknown"
        origin_country = data.get("origin_country") or "unknown"

        return cls(
            icao24=data["icao24"],
            callsign=callsign,
            origin_country=origin_country,
            velocity=get_number("velocity"),
            geo_altitude=get_number("geo_altitude"),
        )

    @classmethod
    def cast_to_object_list(cls, data: list[dict]) -> list["Aeroplane"]:
        """
        Создаёт список объектов Aeroplane из списка словарей.

        Записи без icao24 или с некорректными типами полей пропускаются —
        их невозможно корректно преобразовать в объект.
        """
        aeroplanes: list["Aeroplane"] = []
        for item in data:
            try:
                aeroplanes.append(cls.from_dict(item))
            except (TypeError, ValueError, KeyError):
                continue
        return aeroplanes

    # ------------------------------------------------------------------
    # Представление в виде строки
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        return (
            f"{self.callsign:<10} | {self.origin_country:<15} | "
            f"скорость: {self.velocity:>8.1f} м/с | "
            f"высота: {self.geo_altitude:>9.1f} м"
        )

    def __repr__(self) -> str:
        return (
            f"Aeroplane(icao24={self.icao24!r}, callsign={self.callsign!r}, "
            f"origin_country={self.origin_country!r}, "
            f"velocity={self.velocity!r}, geo_altitude={self.geo_altitude!r})"
        )
