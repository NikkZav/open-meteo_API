from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.db import get_db
from repositories.city_repository import CityRepository
from repositories.weather_repository import WeatherRepository
from services.weather_service import WeatherService
from services.city_service import CityService
from typing import AsyncGenerator


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_db() as session:
        yield session


async def get_city_repository(db: AsyncSession = Depends(get_db_session)
                              ) -> CityRepository:
    return CityRepository(db)


async def get_weather_repository(db: AsyncSession = Depends(get_db_session)
                                 ) -> WeatherRepository:
    return WeatherRepository(db)


async def get_weather_service(
    weather_repo: WeatherRepository = Depends(get_weather_repository),
    city_repo: CityRepository = Depends(get_city_repository)
) -> WeatherService:
    return WeatherService(weather_repo, city_repo)


async def get_city_service(
    city_repo: CityRepository = Depends(get_city_repository),
    weather_repo: WeatherRepository = Depends(get_weather_repository)
) -> CityService:
    return CityService(city_repo, weather_repo)
