from pydantic import BaseModel

from .coordinates import Coordinates
from .weather import Weather, WeatherResponse


class City(BaseModel):
    name: str
    coordinates: Coordinates
    weather_records: list[Weather] | None = None


class CityResponse(BaseModel):
    id: int
    name: str
    coordinates: Coordinates
    weather_records: list[WeatherResponse] | None = None

    class Config:
        from_attributes = True
