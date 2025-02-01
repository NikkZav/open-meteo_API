from pydantic import BaseModel

from .coordinates import CoordinatesSchema
from .weather import WeatherResponse


class CitySchema(CoordinatesSchema):
    name: str


class CityResponse(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    weather_records: list[WeatherResponse] | None = None

    class Config:
        from_attributes = True
