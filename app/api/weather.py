from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from sqlalchemy.orm import Session
from services import weather_service
from services.city_service import get_city_or_none
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
    if (city := get_city_or_none(city_name, db)) is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail="Город не найден")
    weather = weather_service.get_weather_closest_to_time_in_city(city, time)
    return weather_service.build_weather_response(weather,
                                                  weather_query_params)
