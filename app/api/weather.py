from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from sqlalchemy.orm import Session
from services import weather_service
from services.city_service import get_city_or_none
from services.validators import CityValidator, TimeValidator
from schemas.coordinates import CoordinatesSchema
from schemas.weather import WeatherQueryParams
from datetime import datetime
from db import get_db

router = APIRouter()


@router.get("/weather")
async def get_weather_endpoint(
    coordinates: CoordinatesSchema = Depends(),
    weather_query_params: WeatherQueryParams = Depends(),
    db: Session = Depends(get_db)
):
    """
    Метод принимает координаты и возвращает погоду в текущее время.
    Возвращаемые параметры погоды определюятся через qurey-параметры.
    """
    weather = weather_service.get_weather_closest_to_time_by_coordinates(
        coordinates=coordinates,
        time=datetime.now(),
        db=db
    )
    return weather_service.build_weather_response(weather,
                                                  weather_query_params)


@router.get("/weather/{city_name}")
def get_weather_in_city_endpoint(
    city_name: str,
    time: datetime,
    weather_query_params: WeatherQueryParams = Depends(),
    db: Session = Depends(get_db)
):
    """
    Метод принимает название города и время,
    возвращает для него погоду на текущий день в указанное время.
    Возвращаемые параметры погоды определюятся через qurey-параметры.
    """
    # Проверяем существует ли город в базе данных
    city = CityValidator.validate_city_exists(city_name, db)
    # Проверяем что время находится в пределах текущего дня
    TimeValidator.validate_within_current_day(time)

    weather = weather_service.get_weather_closest_to_time_in_city(city, time)

    return weather_service.build_weather_response(weather,
                                                  weather_query_params)
