# Aircraft Tracker Course

Курсовая работа: трекер самолётов (API, ООП, SOLID, pytest).

## Как работает
1. Название страны -> координаты границ (Nominatim, OpenStreetMap).
2. Координаты -> список бортов в воздушном пространстве (OpenSky Network).
3. Словари -> объекты Aeroplane с валидацией и инкапсуляцией.
4. Сохранение и загрузка в JSON (JSONSaver).
5. Интерактивное меню: просмотр, поиск по позывному,
   топ-N по высоте и скорости, статистика по странам.

## Запуск
```bash
pip install -r requirements.txt
python main.py
