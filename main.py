"""
Aircraft Tracker Course — главная точка входа.

Получает данные о самолётах в воздушном пространстве страны
через Nominatim + OpenSky Network, сохраняет в JSON,
позволяет искать, сортировать и выводить топ-N бортов.
"""

import sys

from src.application.business_logic import Aeroplane
from src.infrastructure.api_connector import AeroplanesAPI
from src.infrastructure.json_saver import JSONSaver

DATA_FILE = "data/aeroplanes.json"

MENU = """
================ aircraft-tracker ================
 1. Получить самолёты страны (API + сохранить)
 2. Загрузить самолёты из JSON-файла
 3. Показать все борта
 4. Поиск по позывному
 5. Топ-N по высоте (DESC)
 6. Топ-N по скорости (DESC)
 7. Статистика по странам
 0. Выход
==================================================
Выберите пункт меню: """


def planes_to_objects(data: list) -> list:
    """Словари -> объекты Aeroplane (битые записи пропускаются)."""
    return Aeroplane.cast_to_object_list(data)


def show_planes(planes: list) -> None:
    if not planes:
        print("\nДанных нет. Сначала получите самолёты (пункт 1 или 2).")
        return
    print(f"\n{'Позывной':<10} | {'Страна':<20} | "
          f"{'Скорость, м/с':>13} | {'Высота, м':>10}")
    print("-" * 70)
    for plane in planes:
        print(f"{plane.callsign:<10} | {plane.origin_country:<20} | "
              f"{plane.velocity:>13.1f} | {plane.geo_altitude:>10.1f}")
    print(f"\nВсего бортов: {len(planes)}")


def ask_n() -> int:
    """Запрашивает число N для топ-листа с защитой от опечаток."""
    raw = input("Сколько бортов показать (N): ").strip()
    try:
        n = int(raw)
        if n <= 0:
            raise ValueError
        return n
    except ValueError:
        print("Ошибка: нужно целое положительное число.")
        return 0


def main() -> None:
    api = AeroplanesAPI()
    planes: list = []

    while True:
        choice = input(MENU).strip()

        if choice == "1":
            country = input("Введите название страны (например, Spain): ").strip()
            if not country:
                print("Название страны не может быть пустым.")
                continue
            try:
                print("\nЗапрос к API...")
                data = api.get_aeroplanes(country)
            except (ConnectionError, ValueError) as error:
                # Сетевые сбои и опечатки в стране не роняют программу
                print(f"Ошибка: {error}")
                continue
            print(f"Получено бортов с полными данными: {len(data)}")
            JSONSaver.save(data, DATA_FILE)
            print(f"Данные сохранены в {DATA_FILE}")
            planes = planes_to_objects(data)

        elif choice == "2":
            data = JSONSaver.load(DATA_FILE)
            planes = planes_to_objects(data)
            print(f"Загружено из файла {len(planes)} бортов "
                  f"(файл: {DATA_FILE})")

        elif choice == "3":
            show_planes(planes)

        elif choice == "4":
            query = input("Введите позывной или его часть: ").strip().lower()
            found = [p for p in planes if query in p.callsign.lower()]
            show_planes(found)

        elif choice == "5":
            n = ask_n()
            if n:
                show_planes(sorted(planes, reverse=True)[:n])

        elif choice == "6":
            n = ask_n()
            if n:
                show_planes(sorted(planes, key=lambda p: p.velocity,
                                   reverse=True)[:n])

        elif choice == "7":
            if not planes:
                print("\nДанных нет. Сначала получите самолёты.")
                continue
            stats: dict = {}
            for plane in planes:
                stats[plane.origin_country] = stats.get(plane.origin_country, 0) + 1
            print("\nСтрана -> количество бортов:")
            for country, count in sorted(stats.items(),
                                         key=lambda item: item[1],
                                         reverse=True):
                print(f"  {country:<25} {count:>4}")

        elif choice == "0":
            print("Пока! Хороших полётов 🛫")
            break

        else:
            print("Такого пункта нет — введите число от 0 до 7.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Ctrl+C — штатный способ выйти, а не повод для трейсбека
        print("\nПрервано пользователем.")
        sys.exit(0)
