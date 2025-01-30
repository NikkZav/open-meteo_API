from sqlalchemy.orm import Session, joinedload
from models import CityModel, WeatherModel
from schemas.city import CitySchema
from schemas.coordinates import CoordinatesSchema
from schemas.weather import WeatherSchema
from services.weather_service import get_weather_in_city
from datetime import datetime


def get_city_or_none(recognizer: str | int, db: Session) -> CityModel | None:
    condition = (CityModel.name == recognizer) \
        if isinstance(recognizer, str) else (CityModel.id == recognizer)
    return db.query(CityModel).filter(condition).first()


class CityService:
    def __init__(self, db: Session, city: CitySchema | CityModel = None):
        self.db = db
        if isinstance(city, CityModel):
            self.city = city
        elif isinstance(city, CitySchema):
            self.city_data = city

    def check_city_existence(self) -> bool:
        return get_city_or_none(self.city_data.name, self.db) is not None

    def add_weather_to_city(self) -> None:
        weather: WeatherSchema = get_weather_in_city(self.city)
        new_weather = WeatherModel(
            city_id=self.city.id,
            time=datetime.now(),
            **weather.model_dump()
        )
        self.db.add(new_weather)
        self.db.commit()

    def add_city(self) -> CityModel:
        self.city = CityModel(
            name=self.city_data.name,
            latitude=self.city_data.latitude,
            longitude=self.city_data.longitude
        )
        self.db.add(self.city)
        self.db.commit()
        self.db.refresh(self.city)

        self.add_weather_to_city()

        return self.city

    def get_cities(self, all_statistic_with_weather: bool = False
                   ) -> list[str | dict]:
        if all_statistic_with_weather:
            # В ТЗ просят выводить только список городов
            # но я добавил возможность получить всю информацию, включая погоду
            cities = self.db.query(CityModel).options(
                joinedload(CityModel.weather_records)
            ).all()
            return cities
        else:
            return [city.name for city in
                    self.db.query(CityModel).all()]
