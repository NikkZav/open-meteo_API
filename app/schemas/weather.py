from pydantic import BaseModel, Field


class WeatherSchema(BaseModel):
    temperature: float
    wind_speed: float
    pressure_msl: float
    rain: float = None
    relative_humidity_2m: float = None
