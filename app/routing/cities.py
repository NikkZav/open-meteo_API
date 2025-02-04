from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from depends import get_city_service
from services.city_service import CityService
from schemas.city import CityResponse, City, CityParams
from utils.exceptions import SameCityExistsError
from utils.log import logger
from services.update_weather_services import \
    create_periodic_weather_update_task


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
async def add_city_endpoint(
        city: CityParams,
        city_service: CityService = Depends(get_city_service)):
    """
    Метод принимает название города и его координаты и
    добавляет в список городов для которых отслеживается прогноз погоды
    """
    logger.info(f"Received a request to add a city '{city.name}'")
    try:
        # Добавляем новый город в БД
        new_city = city_service.add_city(city)
        # Создаем задачу обновления погоды для нового города
        create_periodic_weather_update_task(city=new_city)
    except SameCityExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))

    return {"message": "Город успешно добавлен",
            "id": new_city.id,
            "name": new_city.name}


@router.get(
    "/cities",
    response_model=list[CityResponse | str],
    response_model_exclude_unset=True,
    responses={
        200: {"description": "Список городов получен"},
    }
)
def get_cities_endpoint(include_weather: bool | None = None,
                        city_service: CityService = Depends(get_city_service)):
    """Метод возвращает список городов. Есть опция вывести вместе с погодой"""
    logger.info("Received a request to get the list of cities")
    cities: list[City | str] = city_service.get_cities(include_weather)
    return CityResponse.build_response(cities, include_weather)
