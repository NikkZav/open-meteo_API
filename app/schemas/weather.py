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


class WeatherResponse(BaseModel):
    temperature_2m: float | None = None
    wind_speed_10m: float | None = None
    pressure_msl: float | None = None
    relative_humidity_2m: float | None = None
    rain: float | None = None
    time: datetime | None = None

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "temperature_2m": 15.2,
                "wind_speed_10m": 5.6,
                "pressure_msl": 1013.0,
                "relative_humidity_2m": 80.0,
                "rain": 0.0,
                "time": "2025-01-30T12:00:00"
            }
        }
