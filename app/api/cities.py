from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.city_service import CityService
from services.update_weather_services import \
    create_periodic_weather_update_task
from schemas.city import CitySchema
from http import HTTPStatus
from db import get_db

router = APIRouter()


@router.post("/add_city", response_model=dict, status_code=HTTPStatus.CREATED)
async def add_city_endpoint(city_data: CitySchema,
                            db: Session = Depends(get_db)):
    """
    Метод принимает название города и его координаты и
    добавляет в список городов для которых отслеживается прогноз погоды
    """
    city_service = CityService(db, city_data)
    # Проверяем существование города
    if city_service.check_city_existence():
        raise HTTPException(status_code=HTTPStatus.CONFLICT,
                            detail="Этот город уже добавлен")
    # Добавляем новый город в БД
    new_city = city_service.add_city()
    # Создаем задачу обновления погоды для нового города
    await create_periodic_weather_update_task(city_id=new_city.id)
    return {"message": "Город успешно добавлен",
            "id": new_city.id,
            "name": new_city.name}


@router.get("/cities")
def get_cities(include_weather: bool | None = None,
               db: Session = Depends(get_db)):
    """Метод возвращает список городов. Есть опция вывести вместе с погодой"""
    city_service = CityService(db)
    return city_service.get_cities(include_weather)
