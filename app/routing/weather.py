from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime

from schemas.coordinates import Coordinates
from schemas.weather import WeatherQueryParams, WeatherResponse
from depends import get_weather_service
from services.weather_service import WeatherService
from utils.exceptions import (CityNotFoundError, OpenMeteoAPIError,
                              TimeRangeError)
from utils.log import logger


router = APIRouter()


@router.get(
    "/weather",
    response_model=WeatherResponse,
    response_model_exclude_unset=True,
    responses={
        200: {"description": "Успешное получение данных о погоде"},
        404: {"description": "Город не найден"},
        503: {"description": "Сервис погоды недоступен"}
    }
)
async def get_weather_endpoint(
    coordinates: Coordinates = Depends(),
    weather_query_params: WeatherQueryParams = Depends(),
    weather_service: WeatherService = Depends(get_weather_service),
):
    """
    Метод принимает координаты и возвращает погоду в текущее время.
    Возвращаемые параметры погоды определюятся через qurey-параметры.
    """
    logger.info(f"Requesting weather for coordinates {coordinates}")
    try:
        weather = weather_service.get_weather_now(coordinates)
    except OpenMeteoAPIError as e:
        raise HTTPException(status_code=503, detail=str(e))
    return WeatherResponse.build_response(weather, weather_query_params)


@router.get(
    "/weather/{city_name}",
    response_model=WeatherResponse,
    response_model_exclude_unset=True,
    responses={
        200: {"description": "Успешное получение данных о погоде для города"},
        404: {"description": "Город не найден"},
        503: {"description": "Сервис погоды недоступен"},
        400: {"description": "Неверный диапазон времени"}
    }
)
def get_weather_in_city_endpoint(
    city_name: str,
    time: datetime,
    weather_query_params: WeatherQueryParams = Depends(),
    weather_service: WeatherService = Depends(get_weather_service),
):
    """
    Метод принимает название города и время,
    возвращает для него погоду на текущий день в указанное время.
    Возвращаемые параметры погоды определюятся через qurey-параметры.
    """
    logger.info(f"Requesting weather for city '{city_name}' at time {time}")
    try:
        weather = weather_service.get_weather_in_city_at_time(city_name, time)
    except CityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except OpenMeteoAPIError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except TimeRangeError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return WeatherResponse.build_response(weather, weather_query_params)
