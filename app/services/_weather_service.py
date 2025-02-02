from datetime import datetime, time
from http import HTTPStatus

import requests
from sqlalchemy import func
from sqlalchemy.orm import Session

from models import CityModel, WeatherModel
from schemas.coordinates import CoordinatesSchema
from schemas.weather import WeatherQueryParams, WeatherSchema
from app.services._common_utils import get_city_or_none


def search_clothest_to_time_weather_record(
        weather_records: list[WeatherSchema | WeatherModel],
        time: datetime) -> WeatherSchema | WeatherModel:
    """Возвращает запись о погоде, время которой ближе всего к указанному."""
    return min(weather_records, key=lambda record: abs(record.time - time))


def get_weather_closest_to_time_in_city(city: CityModel,
                                        time: datetime) -> WeatherSchema:
    """
    Возвращает погоду в городе во время, наиболее близкое к указанному.
    Поиск производиться среди имеющихся записей в БД.
    """
    if not city.weather_records:
        raise ValueError("Нет данных о погоде для указанного города.")

    # Находим ближайшую запись
    closest_record = search_clothest_to_time_weather_record(
        city.weather_records, time)

    return WeatherSchema.model_validate(closest_record, from_attributes=True)


def get_weather_closest_to_time_by_coordinates(
        coordinates: CoordinatesSchema,
        time: datetime,
        db: Session) -> WeatherSchema:
    """
    Возвращает погоду в городе во время, наиболее близкое к указанному.
    Само значение формируется запросом к Open-Meteo API, если его нет в БД
    """
    if city := get_city_or_none(coordinates, db):
        # Если город есть в БД, то ищем ближайшую запись в БД
        try:
            return get_weather_closest_to_time_in_city(city, time)
        except ValueError:
            # Если нет записей в БД, то запрашиваем данные с API
            pass

    weather_records = get_weather_records_by_coordinates(coordinates)
    return search_clothest_to_time_weather_record(weather_records, time)


def get_weather_records_in_city(city: CityModel) -> list[WeatherSchema]:
    coordinates = CoordinatesSchema(
        latitude=city.latitude,
        longitude=city.longitude
    )
    return get_weather_records_by_coordinates(coordinates)
