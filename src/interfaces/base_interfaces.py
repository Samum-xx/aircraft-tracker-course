"""Абстрактные интерфейсы (контракты) для работы с внешними API."""

from abc import ABC, abstractmethod
from typing import Any


class APIConnectorInterface(ABC):
    """
    Абстрактный класс коннектора к внешнему API.

    Наследники обязаны реализовать метод get_data —
    сами детали запроса каждый коннектор решает по-своему.
    Это принцип SOLID: зависимость от абстракции, а не от реализации.
    """

    @abstractmethod
    def get_data(self, *args, **kwargs) -> Any:
        """Получить данные от внешнего API и вернуть их в удобном виде."""
