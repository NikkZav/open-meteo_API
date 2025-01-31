import requests
from http import HTTPStatus
from sqlalchemy.orm import Session
from sqlalchemy import func
from schemas.coordinates import CoordinatesSchema
from schemas.weather import WeatherSchema, WeatherQueryParams
from models import CityModel, WeatherModel
from datetime import datetime, time
from services.common_utils import get_city_or_none


URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_PARAMS = ','.join(WeatherSchema.__annotations__.keys()
                          ).replace(",time", "")


def parse_weather(json_data: dict) -> list[WeatherSchema]:
    """
    Распоковывает полученные от open-meteo данные
    в список объектов WeatherSchema - прогноз погоды на текущий день.
    """
    weather_forecast = {}
    param_names = WEATHER_PARAMS.split(",") + ["time"]
    for param_name in param_names:
        param_forecast: list = json_data.get("minutely_15", {}).get(param_name)
        weather_forecast[param_name] = param_forecast

    start_of_day = datetime.combine(datetime.today(), time.min)
    end_of_day = datetime.combine(datetime.today(), time.max)

    return [
        weather for weather in [
            WeatherSchema(**dict(zip(param_names, weather_record)))
            for weather_record in zip(*weather_forecast.values())
        ] if start_of_day <= weather.time <= end_of_day
    ]


def get_weather_records_by_coordinates(coordinates: CoordinatesSchema
                                       ) -> list[WeatherSchema]:
    """Возвращает прогноз погоды по координатам на текущий день."""
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


def build_weather_response(weather: WeatherSchema,
                           query_params: WeatherQueryParams) -> dict:
    """Формирует ответ на основе запрошенных параметров."""
    weather_dict = weather.model_dump()
    query_params_dict = query_params.model_dump()

    weather_response = {
        key: weather_dict.get(key)
        for key, include in query_params_dict.items()
        if include
    }
    weather_response["time"] = weather.time.isoformat()
    return weather_response
