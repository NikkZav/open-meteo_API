from repositories.weather_repository import WeatherRepository
from repositories.city_repository import CityRepository
from schemas.weather import Weather
from schemas.coordinates import Coordinates
from datetime import datetime, date
from utils.exceptions import (TimeRangeError, CityNotFoundError,
                              WeatherInCityNotFoundError)


class WeatherService:
    def __init__(self,
                 weather_repository: WeatherRepository,
                 city_repoitory: CityRepository):
        self.weather_repo = weather_repository
        self.city_repo = city_repoitory

    def get_weather_now(self, coordinates: Coordinates) -> Weather:
        """
        Возвращает текущую погоду по координатам.
        Запросом к Open-Meteo API отправляется только тогда, если его нет в БД.
        """
        try:  # В начале пытаемся получить погоду из БД
            city = self.city_repo.get_city_by_coord(coordinates)
            weather_records = city.get_weather_records()
            weather = self._search_closest_to_time_weather_record(
                weather_records=weather_records,
                time=datetime.now()
            )
        except (CityNotFoundError, WeatherInCityNotFoundError):
            weather = self._get_weather_closest_to_time(coordinates,
                                                        time=datetime.now())

        return weather

    def get_weather_in_city_at_time(self, city_name: str,
                                    time: datetime) -> Weather:
        """
        Возвращает погоду в городе во время, наиболее близкое к указанному.
        Запросом к Open-Meteo API отправляется только тогда, если его нет в БД.
        """
        if time.date() != date.today():
            raise TimeRangeError("The time should be today")

        city = self.city_repo.get_city_by_name(city_name)

        try:  # В начале пытаемся получить погоду из БД
            weather_records = city.get_weather_records()
            weather = self._search_closest_to_time_weather_record(
                weather_records, time
            )
        except WeatherInCityNotFoundError:  # Если в БД нет, то запрос к API
            weather = self._get_weather_closest_to_time(city.coordinates, time)
        return weather

    def _search_closest_to_time_weather_record(self,
                                               weather_records: list[Weather],
                                               time: datetime) -> Weather:
        """Возвращает запись о погоде, ближайшую к указанному времени."""
        return min(weather_records, key=lambda record: abs(record.time - time))

    def _get_weather_closest_to_time(self, coordinates: Coordinates,
                                     time: datetime) -> Weather:
        weather_records = \
            self.weather_repo.get_weather_records_by_coord(coordinates)
        closest_weather = \
            self._search_closest_to_time_weather_record(weather_records, time)
        return closest_weather
