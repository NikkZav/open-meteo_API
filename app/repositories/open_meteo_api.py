from datetime import datetime, time
from http import HTTPStatus

import httpx

from schemas.coordinates import Coordinates
from schemas.weather import Weather
from utils.exceptions import OpenMeteoAPIError
from utils.log import logger

URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_PARAMS = ",".join(
    Weather.__annotations__.keys()).replace(",time", "")


def parse_weather(json_data: dict) -> list[Weather]:
    """
    Распоковывает полученные от open-meteo данные
    в список объектов WeatherSchema - прогноз погоды на текущий день.
    """
    logger.info("Parsing weather data")
    weather_forecast = {}
    param_names = WEATHER_PARAMS.split(",") + ["time"]
    for param_name in param_names:
        param_forecast: list = json_data.get("minutely_15", {}).get(param_name)
        weather_forecast[param_name] = param_forecast

    start_of_day = datetime.combine(datetime.today(), time.min)
    end_of_day = datetime.combine(datetime.today(), time.max)

    return [
        weather
        for weather in [
            Weather(**dict(zip(param_names, weather_record)))
            for weather_record in zip(*weather_forecast.values())
        ]
        if start_of_day <= weather.time <= end_of_day
    ]


async def get_weather_records_by_open_meteo_api(coordinates: Coordinates
                                          ) -> list[Weather]:
    """Асинхронный запрос к Open-Meteo API"""
    logger.info("Requesting weather by open-meteo API (async)")
    url_params = {
        "latitude": coordinates.latitude,
        "longitude": coordinates.longitude,
        "minutely_15": WEATHER_PARAMS,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(URL, params=url_params)
    except httpx.HTTPStatusError as e:
        logger.error(f"Open-Meteo API error: {e.response.status_code}")
        raise OpenMeteoAPIError(f"HTTP error {e.response.status_code}: "
                                f"{e.response.text}")
    except httpx.RequestError as e:
        logger.error(f"Open-Meteo connection error: {str(e)}")
        raise OpenMeteoAPIError("Connection to weather service failed")

    json_data = response.json()
    weather_records = parse_weather(json_data)
    return weather_records
