from fastapi import Depends
from sqlalchemy.orm import Session
from services.city_service import CityService
from repositories.weather_repository import WeatherRepository
from repositories.city_repository import CityRepository
from services.weather_service import WeatherService
from repositories.db import get_db
from utils.log import logger


def get_city_repository(db: Session = Depends(get_db)) -> CityRepository:
    logger.debug("Creating CityRepository instance")
    return CityRepository(db)


def get_weather_repository(db: Session = Depends(get_db)) -> WeatherRepository:
    logger.debug("Creating WeatherRepository instance")
    return WeatherRepository(db)


def get_weather_service(
        weather_repo: WeatherRepository = Depends(get_weather_repository),
        city_repo: CityRepository = Depends(get_city_repository),
) -> WeatherService:
    logger.debug("Creating WeatherService instance")
    return WeatherService(weather_repo, city_repo)


def get_city_service(
        city_repo: CityRepository = Depends(get_city_repository),
        weather_repo: WeatherRepository = Depends(get_weather_repository),
) -> CityService:
    logger.debug("Creating CityService instance")
    return CityService(city_repo, weather_repo)
