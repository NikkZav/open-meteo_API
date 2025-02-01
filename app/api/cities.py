from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.city_service import CityService
from services.validators import CityValidator
from services.update_weather_services import \
    create_periodic_weather_update_task
from schemas.city import CitySchema, CityResponse
from http import HTTPStatus
from db import get_db

router = APIRouter()


@router.post(
    "/add_city",
    response_model=dict,
    status_code=HTTPStatus.CREATED,
    responses={
        201: {"description": "Город успешно добавлен"},
        409: {"description": "Город уже существует"}
    }
)
async def add_city_endpoint(city_data: CitySchema,
                            db: Session = Depends(get_db)):
    """
    Метод принимает название города и его координаты и
    добавляет в список городов для которых отслеживается прогноз погоды
    """
    # Проверяем существование города
    CityValidator.validate_city_not_exists(city_data, db)

    # Добавляем новый город в БД
    new_city = CityService(db, city_data).add_city()

    # Создаем задачу обновления погоды для нового города
    await create_periodic_weather_update_task(city_id=new_city.id)

    return {"message": "Город успешно добавлен",
            "id": new_city.id,
            "name": new_city.name}


@router.get(
    "/cities",
    response_model=list[CityResponse | str],
    responses={
        200: {"description": "Список городов получен"},
    }
)
def get_cities(include_weather: bool | None = None,
               db: Session = Depends(get_db)):
    """Метод возвращает список городов. Есть опция вывести вместе с погодой"""
    return CityService(db).get_cities(include_weather)
