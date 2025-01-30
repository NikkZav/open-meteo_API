import requests
from http import HTTPStatus
from sqlalchemy.orm import Session
from sqlalchemy import func
from schemas.coordinates import CoordinatesSchema
from schemas.weather import WeatherSchema
from models import CityModel, WeatherModel
from datetime import datetime


URL = "https://api.open-meteo.com/v1/forecast"


def parse_weather(json_data: dict, params: dict) -> WeatherSchema:
    """Парсит данные о погоде."""

    current_weather = json_data.get("current_weather", {})

    temperature = current_weather.get("temperature", "Uknonwn")
    wind_speed = current_weather.get("windspeed", "Uknonwn")

    others = {}
    # В current_weather не всегда есть все данные
    for property_name in params.get("minutely_15", '').split(','):
        if property_name in current_weather:
            others[property_name] = current_weather[property_name]
        else:
            # Поэтому берем последнюю статистику
            properties = json_data.get("minutely_15", {}).get(property_name)
            others[property_name] = properties[-1] if properties else "Uknonwn"

    return WeatherSchema(
        temperature=temperature,
        wind_speed=wind_speed,
        **others
    )


def get_weather_by_coordinates(coordinates: CoordinatesSchema
                               ) -> WeatherSchema:
    """Возвращает погоду по координатам."""

    params = {
        "latitude": coordinates.latitude,
        "longitude": coordinates.longitude,
        "current_weather": "true",
        "minutely_15": "pressure_msl,relative_humidity_2m,rain"
    }

    response = requests.get(URL, params=params)
    if response.status_code != HTTPStatus.OK:
        return {
            "error": f"Ошибка запроса: {response.status_code}",
            "details": response.text
        }

    json_data = response.json()
    return parse_weather(json_data, params=params)


def get_weather_in_city(city: CityModel) -> WeatherSchema:
    """Возвращает погоду по названию города."""
    coordinates = CoordinatesSchema(
        latitude=city.latitude,
        longitude=city.longitude
    )
    return get_weather_by_coordinates(coordinates)


def get_weather_in_city_on_time(city: CityModel,
                                time: datetime) -> WeatherSchema:
    """Возвращает погоду в городе во время, наиболее близкое к указанному."""
    if not city.weather_records:
        raise ValueError("Нет данных о погоде для указанного города.")

    # Находим ближайшую запись без явной фильтрации
    closest_record = min(city.weather_records,
                         key=lambda record: abs(record.time - time))

    return WeatherSchema.model_validate(closest_record, from_attributes=True)


def build_weather_response(weather: WeatherSchema,
                           requested_params: dict) -> dict:
    weather_dict = weather.model_dump()
    weather_response = {
        key: weather_dict.get(key)
        for key, include in requested_params.items()
        if include
    }
    return weather_response
