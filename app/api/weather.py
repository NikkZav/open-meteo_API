from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from services.weather_service import get_weather_by_coordinates
from core.db import SessionLocal
from schemas.coordinates import CoordinatesSchema

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/weather")
async def weather(coordinates: CoordinatesSchema = Depends()):
    weather = get_weather_by_coordinates(coordinates)
    # В ТЗ по такому запросу требуется возвразать только
    # "данные о температуре, скорости ветра и атмосферном давлении"
    return {
        "temperature": weather.temperature,
        "wind_speed": weather.wind_speed,
        "pressure_msl": weather.pressure_msl
    }


# @router.get("/weather/{city_name}")
