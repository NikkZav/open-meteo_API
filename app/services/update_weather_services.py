import time
import asyncio
from models import CityModel
from services.city_service import get_cities
from core.db import Session
from services.weather_service import get_weather_by_coordinates
from schemas.weather import WeatherSchema


def add_weather_to_city(city: CityModel, ):



def update_weather(db: Session):
    cities = get_cities(db)
    for city in cities:
        weather: WeatherSchema = get_weather_by_coordinates(city.latitude, city.longitude)
        city.weather = weather
        db.commit()


async def strat_update_weather():
    while True:
        update_weather()
        await asyncio.sleep(15*60)
