import asyncio

from db import get_db_session
from models import CityModel
from services.city_service import CityService

tasks: dict[int, asyncio.Task] = {}


async def periodic_weather_update(city_id: int):
    """Обновление погоды для города каждые 15 минут."""
    while True:
        await asyncio.sleep(15)  # 15 минут
        print(f"Обновляем погоду для города ID {city_id}")

        with get_db_session() as db:
            try:
                city = db.query(CityModel).get(city_id)
                if not city:
                    print(f"Город ID {city_id} удалён. "
                          "Останавливаем обновление.")
                    break

                city_service = CityService(db, city)
                city_service.refresh_weather_records_for_city()
                db.commit()
            except Exception as e:
                print(f"Ошибка при обновлении погоды: {e}")
                db.rollback()

    tasks.pop(city_id, None)


async def create_periodic_weather_update_task(city_id: int):
    """Создание задачи для периодического обновления погоды для города."""
    if city_id in tasks:
        print(f"Задача для города ID {city_id} уже существует.")
        return

    task = asyncio.create_task(periodic_weather_update(city_id))
    tasks[city_id] = task
