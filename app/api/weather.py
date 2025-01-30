from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from sqlalchemy.orm import Session
from services import weather_service
from services.city_service import get_city
from core.db import SessionLocal
from schemas.coordinates import CoordinatesSchema
from datetime import datetime

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/weather")
async def get_weather_endpoint(coordinates: CoordinatesSchema = Depends()):
    weather = weather_service.get_weather_by_coordinates(coordinates)
    # В ТЗ по такому запросу требуется возвразать только
    # "данные о температуре, скорости ветра и атмосферном давлении"
    return {"temperature": weather.temperature,
            "wind_speed": weather.wind_speed,
            "pressure_msl": weather.pressure_msl}


@router.get("/weather/{city_name}")
def get_weather_in_city_endpoint(
    city_name: str,
    time: datetime | None = None,
    temperature: bool = True,
    wind_speed: bool = False,
    humidity: bool = False,
    rain: bool = False,
    db: Session = Depends(get_db)
):
    if (city := get_city(city_name, db)) is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND,
                            detail="Город не найден")
    weather = weather_service.get_weather_by_city(city, time, db)
    weather_response = weather_service.build_weather_response(
        weather,
        requested_params={
            "temperature": temperature,
            "wind_speed": wind_speed,
            "humidity": humidity,
            "rain": rain,
        }
    )
    return weather_response
