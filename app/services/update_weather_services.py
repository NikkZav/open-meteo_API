import asyncio
from schemas.city import City
from repositories.db import get_db_session
from repositories.city_repository import CityRepository
from repositories.weather_repository import WeatherRepository
from utils.exceptions import CityNotFoundError, OpenMeteoAPIError


tasks: dict[int, asyncio.Task] = {}


async def periodic_weather_update(city: City) -> None:
    """
    Фоновое обновление погоды для города каждые 15 минут.
    """
    while True:
        await asyncio.sleep(15)  # 15 минут (для тестирования 15сек)
        print(f"Обновляем погоду для города ID {city.id}")

        with get_db_session() as db:
            # Получаем репозитории
            weather_repo = WeatherRepository(db)
            city_repo = CityRepository(db)
            try:
                new_weather_records = \
                    weather_repo.get_weather_records_by_coord(city.coordinates)
                city_repo.update_weather_records(city.id, new_weather_records)
            except OpenMeteoAPIError:
                print("Ошибка при получении погоды ")
            except CityNotFoundError:
                print(f"Город с ID {city.id} не найден")
                break  # Завершаем цикл, если город удалён
            except Exception as e:
                print(f"Ошибка: {e}")

    tasks.pop(city.id, None)


def create_periodic_weather_update_task(city: City) -> None:
    """Создание задачи для периодического обновления погоды для города."""
    if city.id in tasks:
        print(f"Задача для города ID {city.id} уже существует.")
        return
    task = asyncio.create_task(periodic_weather_update(city))
    tasks[city.id] = task
