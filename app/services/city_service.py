from sqlalchemy.orm import Session
from models.city import CityModel
from schemas.city import CitySchema
from schemas.coordinates import CoordinatesSchema
from schemas.weather import WeatherSchema
from services.weather_service import get_weather_by_coordinates


class CityService:
    def __init__(self, city_data: CitySchema, db: Session):
        self.city_data = city_data
        self.db = db

    def check_city_existence(self) -> bool:
        same_name_cities = self.db.query(CityModel).filter(
            CityModel.name == self.city_data.name)
        return same_name_cities.first() is not None

    def add_weather_to_city(self) -> None:
        weather: WeatherSchema = get_weather_by_coordinates(
            CoordinatesSchema(
                latitude=self.city_data.latitude,
                longitude=self.city_data.longitude
            )
        )
        self.city.weather = weather.model_dump_json()

    def add_city(self) -> CityModel:
        self.city = CityModel(
            name=self.city_data.name,
            latitude=self.city_data.latitude,
            longitude=self.city_data.longitude
        )
        self.add_weather_to_city()

        self.db.add(self.city)
        self.db.commit()
        self.db.refresh(self.city)
        return self.city

    def get_cities(self) -> list[dict]:
        cities = self.db.query(CityModel).all()
        # В ТЗ просят выводить только список городов
        # но я добавил всю информацию, включая погоду
        for city in cities:
            city.weather = city.parsed_weather
        return [
            {
                "id": city.id,
                "name": city.name,
                "latitude": city.latitude,
                "longitude": city.longitude,
                "weather": city.weather
            } for city in cities
        ]
