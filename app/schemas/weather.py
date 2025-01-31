from pydantic import BaseModel, Field
from datetime import datetime


class WeatherSchema(BaseModel):
    temperature_2m: float
    wind_speed_10m: float
    pressure_msl: float
    rain: float | None = None
    relative_humidity_2m: float | None = None

    time: datetime | None = None
