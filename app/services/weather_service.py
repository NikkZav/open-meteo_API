import requests
from http import HTTPStatus
from sqlalchemy.orm import Session
from sqlalchemy import func
from schemas.coordinates import CoordinatesSchema
from schemas.weather import WeatherSchema
from models import CityModel, WeatherModel
from datetime import datetime


URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_PARAMS = ','.join(WeatherSchema.__annotations__.keys()
                          ).replace(",time", "")


def parse_weather(json_data: dict) -> list[WeatherSchema]:
    """Парсит данные о погоде."""
    weather_forecast = {}
    param_names = WEATHER_PARAMS.split(",") + ["time"]
    for param_name in param_names:
        param_forecast: list = json_data.get("minutely_15", {}).get(param_name)
        weather_forecast[param_name] = param_forecast

    return [
        WeatherSchema(**dict(zip(param_names, param_forecast)))
        for param_forecast in zip(*weather_forecast.values())
    ]


def get_weather_records_by_coordinates(coordinates: CoordinatesSchema
                                       ) -> list[WeatherSchema]:
    """Возвращает прогноз погоды по координатам."""
    url_params = {
        "latitude": coordinates.latitude,
        "longitude": coordinates.longitude,
        "minutely_15": WEATHER_PARAMS,
    }

    response = requests.get(URL, params=url_params)
    if response.status_code != HTTPStatus.OK:
        raise Exception(f"Ошибка запроса: {response.status_code}\n"
                        f"Детали: {response.text}")

    json_data = response.json()
    weather_records = parse_weather(json_data)
    return weather_records


def get_weather_closest_to_time_by_coordinates(
        coordinates: CoordinatesSchema,
        time: datetime) -> WeatherSchema:
    weather_records = get_weather_records_by_coordinates(coordinates)
    closest_record = min(weather_records,
                         key=lambda record: abs(record.time - time))
    return closest_record


def get_weather_in_city(city: CityModel) -> list[WeatherSchema]:
    coordinates = CoordinatesSchema(
        latitude=city.latitude,
        longitude=city.longitude
    )
    return get_weather_records_by_coordinates(coordinates)


def get_weather_in_city_on_time(city: CityModel,
                                time: datetime) -> WeatherSchema:
    """Возвращает погоду в городе во время, наиболее близкое к указанному."""
    if not city.weather_records:
        raise ValueError("Нет данных о погоде для указанного города.")

    # Находим ближайшую запись
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
