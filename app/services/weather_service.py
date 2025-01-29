import requests
from http import HTTPStatus

if __name__ == "__main__":
    import sys
    sys.path.append("app")

from schemas.coordinates import CoordinatesSchema
from schemas.weather import WeatherSchema


URL = "https://api.open-meteo.com/v1/forecast"


def parse_weather(json_data: dict) -> WeatherSchema:
    """Парсит данные о погоде."""

    current_weather = json_data.get("current_weather", {})

    temperature = current_weather.get("temperature", "Неизвестно")
    wind_speed = current_weather.get("windspeed", "Неизвестно")

    # В current_weather не всегда есть pressure_msl
    if "pressure_msl" in current_weather:
        pressure = current_weather["pressure_msl"]
    else:
        # Поэтому берем статистику за последний час
        pressures = json_data.get("hourly", {}).get("pressure_msl")
        pressure = pressures[-1] if pressures else "Неизвестно"

    return WeatherSchema(
        temperature=temperature,
        wind_speed=wind_speed,
        pressure_msl=pressure
    )


def get_weather_by_coordinates(coordinates: CoordinatesSchema
                               ) -> WeatherSchema:
    """Получает погоду по координатам."""

    params = {
        "latitude": coordinates.latitude,
        "longitude": coordinates.longitude,
        "current_weather": "true",
        "hourly": "pressure_msl",
    }

    response = requests.get(URL, params=params)
    if response.status_code != HTTPStatus.OK:
        return {
            "error": f"Ошибка запроса: {response.status_code}",
            "details": response.text
        }

    json_data = response.json()
    return parse_weather(json_data)


if __name__ == "__main__":
    coordinates = CoordinatesSchema(latitude=55.75, longitude=37.61)
    weather = get_weather_by_coordinates(coordinates)
    print(weather)
