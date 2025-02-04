from schemas.weather import Weather
from schemas.coordinates import Coordinates
from sqlalchemy.orm import Session
from .open_meteo_api import get_weather_records_by_open_meteo_api


class WeatherRepository:

    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def get_weather_records_by_coord(self, coordinates: Coordinates
                                           ) -> list[Weather]:
        return await get_weather_records_by_open_meteo_api(coordinates)
