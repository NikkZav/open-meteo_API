from .coordinates import CoordinatesSchema
from .weather import WeatherSchema
from typing import Optional


class CitySchema(CoordinatesSchema):
    id: int
    name: str
    weather: Optional[WeatherSchema] = None

    class Config:
        orm_mode = True
