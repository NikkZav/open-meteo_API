import asyncio
from sqlalchemy.orm import Session
from services.city_service import CityService
from models import CityModel
from db import SessionLocal

tasks = {}


async def periodic_weather_update(city_id: int):
    """Обновление погоды для города каждые 15 минут."""
    while True:
        await asyncio.sleep(15)  # 15 минут
        print(f"Обновляем погоду для города ID {city_id}")

        # Создаём и управляем сессией
        db = SessionLocal()
        try:
            city = db.query(CityModel).get(city_id)
            if not city:
                print(f"Город ID {city_id} удалён. Останавливаем обновление.")
                break

            city_service = CityService(db, city)
            city_service.refresh_weather_records_for_city()
            db.commit()
        except Exception as e:
            print(f"Ошибка при обновлении погоды: {e}")
            db.rollback()
        finally:
            db.close()


async def create_periodic_weather_update_task(city_id: int):
    """Создание задачи для периодического обновления погоды для города."""
    tasks[city_id] = asyncio.create_task(
        periodic_weather_update(city_id)
    )
