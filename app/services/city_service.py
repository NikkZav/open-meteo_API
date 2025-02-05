from typing import cast

from app.repositories.city_repository import CityRepository
from app.repositories.weather_repository import WeatherRepository
from app.schemas.city import City, CityParams
from app.utils.exceptions import (CityNotFoundError, CitySameCordsExistsError,
                                  CitySameNameExistsError)
from app.utils.log import logger


class CityService:

    def __init__(self,
                 city_repository: CityRepository,
                 weather_repository: WeatherRepository):
        self.city_repo = city_repository
        self.weather_repo = weather_repository

    async def get_cities(
        self, include_weather: bool | None = False
    ) -> list[City | str]:
        """Получение списка городов из БД + (опционально) связанные данные"""
        if include_weather:
            return await self.city_repo.get_cities()
        else:  # cast - приведение типов, чтобы не было ошибки от Mypy
            return cast(list[City | str],
                        await self.city_repo.get_city_names())

    async def add_city(self, city_params: CityParams) -> City:
        """Добавление города в БД"""
        logger.info(
            f"Adding new city with name '{city_params.name}' "
            f"and coordinates {city_params.coordinates}"
        )
        await self._check_unique_city(city_params)
        saved_city = await self.city_repo.save_city(
            await self._create_city_with_weather(city_params)
        )
        return saved_city

    async def _create_city_with_weather(self, city_params: CityParams) -> City:
        """Создание города с погодой"""
        logger.info("Creating city with weather")
        weather_records = await self.weather_repo.get_weather_records_by_coord(
            city_params.coordinates
        )
        return City(**city_params.model_dump(),
                    weather_records=weather_records)

    async def _check_unique_city(self, city: CityParams) -> None:
        """Проверка на отсутствие города с таким же именем или координатами"""
        logger.info(f"Checking uniqueness for city: {city.name}")
        # Проверка по имени
        try:
            await self.city_repo.get_city_by_name(city.name)
        except CityNotFoundError:
            pass
        else:
            raise CitySameNameExistsError(
                f"City with name '{city.name}' already exists")

        # Проверка по координатам
        try:
            await self.city_repo.get_city_by_coord(city.coordinates)
        except CityNotFoundError:
            pass
        else:
            raise CitySameCordsExistsError(
                f"City with coordinates '{city.coordinates}' already exists")

        logger.info(f"City '{city.name}' is unique")
