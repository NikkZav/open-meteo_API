from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from sqlalchemy.orm import Session
from services import weather_service
from services.city_service import get_city_or_none
from schemas.coordinates import CoordinatesSchema
from datetime import datetime
from db import get_db

router = APIRouter()


@router.get("/weather")
async def get_weather_endpoint(coordinates: CoordinatesSchema = Depends()):
    weather = weather_service.get_weather_closest_to_time_by_coordinates(
        coordinates=coordinates,
        time=datetime.now()
    )
    # В ТЗ по такому запросу требуется возвразать только
    # "данные о температуре, скорости ветра и атмосферном давлении"
    return {"temperature_2m": weather.temperature_2m,
            "wind_speed_10m": weather.wind_speed_10m,
            "pressure_msl": weather.pressure_msl,
            "time": weather.time}


@router.get("/weather/{city_name}")
def get_weather_in_city_endpoint(
    city_name: str,
    time: datetime | None = None,
    temperature_2m: bool = True,
    wind_speed_10m: bool = False,
    relative_humidity_2m: bool = False,
    rain: bool = False,
    db: Session = Depends(get_db)
):
    if (city := get_city_or_none(city_name, db)) is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail="Город не найден")
    weather = weather_service.get_weather_in_city_on_time(city, time)
    weather_response = weather_service.build_weather_response(
        weather,
        requested_params={
            "time": True,
            "temperature_2m": temperature_2m,
            "wind_speed_10m": wind_speed_10m,
            "relative_humidity_2m": relative_humidity_2m,
            "rain": rain,
        }
    )
    return weather_response
