import asyncio
from sqlalchemy.orm import Session
from services.city_service import CityService, get_city_or_none
from models import CityModel


tasks = {}


async def periodic_weather_update(city: CityModel, db: Session):
    """Обновление погоды для города каждые 15 минут."""
    city_service = CityService(db, city)
    while True:
        if not get_city_or_none(city.id, db):
            print(f"Город ID {city.id} удалён. Останавливаем обновление.")
            break
        await asyncio.sleep(60)  # 15 минут
        print(f"Обновляем погоду для города ID {city.id}")
        city_service.add_weather_to_city()


async def create_periodic_weather_update_task(city: CityModel, db: Session):
    """Создание задачи для периодического обновления погоды для города."""
    tasks[city.id] = asyncio.create_task(
        periodic_weather_update(city, db)
    )
