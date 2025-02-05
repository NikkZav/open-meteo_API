import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.city import City
from repositories.db import get_db, transaction
from repositories.city_repository import CityRepository
from repositories.weather_repository import WeatherRepository
from utils.exceptions import CityNotFoundError, OpenMeteoAPIError
from utils.log import logger


tasks: dict[int, asyncio.Task] = {}


async def weather_update(city: City, db: AsyncSession) -> None:
    logger.info(f"Weather update started for city {city.id}")
    weather_repo = WeatherRepository(db)
    city_repo = CityRepository(db)

    new_weather_records = await weather_repo.get_weather_records_by_coord(
        city.coordinates)
    await city_repo.update_weather_records(city.id, new_weather_records)


async def periodic_weather_update(city: City) -> None:
    """
    Фоновое обновление погоды для города каждые 15 минут.
    """
    logger.info(f"Starting periodic weather update for city {city.id}")
    while True:
        await asyncio.sleep(15)  # 15 минут (для тестирования 15сек)

        async with get_db() as db, transaction(db):
            try:
                await weather_update(city, db)
                logger.info(f"Weather updated for city {city.id}")
            except OpenMeteoAPIError as e:
                logger.warning(f"OpenMeteo error for city {city.id}: {str(e)}")
            except CityNotFoundError:
                logger.error(f"City {city.id} not found. Stopping updates.")
                break  # Завершаем задачу, если город не найден
            except Exception as e:
                logger.error(f"Unexpected error for city {city.id}: {str(e)}")

    tasks.pop(city.id, None)
    logger.info(f"Stopped periodic updates for city {city.id}")


def create_periodic_weather_update_task(city: City) -> None:
    """Создание задачи для периодического обновления погоды для города."""
    logger.info(f"Creating periodic weather update task for city ID {city.id}")
    if city.id in tasks:
        logger.info(f"Task for city ID {city.id} already exists.")
        return
    task = asyncio.create_task(periodic_weather_update(city))
    tasks[city.id] = task
