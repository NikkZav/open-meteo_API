from schemas.weather import Weather
from schemas.coordinates import Coordinates
from sqlalchemy.orm import Session
from .open_meteo_api import get_weather_records_by_open_meteo_api
from .city_repository import CityRepository
from utils.exceptions import CityNotFoundError


class WeatherRepository:
    """Источник данных о погоде из внешних API."""

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_weather_records_by_coordinates(self, coordinates: Coordinates
                                           ) -> list[Weather]:
        return get_weather_records_by_open_meteo_api(coordinates)

    # def get_weather_records_for_city(self, city_name: str) -> list[Weather]:
    #     """
    #     Возвращает прогноз погоды для города по его названию.
    #     Сам прогноз генерируется с помощью API open-meteo.
    #     """
    #     city = CityRepository(self.db_session).get_city_by_name(city_name)
    #     return self.get_weather_records_by_coordinates(city.coordinates)
