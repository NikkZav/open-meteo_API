from datetime import date, datetime

from app.repositories.city_repository import CityRepository
from app.repositories.weather_repository import WeatherRepository
from app.schemas.coordinates import Coordinates
from app.schemas.weather import Weather
from app.utils.exceptions import (CityNotFoundError, TimeRangeError,
                                  WeatherInCityNotFoundError)
from app.utils.log import logger


class WeatherService:
    def __init__(
        self, weather_repository: WeatherRepository,
        city_repoitory: CityRepository
    ):
        self.weather_repo = weather_repository
        self.city_repo = city_repoitory

    async def get_weather_now(self, coordinates: Coordinates) -> Weather:
        """
        Возвращает текущую погоду по координатам.
        Запросом к Open-Meteo API отправляется только тогда, если его нет в БД.
        """
        logger.info(f"Getting current weather for coordinates {coordinates}")
        try:  # В начале пытаемся получить погоду из БД
            logger.info("Trying to get weather from DB")
            city = await self.city_repo.get_city_by_coord(coordinates)
            weather_records = city.get_weather_records()
            weather = self._search_closest_to_time_weather_record(
                weather_records=weather_records, time=datetime.now()
            )
            logger.info("Weather found in DB")
        except (CityNotFoundError, WeatherInCityNotFoundError):
            logger.warning("Weather not found in DB. Fetching from API")
            weather = await self._get_weather_closest_to_time(
                coordinates, time=datetime.now()
            )
        return weather

    async def get_weather_in_city_at_time(
        self, city_name: str, time: datetime
    ) -> Weather:
        """
        Возвращает погоду в городе во время, наиболее близкое к указанному.
        Запросом к Open-Meteo API отправляется только тогда, если его нет в БД.
        """
        if time.date() != date.today():
            raise TimeRangeError("The time should be today")

        city = await self.city_repo.get_city_by_name(city_name)

        try:  # В начале пытаемся получить погоду из БД
            logger.info("Trying to get weather from DB")
            weather_records = city.get_weather_records()
            weather = self._search_closest_to_time_weather_record(
                weather_records, time)
            logger.info("Weather found in DB")
        except WeatherInCityNotFoundError:  # Если в БД нет, то запрос к API
            logger.info("Getting weather from API")
            weather = await self._get_weather_closest_to_time(
                city.coordinates, time)
        return weather

    def _search_closest_to_time_weather_record(
        self, weather_records: list[Weather], time: datetime
    ) -> Weather:
        """Возвращает запись о погоде, ближайшую к указанному времени."""
        return min(weather_records, key=lambda record: abs(record.time - time))

    async def _get_weather_closest_to_time(
        self, coordinates: Coordinates, time: datetime
    ) -> Weather:
        weather_records = await self.weather_repo.get_weather_records_by_coord(
            coordinates
        )
        closest_weather = self._search_closest_to_time_weather_record(
            weather_records, time
        )
        return closest_weather
