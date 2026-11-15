"""
Aircraft Tracker Course — главная точка входа.

Получает данные о самолётах в воздушном пространстве страны
через Nominatim + OpenSky Network, сохраняет в JSON,
позволяет фильтровать по стране и высоте, выводить топ-N бортов.
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
 4. Фильтр по стране регистрации
 5. Фильтр по диапазону высот
 6. Топ-N по высоте (DESC)
 7. Топ-N по скорости (DESC)
 8. Статистика по странам
 9. Удалить борт по позывному (из файла)
 0. Выход
==================================================
Выберите пункт меню: """


def planes_to_objects(data: list) -> list:
    """Словари -> объекты Aeroplane (битые записи пропускаются)."""
    return Aeroplane.cast_to_object_list(data)


def show_planes(planes: list) -> None:
    if not planes:
        print("\nДанных нет (или фильтр ничего не нашёл).")
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


def filter_aeroplanes(aeroplanes: list, filter_words: list[str]) -> list:
    """Фильтрует самолёты по стране регистрации (вхождение подстроки)."""
    words = [w.strip().lower() for w in filter_words if w.strip()]
    if not words:
        return aeroplanes
    return [p for p in aeroplanes
            if any(w in p.origin_country.lower() for w in words)]


def get_aeroplanes_by_altitude(aeroplanes: list, altitude_range: str) -> list:
    """Фильтрует самолёты по диапазону высот, пример ввода: 5000 - 12000."""
    try:
        left, right = altitude_range.replace("–", "-").split("-")
        low, high = float(left.strip()), float(right.strip())
    except ValueError:
        print("Ошибка: диапазон задайте как 'минимум - максимум', "
              "например 5000 - 12000")
        return []
    if low > high:
        low, high = high, low
    return [p for p in aeroplanes if low <= p.geo_altitude <= high]


def main() -> None:
    api = AeroplanesAPI()
    saver = JSONSaver(DATA_FILE)
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
            saver.add_aeroplanes(data)
            print(f"Данные добавлены в {DATA_FILE}")
            planes = planes_to_objects(saver.get_data())

        elif choice == "2":
            data = saver.get_data()
            planes = planes_to_objects(data)
            print(f"Загружено из файла {len(planes)} бортов "
                  f"(файл: {DATA_FILE})")

        elif choice == "3":
            show_planes(planes)

        elif choice == "4":
            words = input("Введите страны для фильтрации (через пробел): ").split()
            show_planes(filter_aeroplanes(planes, words))

        elif choice == "5":
            alt_range = input("Введите диапазон высот (например, 5000 - 12000): ")
            show_planes(get_aeroplanes_by_altitude(planes, alt_range))

        elif choice == "6":
            n = ask_n()
            if n:
                show_planes(sorted(planes, reverse=True)[:n])

        elif choice == "7":
            n = ask_n()
            if n:
                show_planes(sorted(planes, key=lambda p: p.velocity,
                                   reverse=True)[:n])

        elif choice == "8":
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

        elif choice == "9":
            query = input("Введите позывной борта для удаления: ").strip().lower()
            icao_list = [p.icao24 for p in planes if query in p.callsign.lower()]
            if not icao_list:
                print("Борта с таким позывным не найдены.")
            else:
                removed = saver.delete_aeroplanes(icao_list)
                print(f"Удалено бортов: {removed}")
                planes = planes_to_objects(saver.get_data())

        elif choice == "0":
            print("Пока! Хороших полётов 🛫")
            break

        else:
            print("Такого пункта нет — введите число от 0 до 9.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Ctrl+C — штатный способ выйти, а не повод для трейсбека
        print("\nПрервано пользователем.")
        sys.exit(0)
