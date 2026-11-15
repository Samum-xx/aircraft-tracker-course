from src.infrastructure.api_connector import AeroplanesAPI
from src.application.business_logic import Aeroplane

api = AeroplanesAPI()

# Первый запрос — реальный поход в Nominatim и OpenSky
aeroplanes = api.get_aeroplanes("Spain")
print(f"Найдено бортов с полными данными: {len(aeroplanes)}")

# Второй запрос той же страны — берётся из кэша, быстро
objects = Aeroplane.cast_to_object_list(aeroplanes)

# Топ-3 по высоте (DESC, как требует задание)
top = sorted(objects, reverse=True)[:3]
for plane in top:
    print(plane)
