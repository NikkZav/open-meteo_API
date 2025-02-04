from pydantic import BaseModel

from .coordinates import Coordinates
from .weather import Weather, WeatherResponse
from utils.exceptions import WeatherInCityNotFoundError
from utils.log import logger


class City(BaseModel):
    id: int = 0
    name: str
    coordinates: Coordinates
    weather_records: list[Weather]

    def get_weather_records(self) -> list[Weather]:
        if not self.weather_records:
            raise WeatherInCityNotFoundError(
                f"City {self.name} doesn't have any weather records"
            )
        return self.weather_records


class CityParams(BaseModel):
    name: str
    coordinates: Coordinates


class CityResponse(BaseModel):
    id: int | None = None
    name: str
    coordinates: Coordinates | None = None
    weather_records: list[WeatherResponse] | None = None

    class Config:
        from_attributes = True

    @classmethod
    def build_response(cls, cities: list[City | str],
                       include_weather: bool | None = False
                       ) -> "list[CityResponse | str]":
        """Конвертация списка городов в список CityResponse"""
        logger.info("Building response for a list of cities")
        if include_weather:
            return [cls.convert_city_to_response(city) for city in cities
                    if isinstance(city, City)]
        # return [CityResponse(name=city_name) for city_name
        #         in cities if isinstance(city_name, str)]
        return [city_name for city_name in cities
                if isinstance(city_name, str)]

    @staticmethod
    def convert_city_to_response(city: City) -> "CityResponse":
        """Конвертация City в CityResponse с вложенными Weather"""
        weather_records = [
            WeatherResponse.build_response(weather_record)
            for weather_record in city.weather_records
        ]
        return CityResponse(
            id=city.id,
            name=city.name,
            coordinates=city.coordinates,
            weather_records=weather_records
        )
