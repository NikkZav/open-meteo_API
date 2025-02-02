from repositories.weather_repository import WeatherRepository
from repositories.city_repository import CityRepository
from schemas.weather import Weather
from schemas.coordinates import Coordinates
from schemas.city import City
from datetime import datetime, date
from utils.exceptions import TimeRangeError


class WeatherService:
    def __init__(self,
                 weather_repository: WeatherRepository,
                 city_repository: CityRepository):
        self.weather_repos = weather_repository
        self.city_repos = city_repository

    def get_weather_now(self, coordinates: Coordinates) -> Weather:
        return self._get_weather_closest_to_time(coordinates, datetime.now())

    def get_weather_in_city_at_time(self, city_name: str,
                                    time: datetime) -> Weather:
        if time.date() != date.today():
            raise TimeRangeError("Время должно быть в пределах сегодняшнего дня")
        city: City = self.city_repos.get_city_by_name(city_name)
        return self._get_weather_closest_to_time(city.coordinates, time)

    def get_weather_records_for_city(self, city_name: str) -> list[Weather]:
        """
        Возвращает прогноз погоды для города по его названию.
        Сам прогноз генерируется с помощью API open-meteo.
        """
        city = self.city_repos.get_city_by_name(city_name)
        return (self.weather_repos
                .get_weather_records_by_coordinates(city.coordinates))

    def _search_closest_to_time_weather_record(self,
                                               weather_records: list[Weather],
                                               time: datetime) -> Weather:
        """Возвращает запись о погоде, ближайшую к указанному времени."""
        return min(weather_records, key=lambda record: abs(record.time - time))

    def _get_weather_closest_to_time(self, coordinates: Coordinates,
                                     time: datetime) -> Weather:
        weather_records = \
            self.weather_repos.get_weather_records_by_coordinates(coordinates)
        closest_weather = \
            self._search_closest_to_time_weather_record(weather_records, time)
        return closest_weather
