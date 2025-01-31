from pydantic import BaseModel, Field
from datetime import datetime


class WeatherSchema(BaseModel):
    temperature_2m: float
    wind_speed_10m: float
    pressure_msl: float
    rain: float | None = None
    relative_humidity_2m: float | None = None

    time: datetime | None = None


class WeatherQueryParams(BaseModel):
    temperature_2m: bool = True
    wind_speed_10m: bool = True
    relative_humidity_2m: bool = False
    rain: bool = False
    pressure_msl: bool = True
