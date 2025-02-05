from schemas.coordinates import Coordinates
from repositories.weather_repository import WeatherRepository
from repositories.city_repository import CityRepository
from schemas.city import City, CityParams
from utils.exceptions import (CityNotFoundError,
                              CitySameNameExistsError,
                              CitySameCordsExistsError)
from utils.log import logger
from .update_weather_services import create_periodic_weather_update_task


class CityService:

    def __init__(self,
                 city_repository: CityRepository,
                 weather_repository: WeatherRepository):
        self.city_repo = city_repository
        self.weather_repo = weather_repository

    async def get_cities(self,
                         include_weather: bool | None = False
                         ) -> list[City | str]:
        """Получение списка городов из БД + (опционально) связанные данные"""
        if include_weather:
            return await self.city_repo.get_cities()
        else:
            return await self.city_repo.get_city_names()

    async def add_city(self, city_params: CityParams) -> City:
        """Добавление города в БД"""
        logger.info(f"Adding new city with name '{city_params.name}' "
                    f"and coordinates {city_params.coordinates}")
        await self._check_unique_city(city_params)
        saved_city = await self.city_repo.save_city(
            await self._create_city_with_weather(city_params)
        )
        return saved_city

    async def _create_city_with_weather(self, city_params: CityParams) -> City:
        """Создание города с погодой"""
        logger.info("Creating city with weather")
        weather_records = await self.weather_repo.get_weather_records_by_coord(
            city_params.coordinates)
        return City(**city_params.model_dump(),
                    weather_records=weather_records)

    async def _check_unique_city(self, city: CityParams) -> None:
        # Проверка на отсутствие города с таким же именем или координатами
        logger.info(f"Checking uniqueness for city: {city.name}")
        for getter_city, criteria, error in [
            (self.city_repo.get_city_by_name,  # проверка по имени
             city.name, CitySameNameExistsError),
            (self.city_repo.get_city_by_coord,  # проверка по координатам
             city.coordinates, CitySameCordsExistsError)
        ]:
            try:  # Пробуем получить город по критериям (название, координаты)
                await getter_city(criteria)
            except CityNotFoundError:
                pass  # Если город не найден, то все хорошо, идем дальше
            else:  # Если город найден, то выбрасываем ошибку
                raise error(f"City with '{criteria}' already exists")
        logger.info(f"City '{city.name}' is unique")
